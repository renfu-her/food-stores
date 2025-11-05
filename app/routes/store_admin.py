"""
商店管理者路由
"""
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app.models import Shop, Product, Order, Category, Topping
from app.utils.decorators import login_required, role_required, get_current_user
from app import db

store_admin_bp = Blueprint('store_admin', __name__)

@store_admin_bp.route('/')
@role_required('store_admin')
def index():
    """Store Admin首頁 - 重定向到儀表板"""
    return redirect(url_for('store_admin.dashboard'))

@store_admin_bp.route('/login')
def login():
    """商店管理者登入頁面"""
    if 'user_id' in session:
        user = get_current_user()
        if user and user.role == 'store_admin':
            return redirect(url_for('store_admin.dashboard'))
    return render_template('shop/login.html')

@store_admin_bp.route('/dashboard')
@role_required('store_admin')
def dashboard():
    """商店管理者儀表板"""
    user = get_current_user()
    
    # 獲取用戶的店鋪（排除已刪除）
    shop = Shop.query.filter_by(owner_id=user.id).filter(Shop.deleted_at.is_(None)).first()
    if not shop:
        return render_template('shop/no_shop.html')
    
    # 統計資料（排除已刪除的產品）
    total_products = Product.query.filter_by(shop_id=shop.id).filter(Product.deleted_at.is_(None)).count()
    active_products = Product.query.filter_by(shop_id=shop.id, is_active=True).filter(Product.deleted_at.is_(None)).count()
    total_orders = Order.query.filter_by(shop_id=shop.id).count()
    pending_orders = Order.query.filter_by(shop_id=shop.id, status='pending').count()
    process_orders = Order.query.filter_by(shop_id=shop.id, status='process').count()
    success_orders = Order.query.filter_by(shop_id=shop.id, status='success').count()
    
    # 最近訂單
    recent_orders = Order.query.filter_by(shop_id=shop.id).order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('shop/dashboard.html',
                         shop=shop,
                         user=user,
                         total_products=total_products,
                         active_products=active_products,
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         process_orders=process_orders,
                         success_orders=success_orders,
                         recent_orders=recent_orders)

@store_admin_bp.route('/shops')
@role_required('store_admin')
def shops():
    """店鋪列表頁面"""
    user = get_current_user()
    # 只查詢當前用戶擁有且未軟刪除的店鋪
    shops_list = Shop.query.filter_by(owner_id=user.id).filter(Shop.deleted_at.is_(None)).order_by(Shop.created_at.desc()).all()
    return render_template('shop/shops.html', shops=shops_list, user=user)

@store_admin_bp.route('/profile')
@role_required('store_admin')
def profile():
    """店鋪資訊管理頁面"""
    user = get_current_user()
    shop = Shop.query.filter_by(owner_id=user.id).filter(Shop.deleted_at.is_(None)).first_or_404()
    return render_template('shop/profile.html', shop=shop, user=user)

@store_admin_bp.route('/products')
@role_required('store_admin')
def products():
    """產品管理頁面"""
    user = get_current_user()
    shop = Shop.query.filter_by(owner_id=user.id).filter(Shop.deleted_at.is_(None)).first_or_404()
    # 只顯示未軟刪除的產品
    products_list = Product.query.filter_by(shop_id=shop.id).filter(Product.deleted_at.is_(None)).order_by(Product.created_at.desc()).all()
    categories = Category.query.all()
    return render_template('shop/products.html', 
                         products=products_list,
                         shop=shop,
                         categories=categories)

@store_admin_bp.route('/toppings')
@role_required('store_admin')
def toppings():
    """Toppings管理頁面"""
    user = get_current_user()
    shop = Shop.query.filter_by(owner_id=user.id).filter(Shop.deleted_at.is_(None)).first_or_404()
    toppings_list = Topping.query.filter_by(shop_id=shop.id).order_by(Topping.created_at.desc()).all()
    return render_template('shop/toppings.html', toppings=toppings_list, shop=shop)

@store_admin_bp.route('/orders')
@role_required('store_admin')
def orders():
    """訂單管理頁面"""
    user = get_current_user()
    shop = Shop.query.filter_by(owner_id=user.id).filter(Shop.deleted_at.is_(None)).first_or_404()
    orders_list = Order.query.filter_by(shop_id=shop.id).order_by(Order.created_at.desc()).all()
    return render_template('shop/orders.html', orders=orders_list, shop=shop)

@store_admin_bp.route('/statistics')
@role_required('store_admin')
def statistics():
    """商店統計頁面"""
    user = get_current_user()
    shop = Shop.query.filter_by(owner_id=user.id).filter(Shop.deleted_at.is_(None)).first_or_404()
    
    # 統計資料（排除已刪除的產品）
    total_products = Product.query.filter_by(shop_id=shop.id).filter(Product.deleted_at.is_(None)).count()
    active_products = Product.query.filter_by(shop_id=shop.id, is_active=True).filter(Product.deleted_at.is_(None)).count()
    inactive_products = total_products - active_products
    
    total_orders = Order.query.filter_by(shop_id=shop.id).count()
    pending_orders = Order.query.filter_by(shop_id=shop.id, status='pending').count()
    process_orders = Order.query.filter_by(shop_id=shop.id, status='process').count()
    success_orders = Order.query.filter_by(shop_id=shop.id, status='success').count()
    
    # 計算總收入（成功訂單的總價）
    success_order_list = Order.query.filter_by(shop_id=shop.id, status='success').all()
    total_revenue = sum(float(order.total_price) for order in success_order_list)
    
    # 各狀態訂單百分比
    order_percentage = {
        'pending': (pending_orders / total_orders * 100) if total_orders > 0 else 0,
        'process': (process_orders / total_orders * 100) if total_orders > 0 else 0,
        'success': (success_orders / total_orders * 100) if total_orders > 0 else 0
    }
    
    return render_template('shop/statistics.html',
                         shop=shop,
                         total_products=total_products,
                         active_products=active_products,
                         inactive_products=inactive_products,
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         process_orders=process_orders,
                         success_orders=success_orders,
                         total_revenue=total_revenue,
                         order_percentage=order_percentage)

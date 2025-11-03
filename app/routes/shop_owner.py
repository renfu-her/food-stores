"""
商店管理者路由
"""
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app.models import Shop, Product, Order, Category, Topping
from app.utils.decorators import login_required, shop_owner_required, get_current_user
from app import db

shop_owner_bp = Blueprint('shop_owner', __name__)

@shop_owner_bp.route('/')
@shop_owner_required
def index():
    """Shop Owner首頁 - 重定向到儀表板"""
    return redirect(url_for('shop_owner.dashboard'))

@shop_owner_bp.route('/login')
def login():
    """商店管理者登入頁面"""
    if 'user_id' in session:
        user = get_current_user()
        if user and user.role == 'shop_owner':
            return redirect(url_for('shop_owner.dashboard'))
    return render_template('shop/login.html')

@shop_owner_bp.route('/dashboard')
@shop_owner_required
def dashboard():
    """商店管理者儀表板"""
    user = get_current_user()
    
    # 獲取用戶的店鋪
    shop = Shop.query.filter_by(owner_id=user.id).first()
    if not shop:
        return render_template('shop/no_shop.html')
    
    # 統計資料
    total_products = Product.query.filter_by(shop_id=shop.id).count()
    active_products = Product.query.filter_by(shop_id=shop.id, is_active=True).count()
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

@shop_owner_bp.route('/profile')
@shop_owner_required
def profile():
    """店鋪資訊管理頁面"""
    user = get_current_user()
    shop = Shop.query.filter_by(owner_id=user.id).first_or_404()
    return render_template('shop/profile.html', shop=shop, user=user)

@shop_owner_bp.route('/products')
@shop_owner_required
def products():
    """產品管理頁面"""
    user = get_current_user()
    shop = Shop.query.filter_by(owner_id=user.id).first_or_404()
    products_list = Product.query.filter_by(shop_id=shop.id).order_by(Product.created_at.desc()).all()
    categories = Category.query.all()
    return render_template('shop/products.html', 
                         products=products_list,
                         shop=shop,
                         categories=categories)

@shop_owner_bp.route('/toppings')
@shop_owner_required
def toppings():
    """Toppings管理頁面"""
    user = get_current_user()
    shop = Shop.query.filter_by(owner_id=user.id).first_or_404()
    toppings_list = Topping.query.filter_by(shop_id=shop.id).order_by(Topping.created_at.desc()).all()
    return render_template('shop/toppings.html', toppings=toppings_list, shop=shop)

@shop_owner_bp.route('/orders')
@shop_owner_required
def orders():
    """訂單管理頁面"""
    user = get_current_user()
    shop = Shop.query.filter_by(owner_id=user.id).first_or_404()
    orders_list = Order.query.filter_by(shop_id=shop.id).order_by(Order.created_at.desc()).all()
    return render_template('shop/orders.html', orders=orders_list, shop=shop)

@shop_owner_bp.route('/statistics')
@shop_owner_required
def statistics():
    """商店統計頁面"""
    user = get_current_user()
    shop = Shop.query.filter_by(owner_id=user.id).first_or_404()
    
    # 統計資料
    total_products = Product.query.filter_by(shop_id=shop.id).count()
    active_products = Product.query.filter_by(shop_id=shop.id, is_active=True).count()
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

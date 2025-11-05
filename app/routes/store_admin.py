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
    
    # 獲取用戶的所有店鋪（排除已刪除）
    shops = Shop.query.filter_by(owner_id=user.id).filter(Shop.deleted_at.is_(None)).all()
    if not shops:
        return render_template('shop/no_shop.html')
    
    # 統計資料（所有店鋪加總，排除已刪除的產品）
    shop_ids = [s.id for s in shops]
    total_products = Product.query.filter(Product.shop_id.in_(shop_ids)).filter(Product.deleted_at.is_(None)).count()
    active_products = Product.query.filter(Product.shop_id.in_(shop_ids), Product.is_active==True).filter(Product.deleted_at.is_(None)).count()
    total_orders = Order.query.filter(Order.shop_id.in_(shop_ids)).count()
    pending_orders = Order.query.filter(Order.shop_id.in_(shop_ids), Order.status=='pending').count()
    process_orders = Order.query.filter(Order.shop_id.in_(shop_ids), Order.status=='process').count()
    success_orders = Order.query.filter(Order.shop_id.in_(shop_ids), Order.status=='success').count()
    
    # 最近訂單（所有店鋪）
    recent_orders = Order.query.filter(Order.shop_id.in_(shop_ids)).order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('shop/dashboard.html',
                         shops=shops,
                         total_shops=len(shops),
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
    
    # 序列化為字典（供 JavaScript 使用）
    shops_data = []
    for s in shops_list:
        shops_data.append({
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'shop_order_id': s.shop_order_id,
            'owner_id': s.owner_id,
            'max_toppings_per_order': s.max_toppings_per_order,
            'status': s.status,
            'created_at': s.created_at.isoformat() if s.created_at else None
        })
    
    return render_template('shop/shops/list.html', shops=shops_data, user=user)

@store_admin_bp.route('/shops/add')
@role_required('store_admin')
def shop_add():
    """新增店鋪頁面"""
    user = get_current_user()
    return render_template('shop/shops/add.html', user=user)

@store_admin_bp.route('/shops/<int:shop_id>/edit')
@role_required('store_admin')
def shop_edit(shop_id):
    """編輯店鋪頁面"""
    user = get_current_user()
    shop = Shop.query.filter_by(id=shop_id, owner_id=user.id).filter(Shop.deleted_at.is_(None)).first_or_404()
    return render_template('shop/shops/edit.html', shop=shop, user=user)

@store_admin_bp.route('/products')
@role_required('store_admin')
def products():
    """產品管理頁面"""
    user = get_current_user()
    # 獲取用戶擁有的所有店鋪
    shops_list = Shop.query.filter_by(owner_id=user.id).filter(Shop.deleted_at.is_(None)).all()
    
    if not shops_list:
        return render_template('shop/no_shop.html')
    
    # 獲取所有自己店鋪的產品
    shop_ids = [s.id for s in shops_list]
    products_list = Product.query.filter(Product.shop_id.in_(shop_ids)).filter(Product.deleted_at.is_(None)).order_by(Product.created_at.desc()).all()
    categories_list = Category.query.all()
    
    # 序列化為字典（供 JavaScript 使用）
    products_data = []
    for p in products_list:
        products_data.append({
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'shop_id': p.shop_id,
            'category_id': p.category_id,
            'unit_price': float(p.unit_price),
            'discounted_price': float(p.discounted_price) if p.discounted_price else None,
            'stock': p.stock_quantity,
            'is_active': p.is_active,
            'has_cold_drink': p.has_cold_drink,
            'has_hot_drink': p.has_hot_drink,
            'created_at': p.created_at.isoformat() if p.created_at else None
        })
    
    shops_data = [{'id': s.id, 'name': s.name} for s in shops_list]
    categories_data = [{'id': c.id, 'name': c.name} for c in categories_list]
    
    return render_template('shop/products/list.html', 
                         products=products_data,
                         shops=shops_data,
                         categories=categories_data)

@store_admin_bp.route('/products/add')
@role_required('store_admin')
def product_add():
    """新增產品頁面"""
    user = get_current_user()
    shops = Shop.query.filter_by(owner_id=user.id).filter(Shop.deleted_at.is_(None)).all()
    if not shops:
        return render_template('shop/no_shop.html')
    categories = Category.query.all()
    return render_template('shop/products/add.html', shops=shops, categories=categories, user=user)

@store_admin_bp.route('/products/<int:product_id>/edit')
@role_required('store_admin')
def product_edit(product_id):
    """編輯產品頁面"""
    user = get_current_user()
    # 獲取所有自己的店鋪
    shops = Shop.query.filter_by(owner_id=user.id).filter(Shop.deleted_at.is_(None)).all()
    if not shops:
        return render_template('shop/no_shop.html')
    
    # 檢查產品是否屬於自己的店鋪
    shop_ids = [s.id for s in shops]
    product = Product.query.filter(Product.id == product_id, Product.shop_id.in_(shop_ids)).filter(Product.deleted_at.is_(None)).first_or_404()
    categories = Category.query.all()
    return render_template('shop/products/edit.html', product=product, shops=shops, categories=categories, user=user)

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

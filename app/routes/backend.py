"""
Backend後台路由
"""
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app.models import User, Shop, Product, Order, UpdateLog
from app.utils.decorators import login_required, role_required, get_current_user
from app import db

backend_bp = Blueprint('backend', __name__)

@backend_bp.route('/')
@role_required('admin')
def index():
    """Backend首頁/儀表板"""
    user = get_current_user()
    
    # 統計資料
    total_users = User.query.count()
    total_shops = Shop.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    
    return render_template('backend/dashboard.html', 
                         user=user,
                         total_users=total_users,
                         total_shops=total_shops,
                         total_products=total_products,
                         total_orders=total_orders,
                         pending_orders=pending_orders)

@backend_bp.route('/login')
def login():
    """Backend登入頁面"""
    if 'user_id' in session:
        user = get_current_user()
        if user and user.role == 'admin':
            return redirect(url_for('backend.index'))
    return render_template('backend/login.html')

@backend_bp.route('/users')
@role_required('admin')
def users():
    """使用者管理頁面"""
    users_list = User.query.order_by(User.created_at.desc()).all()
    # 将用户转换为字典格式以便 JavaScript 处理
    users_data = []
    for u in users_list:
        users_data.append({
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'role': u.role,
            'is_active': u.is_active,
            'created_at': u.created_at.isoformat() if u.created_at else None
        })
    # 使用工作版本的模板
    return render_template('backend/users_working.html', users=users_data)

@backend_bp.route('/shops')
@role_required('admin')
def shops():
    """店鋪管理頁面"""
    shops_list = Shop.query.order_by(Shop.created_at.desc()).all()
    users_list = User.query.filter_by(role='store_admin').all()
    
    shops_data = []
    for s in shops_list:
        shops_data.append({
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'owner_id': s.owner_id,
            'max_toppings_per_order': s.max_toppings_per_order,
            'status': s.status,
            'created_at': s.created_at.isoformat() if s.created_at else None
        })
    
    users_data = []
    for u in users_list:
        users_data.append({
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'role': u.role
        })
    
    return render_template('backend/shops.html', shops=shops_data, users=users_data)

@backend_bp.route('/products')
@role_required('admin')
def products():
    """產品管理頁面"""
    from app.models import Category
    products_list = Product.query.order_by(Product.created_at.desc()).all()
    shops_list = Shop.query.all()
    categories_list = Category.query.all()
    
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
            'stock': p.stock,
            'is_active': p.is_active,
            'created_at': p.created_at.isoformat() if p.created_at else None
        })
    
    shops_data = [{'id': s.id, 'name': s.name} for s in shops_list]
    categories_data = [{'id': c.id, 'name': c.name} for c in categories_list]
    
    return render_template('backend/products.html', 
                         products=products_data,
                         shops=shops_data,
                         categories=categories_data)

@backend_bp.route('/orders')
@role_required('admin')
def orders():
    """訂單管理頁面"""
    orders_list = Order.query.order_by(Order.created_at.desc()).all()
    shops_list = Shop.query.all()
    users_list = User.query.all()
    
    orders_data = []
    for o in orders_list:
        orders_data.append({
            'id': o.id,
            'user_id': o.user_id,
            'shop_id': o.shop_id,
            'total_price': float(o.total_price),
            'status': o.status,
            'created_at': o.created_at.isoformat() if o.created_at else None
        })
    
    shops_data = [{'id': s.id, 'name': s.name} for s in shops_list]
    users_data = [{'id': u.id, 'name': u.name, 'email': u.email} for u in users_list]
    
    return render_template('backend/orders.html', 
                         orders=orders_data,
                         shops=shops_data,
                         users=users_data)

@backend_bp.route('/shop/<int:shop_id>')
@role_required('admin')
def shop_detail(shop_id):
    """店鋪詳情頁面"""
    shop = Shop.query.get_or_404(shop_id)
    products = Product.query.filter_by(shop_id=shop_id).all()
    toppings = shop.toppings
    return render_template('backend/shop_detail.html', 
                         shop=shop, 
                         products=products,
                         toppings=toppings)

@backend_bp.route('/product/<int:product_id>')
@role_required('admin')
def product_detail(product_id):
    """產品詳情頁面"""
    product = Product.query.get_or_404(product_id)
    return render_template('backend/product_detail.html', product=product)

@backend_bp.route('/order/<int:order_id>')
@role_required('admin')
def order_detail(order_id):
    """訂單詳情頁面"""
    order = Order.query.get_or_404(order_id)
    return render_template('backend/order_detail.html', order=order)

@backend_bp.route('/users-test')
@role_required('admin')
def users_test():
    """使用者管理測試頁面"""
    users_list = User.query.order_by(User.created_at.desc()).all()
    users_data = []
    for u in users_list:
        users_data.append({
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'role': u.role,
            'is_active': u.is_active,
            'created_at': u.created_at.isoformat() if u.created_at else None
        })
    return render_template('backend/users_simple.html', users=users_data)

@backend_bp.route('/users-v2')
@role_required('admin')
def users_v2():
    """使用者管理 v2（簡化測試）"""
    users_list = User.query.order_by(User.created_at.desc()).all()
    users_data = []
    for u in users_list:
        users_data.append({
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'role': u.role,
            'is_active': u.is_active,
            'created_at': u.created_at.isoformat() if u.created_at else None
        })
    return render_template('backend/users_v2.html', users=users_data)

@backend_bp.route('/update-logs')
@role_required('admin')
def update_logs():
    """系統更新日誌頁面"""
    logs_list = UpdateLog.query.order_by(UpdateLog.created_at.desc()).limit(1000).all()
    users_list = User.query.all()
    
    logs_data = []
    for log in logs_list:
        logs_data.append({
            'id': log.id,
            'user_id': log.user_id,
            'action': log.action,
            'table_name': log.table_name,
            'record_id': log.record_id,
            'old_data': log.old_data,
            'new_data': log.new_data,
            'description': log.description,
            'ip_address': log.ip_address,
            'created_at': log.created_at.isoformat() if log.created_at else None
        })
    
    users_data = [{'id': u.id, 'name': u.name} for u in users_list]
    
    return render_template('backend/update_logs.html', logs=logs_data, users=users_data)

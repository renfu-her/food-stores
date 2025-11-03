"""
Backend後台路由
"""
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app.models import User, Shop, Product, Order
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
    return render_template('backend/users.html', users=users_list)

@backend_bp.route('/shops')
@role_required('admin')
def shops():
    """店鋪管理頁面"""
    shops_list = Shop.query.order_by(Shop.created_at.desc()).all()
    return render_template('backend/shops.html', shops=shops_list)

@backend_bp.route('/products')
@role_required('admin')
def products():
    """產品管理頁面"""
    products_list = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('backend/products.html', products=products_list)

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

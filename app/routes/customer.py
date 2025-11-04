"""
商城使用者路由
"""
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app.models import Shop, Product, Order, Category
from app.utils.decorators import login_required, get_current_user
from app import db

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/')
def index():
    """商城首頁"""
    shops = Shop.query.filter_by(status='active').all()
    return render_template('store/index.html', shops=shops)

@customer_bp.route('/login')
def login():
    """使用者登入/註冊頁面"""
    if 'user_id' in session:
        return redirect(url_for('customer.index'))
    return render_template('store/login.html', active_tab='login')

@customer_bp.route('/register')
def register():
    """使用者註冊頁面（顯示註冊選項卡）"""
    if 'user_id' in session:
        return redirect(url_for('customer.index'))
    return render_template('store/login.html', active_tab='register')

@customer_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    """訂單詳情頁面"""
    user = get_current_user()
    order = Order.query.get_or_404(order_id)
    
    # 權限檢查
    if order.user_id != user.id:
        return redirect(url_for('customer.orders'))
    
    return render_template('store/order_detail.html', order=order)

@customer_bp.route('/shop/<int:shop_id>')
def shop(shop_id):
    """店鋪詳情頁"""
    shop = Shop.query.get_or_404(shop_id)
    products = Product.query.filter_by(shop_id=shop_id, is_active=True).all()
    categories = Category.query.all()
    
    return render_template('store/shop.html', 
                         shop=shop, 
                         products=products,
                         categories=categories)

@customer_bp.route('/product/<int:product_id>')
def product(product_id):
    """產品詳情頁"""
    product = Product.query.get_or_404(product_id)
    if not product.is_active:
        return redirect(url_for('customer.index'))
    
    # 獲取店鋪的toppings
    toppings = [t for t in product.shop.toppings if t.is_active]
    
    return render_template('store/product.html', 
                         product=product,
                         toppings=toppings)

@customer_bp.route('/cart')
@login_required
def cart():
    """購物車頁面"""
    user = get_current_user()
    return render_template('store/cart.html', user=user)

@customer_bp.route('/checkout')
@login_required
def checkout():
    """結帳頁面"""
    user = get_current_user()
    return render_template('store/checkout.html', user=user)

@customer_bp.route('/orders')
@login_required
def orders():
    """我的訂單頁面"""
    user = get_current_user()
    orders_list = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return render_template('store/orders.html', orders=orders_list)

@customer_bp.route('/profile')
@login_required
def profile():
    """個人資料頁面"""
    user = get_current_user()
    return render_template('store/profile.html', user=user)

"""
商城使用者路由
"""
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app.models import Shop, Product, Order, Category, About, News, Table, PointTransaction
from app.utils.decorators import login_required, get_current_user
from app import db

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/')
def index():
    """商城首頁（排除已刪除的店鋪）"""
    from app.models import HomeBanner
    shops = Shop.query.filter_by(status='active').filter(Shop.deleted_at.is_(None)).all()
    banners = HomeBanner.query.filter_by(is_active=True).order_by(HomeBanner.display_order).all()
    return render_template('store/index.html', shops=shops, banners=banners)

@customer_bp.route('/about')
def about():
    """關於我們頁面"""
    about_list = About.query.filter_by(is_active=True).order_by(About.display_order).all()
    return render_template('store/about.html', about_list=about_list)

@customer_bp.route('/news')
def news():
    """最新消息列表頁面"""
    news_list = News.query.filter_by(is_active=True).order_by(News.publish_date.desc()).all()
    return render_template('store/news.html', news_list=news_list)

@customer_bp.route('/news/<int:news_id>')
def news_detail(news_id):
    """最新消息詳情頁面"""
    news = News.query.get_or_404(news_id)
    if not news.is_active:
        return redirect(url_for('customer.news'))
    return render_template('store/news_detail.html', news=news)

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
    """店鋪詳情頁（排除已刪除）"""
    shop = Shop.query.filter_by(id=shop_id).filter(Shop.deleted_at.is_(None)).first_or_404()
    # 只顯示啟用且未軟刪除的產品
    products = Product.query.filter_by(shop_id=shop_id, is_active=True).filter(Product.deleted_at.is_(None)).all()
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

@customer_bp.route('/store/<int:shop_id>/table/<table_number>')
def guest_order(shop_id, table_number):
    """访客点餐页面（扫描桌号QRCode进入）"""
    # 获取店铺
    shop = Shop.query.filter_by(id=shop_id).filter(Shop.deleted_at.is_(None)).first_or_404()
    
    # 检查店铺是否启用桌号点餐
    if not shop.qrcode_enabled:
        return render_template('store/error.html', 
                             message='此店铺未启用桌号扫码点餐',
                             shop=shop)
    
    # 获取桌号
    table = Table.query.filter_by(shop_id=shop_id, table_number=table_number).first()
    if not table:
        return render_template('store/error.html',
                             message='桌号不存在',
                             shop=shop)
    
    # 获取产品
    products = Product.query.filter_by(shop_id=shop_id, is_active=True).filter(Product.deleted_at.is_(None)).all()
    categories = Category.query.all()
    
    return render_template('store/guest_order.html', 
                         shop=shop,
                         table=table,
                         table_number=table_number,
                         products=products,
                         categories=categories)

@customer_bp.route('/points')
@login_required
def points():
    """回馈金页面"""
    user = get_current_user()
    
    # 获取最近的交易记录（前20条）
    transactions = PointTransaction.query.filter_by(user_id=user.id)\
                                       .order_by(PointTransaction.created_at.desc())\
                                       .limit(20).all()
    
    return render_template('store/points.html', user=user, transactions=transactions)

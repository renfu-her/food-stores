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
    return render_template('backend/users/list.html', users=users_data)

@backend_bp.route('/users/add')
@role_required('admin')
def user_add():
    """新增使用者頁面"""
    return render_template('backend/users/add.html')

@backend_bp.route('/users/<int:user_id>/edit')
@role_required('admin')
def user_edit(user_id):
    """編輯使用者頁面"""
    user = User.query.get_or_404(user_id)
    return render_template('backend/users/edit.html', user=user)

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
            'shop_order_id': s.shop_order_id,
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
    
    return render_template('backend/shops/list.html', shops=shops_data, users=users_data)

@backend_bp.route('/shops/add')
@role_required('admin')
def shop_add():
    """新增店鋪頁面"""
    users_list = User.query.filter_by(role='store_admin', is_active=True).all()
    return render_template('backend/shops/add.html', users=users_list)

@backend_bp.route('/shops/<int:shop_id>/edit')
@role_required('admin')
def shop_edit(shop_id):
    """編輯店鋪頁面"""
    shop = Shop.query.get_or_404(shop_id)
    users_list = User.query.filter_by(role='store_admin', is_active=True).all()
    return render_template('backend/shops/edit.html', shop=shop, users=users_list)

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
            'stock': p.stock_quantity,
            'is_active': p.is_active,
            'created_at': p.created_at.isoformat() if p.created_at else None
        })
    
    shops_data = [{'id': s.id, 'name': s.name} for s in shops_list]
    categories_data = [{'id': c.id, 'name': c.name} for c in categories_list]
    
    return render_template('backend/products/list.html', 
                         products=products_data,
                         shops=shops_data,
                         categories=categories_data)

@backend_bp.route('/products/add')
@role_required('admin')
def product_add():
    """新增產品頁面"""
    from app.models import Category
    shops_list = Shop.query.filter_by(status='active').all()
    categories_list = Category.query.all()
    return render_template('backend/products/add.html', shops=shops_list, categories=categories_list)

@backend_bp.route('/products/<int:product_id>/edit')
@role_required('admin')
def product_edit(product_id):
    """編輯產品頁面"""
    from app.models import Category
    product = Product.query.get_or_404(product_id)
    shops_list = Shop.query.all()
    categories_list = Category.query.all()
    return render_template('backend/products/edit.html', product=product, shops=shops_list, categories=categories_list)

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
    
    return render_template('backend/orders/list.html', 
                         orders=orders_data,
                         shops=shops_data,
                         users=users_data)

@backend_bp.route('/orders/<int:order_id>/edit')
@role_required('admin')
def order_edit(order_id):
    """編輯訂單頁面（主要用於更新狀態）"""
    order = Order.query.get_or_404(order_id)
    return render_template('backend/orders/edit.html', order=order)

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

@backend_bp.route('/categories')
@role_required('admin')
def categories():
    """分類管理頁面"""
    from app.models import Category
    categories_list = Category.query.order_by(Category.name).all()
    
    categories_data = []
    for c in categories_list:
        product_count = Product.query.filter_by(category_id=c.id).count()
        categories_data.append({
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'product_count': product_count,
            'created_at': c.created_at.isoformat() if c.created_at else None
        })
    
    return render_template('backend/categories.html', categories=categories_data)

@backend_bp.route('/home-banners')
@role_required('admin')
def home_banners():
    """首頁 Banner 管理頁面"""
    from app.models import HomeBanner
    banners_list = HomeBanner.query.order_by(HomeBanner.display_order).all()
    
    banners_data = []
    for b in banners_list:
        banners_data.append({
            'id': b.id,
            'name': b.name,
            'image_path': b.image_path,
            'title': b.title,
            'subtitle': b.subtitle,
            'link': b.link,
            'is_active': b.is_active,
            'display_order': b.display_order,
            'created_at': b.created_at.isoformat() if b.created_at else None
        })
    
    return render_template('backend/home_banners/list.html', banners=banners_data)

@backend_bp.route('/home-banners/add')
@role_required('admin')
def home_banner_add():
    """新增首頁 Banner 頁面"""
    return render_template('backend/home_banners/add.html')

@backend_bp.route('/home-banners/<int:banner_id>/edit')
@role_required('admin')
def home_banner_edit(banner_id):
    """編輯首頁 Banner 頁面"""
    from app.models import HomeBanner
    banner = HomeBanner.query.get_or_404(banner_id)
    return render_template('backend/home_banners/edit.html', banner=banner)

@backend_bp.route('/about')
@role_required('admin')
def about():
    """關於我們管理頁面（列表）"""
    from app.models import About
    about_list = About.query.order_by(About.display_order).all()
    
    about_data = []
    for a in about_list:
        about_data.append({
            'id': a.id,
            'title': a.title,
            'content': a.content,
            'is_active': a.is_active,
            'display_order': a.display_order,
            'created_at': a.created_at.isoformat() if a.created_at else None
        })
    
    return render_template('backend/about/list.html', about_list=about_data)

@backend_bp.route('/about/add')
@role_required('admin')
def about_add():
    """新增關於我們頁面"""
    return render_template('backend/about/add.html')

@backend_bp.route('/about/<int:about_id>/edit')
@role_required('admin')
def about_edit(about_id):
    """編輯關於我們頁面"""
    from app.models import About
    about_record = About.query.get_or_404(about_id)
    return render_template('backend/about/edit.html', about=about_record)

@backend_bp.route('/news')
@role_required('admin')
def news():
    """最新消息管理頁面"""
    from app.models import News
    news_list = News.query.order_by(News.publish_date.desc()).all()
    
    news_data = []
    for n in news_list:
        news_data.append({
            'id': n.id,
            'name': n.name,
            'description': n.description,
            'image_path': n.image_path,
            'is_active': n.is_active,
            'publish_date': n.publish_date.isoformat() if n.publish_date else None,
            'created_at': n.created_at.isoformat() if n.created_at else None
        })
    
    return render_template('backend/news/list.html', news=news_data)

@backend_bp.route('/news/add')
@role_required('admin')
def news_add():
    """新增最新消息頁面"""
    return render_template('backend/news/add.html')

@backend_bp.route('/news/<int:news_id>/edit')
@role_required('admin')
def news_edit(news_id):
    """編輯最新消息頁面"""
    from app.models import News
    news = News.query.get_or_404(news_id)
    return render_template('backend/news/edit.html', news=news)

@backend_bp.route('/settings')
@role_required('admin')
def settings():
    """系統設定頁面"""
    return render_template('backend/settings.html')

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

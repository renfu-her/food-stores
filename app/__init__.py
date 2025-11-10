from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from app.config import Config

# 初始化擴展
db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO(
    cors_allowed_origins="*",
    logger=False,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25
)

def create_app(config_class=Config):
    """應用工廠函數"""
    import os
    # 獲取專案根目錄（app/__init__.py 位於 app/ 目錄，需要向上兩層到專案根目錄）
    # __file__ = /path/to/app/__init__.py
    # dirname(__file__) = /path/to/app
    # dirname(dirname(__file__)) = /path/to (專案根目錄)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 模板目錄：public/templates
    template_dir = os.path.join(BASE_DIR, 'public', 'templates')
    
    # 靜態文件目錄：優先使用根目錄的 static，否則使用 public/static
    static_dir = os.path.join(BASE_DIR, 'static') if os.path.exists(os.path.join(BASE_DIR, 'static')) else os.path.join(BASE_DIR, 'public', 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    app.config.from_object(config_class)
    
    # 初始化擴展
    # Flask-SQLAlchemy 会自动读取 SQLALCHEMY_ENGINE_OPTIONS 配置
    # 无需手动创建 engine，Flask-SQLAlchemy 会在首次访问时自动创建
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, async_mode=app.config['SOCKETIO_ASYNC_MODE'])
    
    # 註冊藍圖（延遲導入避免循環依賴）
    with app.app_context():
        from app.routes.auth import auth_bp
        from app.routes.backend import backend_bp
        from app.routes.store_admin import store_admin_bp
        from app.routes.customer import customer_bp
        from app.routes.guest import guest_bp
        from app.routes.api.shops import shops_api_bp
        from app.routes.api.products import products_api_bp
        from app.routes.api.orders import orders_api_bp
        from app.routes.api.toppings import toppings_api_bp
        from app.routes.api.users import users_api_bp
        from app.routes.api.shop_images import shop_images_api_bp
        from app.routes.api.product_images import product_images_api_bp
        from app.routes.api.shop_banner import shop_banner_api_bp
        from app.routes.api.categories import categories_api_bp
        from app.routes.api.home_banners import home_banners_api_bp
        from app.routes.api.cart import cart_api_bp
        from app.routes.api.about import about_api_bp
        from app.routes.api.news import news_api_bp
        from app.routes.api.system_settings import system_settings_api_bp
        from app.routes.api.points import points_api_bp
        from app.routes.api.tables import tables_api_bp
        from app.routes.api.payment_methods import payment_methods_api_bp
        from app.routes.websocket import websocket_bp
        from app.routes.seo import seo_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(backend_bp, url_prefix='/backend')
        app.register_blueprint(store_admin_bp, url_prefix='/store_admin')
        app.register_blueprint(customer_bp)  # 首頁路由，不需要前綴
        app.register_blueprint(guest_bp, url_prefix='/guest')  # 訪客點餐路由
        app.register_blueprint(seo_bp)  # SEO 路由（sitemap.xml, robots.txt）
        app.register_blueprint(shops_api_bp, url_prefix='/api/shops')
        app.register_blueprint(products_api_bp, url_prefix='/api/products')
        app.register_blueprint(orders_api_bp, url_prefix='/api/orders')
        app.register_blueprint(toppings_api_bp, url_prefix='/api/toppings')
        app.register_blueprint(users_api_bp, url_prefix='/api/users')
        app.register_blueprint(shop_images_api_bp, url_prefix='/api')
        app.register_blueprint(product_images_api_bp, url_prefix='/api')
        app.register_blueprint(shop_banner_api_bp, url_prefix='/api')
        app.register_blueprint(categories_api_bp, url_prefix='/api/categories')
        app.register_blueprint(home_banners_api_bp, url_prefix='/api/home-banners')
        app.register_blueprint(cart_api_bp, url_prefix='/api/cart')
        app.register_blueprint(about_api_bp, url_prefix='/api/about')
        app.register_blueprint(news_api_bp, url_prefix='/api/news')
        app.register_blueprint(system_settings_api_bp, url_prefix='/api/settings')
        app.register_blueprint(points_api_bp, url_prefix='/api')
        app.register_blueprint(tables_api_bp, url_prefix='/api')
        app.register_blueprint(payment_methods_api_bp, url_prefix='/api')
        app.register_blueprint(websocket_bp)
        
        # 靜態文件路由：提供上傳的圖片
        @app.route('/uploads/<path:filename>')
        def uploaded_file(filename):
            from flask import send_from_directory
            import os
            # 優先使用根目錄的 uploads，否則使用 public/uploads（向後兼容）
            uploads_dir = os.path.join(BASE_DIR, 'uploads')
            uploads_dir_public = os.path.join(BASE_DIR, 'public', 'uploads')
            upload_folder = uploads_dir if os.path.exists(uploads_dir) else uploads_dir_public
            return send_from_directory(upload_folder, filename)
        
        # 根路径指向前台首页
        @app.route('/')
        def index():
            from flask import render_template
            from app.models import Shop, HomeBanner
            shops = Shop.query.filter_by(status='active').all()
            banners = HomeBanner.query.filter_by(is_active=True).order_by(HomeBanner.display_order).all()
            return render_template('store/index.html', shops=shops, banners=banners)
    
    # 註冊錯誤處理器
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    # 添加模板上下文：提供靜態文件版本號
    @app.context_processor
    def inject_static_version():
        import time
        return dict(static_version=int(time.time()))
    
    return app


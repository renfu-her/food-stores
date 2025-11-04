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
    app = Flask(__name__, 
                template_folder='../public/templates',
                static_folder='../public/static')
    app.config.from_object(config_class)
    
    # 初始化擴展
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, async_mode=app.config['SOCKETIO_ASYNC_MODE'])
    
    # 註冊藍圖（延遲導入避免循環依賴）
    with app.app_context():
        try:
            from app.routes.auth import auth_bp
            from app.routes.backend import backend_bp
            from app.routes.store_admin import store_admin_bp
            from app.routes.customer import customer_bp
            from app.routes.api.shops import shops_api_bp
            from app.routes.api.products import products_api_bp
            from app.routes.api.orders import orders_api_bp
            from app.routes.api.toppings import toppings_api_bp
            from app.routes.api.users import users_api_bp
            from app.routes.api.shop_images import shop_images_api_bp
            from app.routes.websocket import websocket_bp
            
            app.register_blueprint(auth_bp)
            app.register_blueprint(backend_bp, url_prefix='/backend')
            app.register_blueprint(store_admin_bp, url_prefix='/shop')
            app.register_blueprint(customer_bp, url_prefix='/store')
            app.register_blueprint(shops_api_bp, url_prefix='/api/shops')
            app.register_blueprint(products_api_bp, url_prefix='/api/products')
            app.register_blueprint(orders_api_bp, url_prefix='/api/orders')
            app.register_blueprint(toppings_api_bp, url_prefix='/api/toppings')
            app.register_blueprint(users_api_bp, url_prefix='/api/users')
            app.register_blueprint(shop_images_api_bp, url_prefix='/api')
            app.register_blueprint(websocket_bp)
            
            # 靜態文件路由：提供上傳的圖片
            @app.route('/uploads/<path:filename>')
            def uploaded_file(filename):
                from flask import send_from_directory
                import os
                upload_folder = os.path.join(app.root_path, '..', 'public', 'uploads')
                return send_from_directory(upload_folder, filename)
            
            # 根路径指向前台首页
            @app.route('/')
            def index():
                from flask import render_template
                from app.models import Shop
                shops = Shop.query.filter_by(status='active').all()
                return render_template('store/index.html', shops=shops)
        except ImportError:
            # 如果路由檔案還不存在，暫時跳過
            pass
    
    # 註冊錯誤處理器
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    return app


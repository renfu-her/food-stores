import os
from datetime import timedelta
from dotenv import load_dotenv

# 載入 .env 文件
load_dotenv()

class Config:
    """應用配置類"""
    # 基礎配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    
    # 資料庫配置
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_PORT = os.environ.get('DB_PORT') or '3306'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or ''
    DB_NAME = os.environ.get('DB_NAME') or 'food-stores'
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', 'False').lower() in ('true', '1', 't')
    
    # 数据库连接池配置（性能优化）
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', '10')),  # 连接池大小
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', '3600')),  # 连接回收时间（秒）
        'pool_pre_ping': True,  # 连接前检查连接是否有效
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', '20')),  # 最大溢出连接数
        'echo': os.environ.get('SQLALCHEMY_ECHO', 'False').lower() in ('true', '1', 't')
    }
    
    # Flask-Migrate配置
    MIGRATIONS_DIR = 'migrations'
    
    # Session配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=int(os.environ.get('SESSION_LIFETIME_DAYS', '7')))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # SocketIO配置
    SOCKETIO_ASYNC_MODE = os.environ.get('SOCKETIO_ASYNC_MODE', 'threading')
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.environ.get('SOCKETIO_CORS_ALLOWED_ORIGINS', '*')
    
    # SEO 配置
    BASE_URL = os.environ.get('BASE_URL') or 'https://yourdomain.com'  # 网站基础 URL，用于 SEO
    SITE_NAME = os.environ.get('SITE_NAME') or '快點訂'
    SITE_DESCRIPTION = os.environ.get('SITE_DESCRIPTION') or '快點訂 - 在线订餐平台，提供便捷的外卖订餐服务'
    
    # 文件上傳配置
    # 優先使用根目錄的 uploads，否則使用 public/uploads（向後兼容）
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    uploads_dir = os.path.join(BASE_DIR, 'uploads')
    uploads_dir_public = os.path.join(BASE_DIR, 'public', 'uploads')
    UPLOAD_FOLDER = uploads_dir if os.path.exists(uploads_dir) else uploads_dir_public
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_UPLOAD_SIZE_MB', '16')) * 1024 * 1024  # 默認16MB
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


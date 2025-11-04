"""
權限裝飾器
"""
from functools import wraps
from flask import session, jsonify, request
from app.models import User, Shop

def login_required(f):
    """需要登入的裝飾器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({
                    'error': 'unauthorized',
                    'message': '未認證，请先登录',
                    'details': {}
                }), 401
            from flask import redirect, url_for
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """需要特定角色的裝飾器"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({
                    'error': 'unauthorized',
                    'message': '未認證，请先登录',
                    'details': {}
                }), 401
            
            user = User.query.get(user_id)
            if not user or user.role not in roles:
                return jsonify({
                    'error': 'forbidden',
                    'message': '權限不足',
                    'details': {}
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def store_admin_required(f):
    """需要是店鋪管理者的裝飾器"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user or user.role != 'store_admin':
            return jsonify({
                'error': 'forbidden',
                'message': '需要店鋪管理者權限',
                'details': {}
            }), 403
        return f(*args, **kwargs)
    return decorated_function

def shop_access_required(shop_id_param='shop_id'):
    """需要存取特定店鋪權限的裝飾器"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            # 獲取shop_id
            shop_id = kwargs.get(shop_id_param) or request.args.get('shop_id') or request.json.get('shop_id') if request.is_json else None
            
            if not shop_id:
                return jsonify({
                    'error': 'bad_request',
                    'message': '缺少shop_id參數',
                    'details': {}
                }), 400
            
            shop = Shop.query.get(shop_id)
            if not shop:
                return jsonify({
                    'error': 'not_found',
                    'message': '店鋪不存在',
                    'details': {}
                }), 404
            
            # 管理員可以存取所有店鋪
            if user.role == 'admin':
                return f(*args, **kwargs)
            
            # 店鋪管理者只能存取自己的店鋪
            if user.role == 'store_admin' and shop.owner_id == user.id:
                return f(*args, **kwargs)
            
            return jsonify({
                'error': 'forbidden',
                'message': '無權存取此店鋪',
                'details': {}
            }), 403
        return decorated_function
    return decorator

def get_current_user():
    """獲取當前登入使用者"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


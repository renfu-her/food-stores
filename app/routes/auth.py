"""
認證路由
"""
from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from app import db
from app.models import User
from app.utils.password import hash_password, check_password
from app.utils.validators import validate_email
from app.utils.decorators import login_required, get_current_user
from app.utils.password_strength import validate_password_strength

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """使用者註冊"""
    try:
        data = request.get_json()
        
        # 驗證必填欄位
        if not data:
            return jsonify({
                'error': 'bad_request',
                'message': '請求資料不能為空',
                'details': {}
            }), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # 验证字段
        if not name:
            return jsonify({
                'error': 'validation_error',
                'message': '姓名不能為空',
                'details': {}
            }), 400
        
        is_valid, error_msg = validate_email(email)
        if not is_valid:
            return jsonify({
                'error': 'validation_error',
                'message': error_msg,
                'details': {}
            }), 400
        
        if not password or len(password) < 6:
            return jsonify({
                'error': 'validation_error',
                'message': '密碼長度至少6位',
                'details': {}
            }), 400
        
        # 验证密码强度（要求至少为 middle）
        is_valid, error_msg = validate_password_strength(password, min_strength='middle')
        if not is_valid:
            return jsonify({
                'error': 'validation_error',
                'message': error_msg,
                'details': {}
            }), 400
        
        # 檢查郵箱是否已存在
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'error': 'validation_error',
                'message': '該郵箱已被註冊',
                'details': {}
            }), 400
        
        # 建立新使用者（預設為customer角色）
        new_user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role='customer',
            is_active=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': '註冊成功',
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email,
                'role': new_user.role
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '註冊失敗',
            'details': {'error': str(e)}
        }), 500

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """使用者登入"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'bad_request',
                'message': '請求資料不能為空',
                'details': {}
            }), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({
                'error': 'validation_error',
                'message': '郵箱和密碼不能為空',
                'details': {}
            }), 400
        
        # 查找使用者
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password(password, user.password_hash):
            return jsonify({
                'error': 'unauthorized',
                'message': '郵箱或密碼錯誤',
                'details': {}
            }), 401
        
        if not user.is_active:
            return jsonify({
                'error': 'forbidden',
                'message': '帳戶已被禁用',
                'details': {}
            }), 403
        
        # 設置session
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_role'] = user.role
        session.permanent = True
        
        return jsonify({
            'message': '登入成功',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'internal_error',
            'message': '登入失敗',
            'details': {'error': str(e)}
        }), 500

@auth_bp.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """使用者登出"""
    try:
        session.clear()
        return jsonify({
            'message': '登出成功'
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'internal_error',
            'message': '登出失敗',
            'details': {'error': str(e)}
        }), 500

@auth_bp.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user_info():
    """獲取當前使用者資訊"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'error': 'unauthorized',
                'message': '未認證',
                'details': {}
            }), 401
        
        return jsonify({
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active
            }
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'internal_error',
            'message': '獲取使用者資訊失敗',
            'details': {'error': str(e)}
        }), 500

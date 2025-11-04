"""
用戶管理 API
"""
from flask import Blueprint, request, jsonify, session
from app import db
from app.models import User
from app.utils.decorators import role_required
from app.utils.password import hash_password
from app.utils.update_logger import log_update

users_api_bp = Blueprint('users_api', __name__)

@users_api_bp.route('', methods=['POST'])
@role_required('admin')
def create_user():
    """創建用戶"""
    try:
        data = request.get_json()
        
        # 檢查郵箱是否已存在
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'email_exists', 'message': '郵箱已被使用'}), 400
        
        # 創建用戶
        user = User(
            name=data['name'],
            email=data['email'],
            password_hash=hash_password(data['password']),
            role=data.get('role', 'customer'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(user)
        db.session.flush()  # 獲取用戶ID
        
        # 記錄日誌
        log_update(
            action='create',
            table_name='user',
            record_id=user.id,
            new_data={
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active
            },
            description=f'新增使用者: {user.name} ({user.email})'
        )
        
        db.session.commit()
        
        return jsonify({
            'message': '用戶創建成功',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'create_failed', 'message': str(e)}), 500

@users_api_bp.route('/<int:user_id>', methods=['PUT'])
@role_required('admin')
def update_user(user_id):
    """更新用戶"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # 保存舊數據
        old_data = {
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active
        }
        
        # 更新用戶信息
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            # 檢查郵箱是否被其他用戶使用
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                return jsonify({'error': 'email_exists', 'message': '郵箱已被使用'}), 400
            user.email = data['email']
        if 'password' in data and data['password']:
            user.password_hash = hash_password(data['password'])
        if 'role' in data:
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        # 新數據
        new_data = {
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active
        }
        
        # 記錄日誌
        log_update(
            action='update',
            table_name='user',
            record_id=user.id,
            old_data=old_data,
            new_data=new_data,
            description=f'更新使用者: {user.name} ({user.email})'
        )
        
        db.session.commit()
        
        return jsonify({
            'message': '用戶更新成功',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'update_failed', 'message': str(e)}), 500

@users_api_bp.route('/<int:user_id>', methods=['DELETE'])
@role_required('admin')
def delete_user(user_id):
    """刪除用戶"""
    try:
        user = User.query.get_or_404(user_id)
        
        # 保存用戶信息用於日誌
        user_data = {
            'name': user.name,
            'email': user.email,
            'role': user.role
        }
        
        # 記錄日誌
        log_update(
            action='delete',
            table_name='user',
            record_id=user.id,
            old_data=user_data,
            description=f'刪除使用者: {user.name} ({user.email})'
        )
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': '用戶刪除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'delete_failed', 'message': str(e)}), 500


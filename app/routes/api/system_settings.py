"""
系統設定 API
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import SystemSetting
from app.utils.decorators import role_required

system_settings_api_bp = Blueprint('system_settings_api', __name__)

@system_settings_api_bp.route('', methods=['GET'])
@role_required('admin')
def get_settings():
    """獲取所有系統設定（按分類）"""
    try:
        category = request.args.get('category')
        
        if category:
            settings = SystemSetting.query.filter_by(category=category).all()
        else:
            settings = SystemSetting.query.all()
        
        # 按分類分組
        settings_by_category = {}
        for setting in settings:
            if setting.category not in settings_by_category:
                settings_by_category[setting.category] = []
            
            settings_by_category[setting.category].append({
                'id': setting.id,
                'key': setting.setting_key,
                'value': setting.setting_value,
                'type': setting.setting_type,
                'description': setting.description,
                'category': setting.category,
                'is_encrypted': setting.is_encrypted
            })
        
        return jsonify({
            'settings': settings_by_category,
            'total': len(settings)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'internal_error',
            'message': '獲取設定失敗',
            'details': {'error': str(e)}
        }), 500


@system_settings_api_bp.route('/<int:setting_id>', methods=['GET'])
@role_required('admin')
def get_setting(setting_id):
    """獲取單個設定"""
    try:
        setting = SystemSetting.query.get_or_404(setting_id)
        
        return jsonify({
            'setting': {
                'id': setting.id,
                'key': setting.setting_key,
                'value': setting.setting_value,
                'type': setting.setting_type,
                'description': setting.description,
                'category': setting.category,
                'is_encrypted': setting.is_encrypted
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'internal_error',
            'message': '獲取設定失敗',
            'details': {'error': str(e)}
        }), 500


@system_settings_api_bp.route('', methods=['POST'])
@role_required('admin')
def create_setting():
    """創建新設定"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'bad_request',
                'message': '請求資料不能為空',
                'details': {}
            }), 400
        
        setting_key = data.get('key', '').strip()
        setting_value = data.get('value', '')
        setting_type = data.get('type', 'text')
        description = data.get('description', '').strip()
        category = data.get('category', 'general')
        
        if not setting_key:
            return jsonify({
                'error': 'validation_error',
                'message': '設定鍵不能為空',
                'details': {}
            }), 400
        
        # 檢查是否已存在
        existing = SystemSetting.query.filter_by(setting_key=setting_key).first()
        if existing:
            return jsonify({
                'error': 'validation_error',
                'message': f'設定鍵 {setting_key} 已存在',
                'details': {}
            }), 400
        
        # 創建設定
        new_setting = SystemSetting(
            setting_key=setting_key,
            setting_value=setting_value,
            setting_type=setting_type,
            description=description,
            category=category
        )
        
        db.session.add(new_setting)
        db.session.commit()
        
        return jsonify({
            'message': '設定創建成功',
            'setting': {
                'id': new_setting.id,
                'key': new_setting.setting_key,
                'value': new_setting.setting_value,
                'type': new_setting.setting_type,
                'description': new_setting.description,
                'category': new_setting.category
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '創建設定失敗',
            'details': {'error': str(e)}
        }), 500


@system_settings_api_bp.route('/<int:setting_id>', methods=['PUT'])
@role_required('admin')
def update_setting(setting_id):
    """更新設定"""
    try:
        setting = SystemSetting.query.get_or_404(setting_id)
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'bad_request',
                'message': '請求資料不能為空',
                'details': {}
            }), 400
        
        # 更新字段
        if 'value' in data:
            setting.setting_value = data['value']
        if 'description' in data:
            setting.description = data['description']
        if 'category' in data:
            setting.category = data['category']
        
        db.session.commit()
        
        return jsonify({
            'message': '設定更新成功',
            'setting': {
                'id': setting.id,
                'key': setting.setting_key,
                'value': setting.setting_value,
                'type': setting.setting_type,
                'description': setting.description,
                'category': setting.category
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '更新設定失敗',
            'details': {'error': str(e)}
        }), 500


@system_settings_api_bp.route('/batch', methods=['PUT'])
@role_required('admin')
def batch_update_settings():
    """批量更新設定"""
    try:
        data = request.get_json()
        
        if not data or 'settings' not in data:
            return jsonify({
                'error': 'bad_request',
                'message': '請求資料不能為空',
                'details': {}
            }), 400
        
        settings_data = data['settings']
        updated_count = 0
        
        for setting_data in settings_data:
            key = setting_data.get('key')
            value = setting_data.get('value')
            
            if not key:
                continue
            
            setting = SystemSetting.query.filter_by(setting_key=key).first()
            if setting:
                setting.setting_value = value
                updated_count += 1
            else:
                # 如果不存在，創建新的
                new_setting = SystemSetting(
                    setting_key=key,
                    setting_value=value,
                    setting_type=setting_data.get('type', 'text'),
                    description=setting_data.get('description', ''),
                    category=setting_data.get('category', 'general')
                )
                db.session.add(new_setting)
                updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'成功更新 {updated_count} 個設定',
            'updated_count': updated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '批量更新設定失敗',
            'details': {'error': str(e)}
        }), 500


@system_settings_api_bp.route('/<int:setting_id>', methods=['DELETE'])
@role_required('admin')
def delete_setting(setting_id):
    """刪除設定"""
    try:
        setting = SystemSetting.query.get_or_404(setting_id)
        
        db.session.delete(setting)
        db.session.commit()
        
        return jsonify({
            'message': '設定刪除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '刪除設定失敗',
            'details': {'error': str(e)}
        }), 500


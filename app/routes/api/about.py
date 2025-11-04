"""
關於我們 API 路由
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import About
from app.utils.decorators import role_required
from app.utils.update_logger import log_update

about_api_bp = Blueprint('about_api', __name__)

@about_api_bp.route('', methods=['GET'])
def get_about_list():
    """獲取關於我們列表（公開，可篩選啟用狀態）"""
    is_active = request.args.get('is_active', type=str)
    
    query = About.query
    if is_active == 'true':
        query = query.filter_by(is_active=True)
    
    about_list = query.order_by(About.display_order, About.created_at.desc()).all()
    
    return jsonify([{
        'id': about.id,
        'title': about.title,
        'content': about.content,
        'is_active': about.is_active,
        'display_order': about.display_order,
        'created_at': about.created_at.isoformat() if about.created_at else None,
        'updated_at': about.updated_at.isoformat() if about.updated_at else None
    } for about in about_list])

@about_api_bp.route('/<int:about_id>', methods=['GET'])
def get_about(about_id):
    """獲取單個關於我們記錄"""
    about = About.query.get_or_404(about_id)
    
    return jsonify({
        'id': about.id,
        'title': about.title,
        'content': about.content,
        'is_active': about.is_active,
        'display_order': about.display_order,
        'created_at': about.created_at.isoformat() if about.created_at else None,
        'updated_at': about.updated_at.isoformat() if about.updated_at else None
    })

@about_api_bp.route('', methods=['POST'])
@role_required('admin')
def create_about():
    """新增關於我們記錄"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '缺少請求數據'}), 400
    
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    is_active = data.get('is_active', True)
    
    if not title:
        return jsonify({'error': '請輸入標題'}), 400
    
    if not content:
        return jsonify({'error': '請輸入內容'}), 400
    
    try:
        # 獲取最大排序號
        max_order = db.session.query(db.func.max(About.display_order)).scalar() or 0
        
        about = About(
            title=title,
            content=content,
            is_active=is_active,
            display_order=max_order + 1
        )
        
        db.session.add(about)
        db.session.flush()
        
        log_update(
            action='create',
            table_name='about',
            record_id=about.id,
            new_data={'title': title, 'content': content, 'is_active': is_active},
            description=f'新增關於我們: {title}'
        )
        
        db.session.commit()
        
        return jsonify({
            'id': about.id,
            'title': about.title,
            'content': about.content,
            'is_active': about.is_active,
            'display_order': about.display_order
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@about_api_bp.route('/<int:about_id>', methods=['PUT'])
@role_required('admin')
def update_about(about_id):
    """更新關於我們記錄"""
    about = About.query.get_or_404(about_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '缺少請求數據'}), 400
    
    try:
        old_data = {
            'title': about.title,
            'content': about.content,
            'is_active': about.is_active
        }
        
        if 'title' in data:
            about.title = data['title'].strip()
        if 'content' in data:
            about.content = data['content'].strip()
        if 'is_active' in data:
            about.is_active = bool(data['is_active'])
        
        new_data = {
            'title': about.title,
            'content': about.content,
            'is_active': about.is_active
        }
        
        log_update(
            action='update',
            table_name='about',
            record_id=about.id,
            old_data=old_data,
            new_data=new_data,
            description=f'更新關於我們: {about.title}'
        )
        
        db.session.commit()
        
        return jsonify({
            'id': about.id,
            'title': about.title,
            'content': about.content,
            'is_active': about.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@about_api_bp.route('/<int:about_id>', methods=['DELETE'])
@role_required('admin')
def delete_about(about_id):
    """刪除關於我們記錄"""
    about = About.query.get_or_404(about_id)
    
    try:
        log_update(
            action='delete',
            table_name='about',
            record_id=about.id,
            old_data={'title': about.title, 'content': about.content},
            description=f'刪除關於我們: {about.title}'
        )
        
        db.session.delete(about)
        db.session.commit()
        
        return jsonify({'message': '刪除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '刪除失敗'}), 500

@about_api_bp.route('/reorder', methods=['PUT'])
@role_required('admin')
def reorder_about():
    """重新排序關於我們記錄"""
    data = request.get_json()
    
    if not data or 'order' not in data:
        return jsonify({'error': '缺少排序數據'}), 400
    
    order_list = data['order']  # [about_id1, about_id2, ...]
    
    try:
        for index, about_id in enumerate(order_list):
            about = About.query.get(about_id)
            if about:
                about.display_order = index + 1
        
        log_update(
            action='update',
            table_name='about',
            record_id=0,
            new_data={'order': order_list},
            description=f'重新排序關於我們'
        )
        
        db.session.commit()
        
        return jsonify({'message': '排序成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '排序失敗'}), 500

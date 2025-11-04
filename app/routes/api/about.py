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
def get_about():
    """獲取關於我們內容（公開）"""
    about = About.query.first()
    
    if not about:
        return jsonify({
            'id': None,
            'content': '',
            'updated_at': None
        })
    
    return jsonify({
        'id': about.id,
        'content': about.content,
        'updated_at': about.updated_at.isoformat() if about.updated_at else None
    })

@about_api_bp.route('', methods=['PUT'])
@role_required('admin')
def update_about():
    """更新關於我們內容"""
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({'error': '缺少內容'}), 400
    
    content = data['content'].strip()
    
    try:
        about = About.query.first()
        
        if not about:
            # 創建新記錄
            about = About(content=content)
            db.session.add(about)
            db.session.flush()
            
            log_update(
                action='create',
                table_name='about',
                record_id=about.id,
                new_data={'content': content},
                description='創建關於我們內容'
            )
        else:
            # 更新現有記錄
            old_data = {'content': about.content}
            about.content = content
            
            log_update(
                action='update',
                table_name='about',
                record_id=about.id,
                old_data=old_data,
                new_data={'content': content},
                description='更新關於我們內容'
            )
        
        db.session.commit()
        
        return jsonify({
            'id': about.id,
            'content': about.content,
            'updated_at': about.updated_at.isoformat() if about.updated_at else None
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


"""
最新消息 API 路由
"""
import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import News
from app.utils.decorators import role_required
from app.utils.update_logger import log_update
from app.utils.image_processor import convert_to_webp, allowed_image_file
from app.utils.upload_path import get_upload_file_path
from datetime import datetime

news_api_bp = Blueprint('news_api', __name__)

@news_api_bp.route('', methods=['GET'])
def get_news_list():
    """獲取最新消息列表（公開，可篩選啟用狀態）"""
    is_active = request.args.get('is_active', type=str)
    
    query = News.query
    if is_active == 'true':
        query = query.filter_by(is_active=True)
    
    news_list = query.order_by(News.publish_date.desc(), News.created_at.desc()).all()
    
    return jsonify([{
        'id': news.id,
        'name': news.name,
        'description': news.description,
        'image_path': news.image_path,
        'is_active': news.is_active,
        'publish_date': news.publish_date.isoformat() if news.publish_date else None,
        'created_at': news.created_at.isoformat() if news.created_at else None,
        'updated_at': news.updated_at.isoformat() if news.updated_at else None
    } for news in news_list])

@news_api_bp.route('/<int:news_id>', methods=['GET'])
def get_news(news_id):
    """獲取單個最新消息"""
    news = News.query.get_or_404(news_id)
    
    return jsonify({
        'id': news.id,
        'name': news.name,
        'description': news.description,
        'image_path': news.image_path,
        'is_active': news.is_active,
        'publish_date': news.publish_date.isoformat() if news.publish_date else None,
        'created_at': news.created_at.isoformat() if news.created_at else None
    })

@news_api_bp.route('', methods=['POST'])
@role_required('admin')
def create_news():
    """新增最新消息"""
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip() or None
    is_active = request.form.get('is_active', 'true').lower() == 'true'
    publish_date_str = request.form.get('publish_date', '').strip()
    
    if not name:
        return jsonify({'error': '請輸入消息標題'}), 400
    
    # 處理發布日期
    if publish_date_str:
        try:
            publish_date = datetime.fromisoformat(publish_date_str.replace('Z', '+00:00'))
        except:
            publish_date = datetime.utcnow()
    else:
        publish_date = datetime.utcnow()
    
    # 處理圖片上傳（可選）
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '' and allowed_image_file(file.filename):
            try:
                # 生成安全的文件名（不含擴展名，因為會轉換為 .webp）
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
                filename_base = f"news_{timestamp}"
                
                # 確保目錄存在
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'news')
                os.makedirs(upload_dir, exist_ok=True)
                
                # 轉換為 WebP 並保存
                output_path = os.path.join(upload_dir, filename_base)
                filepath = convert_to_webp(file, output_path, quality=85)
                
                # 獲取實際的文件名（含 .webp 擴展名）
                filename = os.path.basename(filepath)
                
                image_path = f'/uploads/news/{filename}'
            except Exception as e:
                current_app.logger.error(f'上傳圖片失敗: {str(e)}')
    
    try:
        news = News(
            name=name,
            description=description,
            image_path=image_path,
            is_active=is_active,
            publish_date=publish_date
        )
        
        db.session.add(news)
        db.session.flush()
        
        log_update(
            action='create',
            table_name='news',
            record_id=news.id,
            new_data={
                'name': name,
                'description': description,
                'image_path': image_path,
                'is_active': is_active,
                'publish_date': publish_date.isoformat()
            },
            description=f'新增最新消息: {name}'
        )
        
        db.session.commit()
        
        return jsonify({
            'id': news.id,
            'name': news.name,
            'description': news.description,
            'image_path': news.image_path,
            'is_active': news.is_active,
            'publish_date': news.publish_date.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'新增消息失敗: {str(e)}')
        return jsonify({'error': '新增失敗'}), 500

@news_api_bp.route('/<int:news_id>', methods=['PUT'])
@role_required('admin')
def update_news(news_id):
    """更新最新消息"""
    news = News.query.get_or_404(news_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '缺少請求數據'}), 400
    
    try:
        old_data = {
            'name': news.name,
            'description': news.description,
            'is_active': news.is_active,
            'publish_date': news.publish_date.isoformat() if news.publish_date else None
        }
        
        if 'name' in data:
            news.name = data['name'].strip()
        if 'description' in data:
            news.description = data['description'].strip() if data['description'] else None
        if 'is_active' in data:
            news.is_active = bool(data['is_active'])
        if 'publish_date' in data and data['publish_date']:
            try:
                news.publish_date = datetime.fromisoformat(data['publish_date'].replace('Z', '+00:00'))
            except:
                pass
        
        new_data = {
            'name': news.name,
            'description': news.description,
            'is_active': news.is_active,
            'publish_date': news.publish_date.isoformat() if news.publish_date else None
        }
        
        log_update(
            action='update',
            table_name='news',
            record_id=news.id,
            old_data=old_data,
            new_data=new_data,
            description=f'更新最新消息: {news.name}'
        )
        
        db.session.commit()
        
        return jsonify({
            'id': news.id,
            'name': news.name,
            'description': news.description,
            'image_path': news.image_path,
            'is_active': news.is_active,
            'publish_date': news.publish_date.isoformat() if news.publish_date else None
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@news_api_bp.route('/<int:news_id>/image', methods=['PUT'])
@role_required('admin')
def update_news_image(news_id):
    """更新最新消息圖片"""
    news = News.query.get_or_404(news_id)
    
    if 'image' not in request.files:
        return jsonify({'error': '沒有上傳文件'}), 400
    
    file = request.files['image']
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip() or None
    is_active = request.form.get('is_active', 'true').lower() == 'true'
    publish_date_str = request.form.get('publish_date', '').strip()
    
    if file.filename == '':
        return jsonify({'error': '沒有選擇文件'}), 400
    
    if not allowed_image_file(file.filename):
        return jsonify({'error': '不支持的文件格式'}), 400
    
    try:
        # 刪除舊文件
        if news.image_path:
            old_file_path = get_upload_file_path(news.image_path, current_app.root_path)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        
        # 生成安全的文件名（不含擴展名，因為會轉換為 .webp）
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        filename_base = f"news_{timestamp}"
        
        # 確保目錄存在
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'news')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 轉換為 WebP 並保存
        output_path = os.path.join(upload_dir, filename_base)
        filepath = convert_to_webp(file, output_path, quality=85)
        
        # 獲取實際的文件名（含 .webp 擴展名）
        filename = os.path.basename(filepath)
        
        old_data = {
            'name': news.name,
            'description': news.description,
            'image_path': news.image_path,
            'is_active': news.is_active,
            'publish_date': news.publish_date.isoformat() if news.publish_date else None
        }
        
        # 更新數據庫記錄
        relative_path = f'/uploads/news/{filename}'
        news.image_path = relative_path
        if name:
            news.name = name
        if description is not None:
            news.description = description
        news.is_active = is_active
        if publish_date_str:
            try:
                news.publish_date = datetime.fromisoformat(publish_date_str.replace('Z', '+00:00'))
            except:
                pass
        
        new_data = {
            'name': news.name,
            'description': news.description,
            'image_path': news.image_path,
            'is_active': news.is_active,
            'publish_date': news.publish_date.isoformat() if news.publish_date else None
        }
        
        log_update(
            action='update',
            table_name='news',
            record_id=news.id,
            old_data=old_data,
            new_data=new_data,
            description=f'更新最新消息圖片: {news.name}'
        )
        
        db.session.commit()
        
        return jsonify({
            'id': news.id,
            'name': news.name,
            'description': news.description,
            'image_path': news.image_path,
            'is_active': news.is_active,
            'publish_date': news.publish_date.isoformat() if news.publish_date else None
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'更新消息圖片失敗: {str(e)}')
        return jsonify({'error': '更新失敗'}), 500

@news_api_bp.route('/<int:news_id>', methods=['DELETE'])
@role_required('admin')
def delete_news(news_id):
    """刪除最新消息"""
    news = News.query.get_or_404(news_id)
    
    try:
        # 刪除文件
        if news.image_path:
            file_path = get_upload_file_path(news.image_path, current_app.root_path)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        log_update(
            action='delete',
            table_name='news',
            record_id=news.id,
            old_data={'name': news.name, 'image_path': news.image_path},
            description=f'刪除最新消息: {news.name}'
        )
        
        db.session.delete(news)
        db.session.commit()
        
        return jsonify({'message': '刪除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'刪除消息失敗: {str(e)}')
        return jsonify({'error': '刪除失敗'}), 500


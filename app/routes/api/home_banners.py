"""
首頁 Banner API 路由
"""
import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import HomeBanner
from app.utils.decorators import role_required
from app.utils.update_logger import log_update
from app.utils.image_processor import convert_to_webp, allowed_image_file
from datetime import datetime

home_banners_api_bp = Blueprint('home_banners_api', __name__)

@home_banners_api_bp.route('', methods=['GET'])
def get_home_banners():
    """獲取所有首頁 Banner（公開，可篩選啟用狀態）"""
    is_active = request.args.get('is_active', type=str)
    
    query = HomeBanner.query
    if is_active == 'true':
        query = query.filter_by(is_active=True)
    
    banners = query.order_by(HomeBanner.display_order, HomeBanner.created_at.desc()).all()
    
    return jsonify([{
        'id': banner.id,
        'name': banner.name,
        'image_path': banner.image_path,
        'title': banner.title,
        'subtitle': banner.subtitle,
        'link': banner.link,
        'is_active': banner.is_active,
        'display_order': banner.display_order,
        'created_at': banner.created_at.isoformat() if banner.created_at else None,
        'updated_at': banner.updated_at.isoformat() if banner.updated_at else None
    } for banner in banners])

@home_banners_api_bp.route('/<int:banner_id>', methods=['GET'])
def get_home_banner(banner_id):
    """獲取單個 Banner"""
    banner = HomeBanner.query.get_or_404(banner_id)
    
    return jsonify({
        'id': banner.id,
        'name': banner.name,
        'image_path': banner.image_path,
        'title': banner.title,
        'subtitle': banner.subtitle,
        'link': banner.link,
        'is_active': banner.is_active,
        'display_order': banner.display_order,
        'created_at': banner.created_at.isoformat() if banner.created_at else None
    })

@home_banners_api_bp.route('', methods=['POST'])
@role_required('admin')
def create_home_banner():
    """新增首頁 Banner"""
    if 'image' not in request.files:
        return jsonify({'error': '沒有上傳文件'}), 400
    
    file = request.files['image']
    name = request.form.get('name', '').strip()
    title = request.form.get('title', '').strip() or None
    subtitle = request.form.get('subtitle', '').strip() or None
    link = request.form.get('link', '').strip() or None
    is_active = request.form.get('is_active', 'true').lower() == 'true'
    
    if not name:
        return jsonify({'error': '請輸入 Banner 名稱'}), 400
    
    if file.filename == '':
        return jsonify({'error': '沒有選擇文件'}), 400
    
    if not allowed_image_file(file.filename):
        return jsonify({'error': '不支持的文件格式'}), 400
    
    try:
        # 生成安全的文件名（不含擴展名，因為會轉換為 .webp）
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        filename_base = f"home_banner_{timestamp}"
        
        # 確保目錄存在
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'banners')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 轉換為 WebP 並保存（首頁 Banner 使用更高分辨率）
        output_path = os.path.join(upload_dir, filename_base)
        filepath = convert_to_webp(file, output_path, quality=90, max_width=2560, max_height=1440)
        
        # 獲取實際的文件名（含 .webp 擴展名）
        filename = os.path.basename(filepath)
        
        # 獲取最大排序號
        max_order = db.session.query(db.func.max(HomeBanner.display_order)).scalar() or 0
        
        # 創建數據庫記錄
        relative_path = f'/uploads/banners/{filename}'
        banner = HomeBanner(
            name=name,
            image_path=relative_path,
            title=title,
            subtitle=subtitle,
            link=link,
            is_active=is_active,
            display_order=max_order + 1
        )
        
        db.session.add(banner)
        db.session.flush()
        
        log_update(
            action='create',
            table_name='home_banner',
            record_id=banner.id,
            new_data={'name': name, 'image_path': relative_path, 'is_active': is_active},
            description=f'新增首頁 Banner: {name}'
        )
        
        db.session.commit()
        
        return jsonify({
            'id': banner.id,
            'name': banner.name,
            'image_path': banner.image_path,
            'title': banner.title,
            'subtitle': banner.subtitle,
            'link': banner.link,
            'is_active': banner.is_active,
            'display_order': banner.display_order
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'上傳 Banner 失敗: {str(e)}')
        return jsonify({'error': '上傳失敗'}), 500

@home_banners_api_bp.route('/<int:banner_id>', methods=['PUT'])
@role_required('admin')
def update_home_banner(banner_id):
    """更新首頁 Banner"""
    banner = HomeBanner.query.get_or_404(banner_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '缺少請求數據'}), 400
    
    try:
        old_data = {
            'name': banner.name,
            'title': banner.title,
            'subtitle': banner.subtitle,
            'link': banner.link,
            'is_active': banner.is_active
        }
        
        if 'name' in data:
            banner.name = data['name'].strip()
        if 'title' in data:
            banner.title = data['title'].strip() if data['title'] else None
        if 'subtitle' in data:
            banner.subtitle = data['subtitle'].strip() if data['subtitle'] else None
        if 'link' in data:
            banner.link = data['link'].strip() if data['link'] else None
        if 'is_active' in data:
            banner.is_active = bool(data['is_active'])
        
        new_data = {
            'name': banner.name,
            'title': banner.title,
            'subtitle': banner.subtitle,
            'link': banner.link,
            'is_active': banner.is_active
        }
        
        log_update(
            action='update',
            table_name='home_banner',
            record_id=banner.id,
            old_data=old_data,
            new_data=new_data,
            description=f'更新首頁 Banner: {banner.name}'
        )
        
        db.session.commit()
        
        return jsonify({
            'id': banner.id,
            'name': banner.name,
            'title': banner.title,
            'subtitle': banner.subtitle,
            'link': banner.link,
            'is_active': banner.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@home_banners_api_bp.route('/<int:banner_id>/image', methods=['PUT'])
@role_required('admin')
def update_home_banner_image(banner_id):
    """更新首頁 Banner 圖片"""
    banner = HomeBanner.query.get_or_404(banner_id)
    
    if 'image' not in request.files:
        return jsonify({'error': '沒有上傳文件'}), 400
    
    file = request.files['image']
    name = request.form.get('name', '').strip()
    title = request.form.get('title', '').strip() or None
    subtitle = request.form.get('subtitle', '').strip() or None
    link = request.form.get('link', '').strip() or None
    is_active = request.form.get('is_active', 'true').lower() == 'true'
    
    if file.filename == '':
        return jsonify({'error': '沒有選擇文件'}), 400
    
    if not allowed_image_file(file.filename):
        return jsonify({'error': '不支持的文件格式'}), 400
    
    try:
        # 刪除舊文件
        old_file_path = os.path.join(current_app.root_path, '..', 'public', banner.image_path.lstrip('/'))
        if os.path.exists(old_file_path):
            os.remove(old_file_path)
        
        # 生成安全的文件名（不含擴展名，因為會轉換為 .webp）
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        filename_base = f"home_banner_{timestamp}"
        
        # 確保目錄存在
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'banners')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 轉換為 WebP 並保存（首頁 Banner 使用更高分辨率）
        output_path = os.path.join(upload_dir, filename_base)
        filepath = convert_to_webp(file, output_path, quality=90, max_width=2560, max_height=1440)
        
        # 獲取實際的文件名（含 .webp 擴展名）
        filename = os.path.basename(filepath)
        
        old_data = {
            'name': banner.name,
            'image_path': banner.image_path,
            'title': banner.title,
            'subtitle': banner.subtitle,
            'link': banner.link,
            'is_active': banner.is_active
        }
        
        # 更新數據庫記錄
        relative_path = f'/uploads/banners/{filename}'
        banner.image_path = relative_path
        if name:
            banner.name = name
        if title is not None:
            banner.title = title
        if subtitle is not None:
            banner.subtitle = subtitle
        if link is not None:
            banner.link = link
        banner.is_active = is_active
        
        new_data = {
            'name': banner.name,
            'image_path': banner.image_path,
            'title': banner.title,
            'subtitle': banner.subtitle,
            'link': banner.link,
            'is_active': banner.is_active
        }
        
        log_update(
            action='update',
            table_name='home_banner',
            record_id=banner.id,
            old_data=old_data,
            new_data=new_data,
            description=f'更新首頁 Banner 圖片: {banner.name}'
        )
        
        db.session.commit()
        
        return jsonify({
            'id': banner.id,
            'name': banner.name,
            'image_path': banner.image_path,
            'title': banner.title,
            'subtitle': banner.subtitle,
            'link': banner.link,
            'is_active': banner.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'更新 Banner 圖片失敗: {str(e)}')
        return jsonify({'error': '更新失敗'}), 500

@home_banners_api_bp.route('/<int:banner_id>', methods=['DELETE'])
@role_required('admin')
def delete_home_banner(banner_id):
    """刪除首頁 Banner"""
    banner = HomeBanner.query.get_or_404(banner_id)
    
    try:
        # 刪除文件
        file_path = os.path.join(current_app.root_path, '..', 'public', banner.image_path.lstrip('/'))
        if os.path.exists(file_path):
            os.remove(file_path)
        
        log_update(
            action='delete',
            table_name='home_banner',
            record_id=banner.id,
            old_data={'name': banner.name, 'image_path': banner.image_path},
            description=f'刪除首頁 Banner: {banner.name}'
        )
        
        db.session.delete(banner)
        db.session.commit()
        
        return jsonify({'message': '刪除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'刪除 Banner 失敗: {str(e)}')
        return jsonify({'error': '刪除失敗'}), 500

@home_banners_api_bp.route('/reorder', methods=['PUT'])
@role_required('admin')
def reorder_home_banners():
    """重新排序首頁 Banner"""
    data = request.get_json()
    
    if not data or 'order' not in data:
        return jsonify({'error': '缺少排序數據'}), 400
    
    order_list = data['order']  # [banner_id1, banner_id2, ...]
    
    try:
        for index, banner_id in enumerate(order_list):
            banner = HomeBanner.query.get(banner_id)
            if banner:
                banner.display_order = index + 1
        
        log_update(
            action='update',
            table_name='home_banner',
            record_id=0,
            new_data={'order': order_list},
            description=f'重新排序首頁 Banner'
        )
        
        db.session.commit()
        
        return jsonify({'message': '排序成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'排序失敗: {str(e)}')
        return jsonify({'error': '排序失敗'}), 500


"""
店鋪 Banner API 路由
"""
import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Shop
from app.utils.decorators import role_required
from app.utils.update_logger import log_update
from datetime import datetime

shop_banner_api_bp = Blueprint('shop_banner_api', __name__)

def allowed_file(filename):
    """檢查文件擴展名是否允許"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_IMAGE_EXTENSIONS']

@shop_banner_api_bp.route('/shops/<int:shop_id>/banner', methods=['POST'])
@role_required('admin')
def upload_shop_banner(shop_id):
    """上傳店鋪 Banner"""
    shop = Shop.query.get_or_404(shop_id)
    
    if 'banner' not in request.files:
        return jsonify({'error': '沒有上傳文件'}), 400
    
    file = request.files['banner']
    
    if file.filename == '':
        return jsonify({'error': '沒有選擇文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式'}), 400
    
    try:
        # 刪除舊的 Banner 文件
        if shop.banner_image:
            old_file_path = os.path.join(current_app.root_path, '..', 'public', shop.banner_image.lstrip('/'))
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        
        # 生成安全的文件名
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"banner_shop_{shop_id}_{timestamp}.{ext}"
        
        # 確保目錄存在
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'banners')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # 更新數據庫
        relative_path = f'/uploads/banners/{filename}'
        old_banner = shop.banner_image
        shop.banner_image = relative_path
        
        log_update(
            action='update',
            table_name='shop',
            record_id=shop.id,
            old_data={'banner_image': old_banner},
            new_data={'banner_image': relative_path},
            description=f'上傳店鋪 Banner: {shop.name}'
        )
        
        db.session.commit()
        
        return jsonify({
            'banner_image': relative_path,
            'message': '上傳成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'上傳 Banner 失敗: {str(e)}')
        return jsonify({'error': '上傳失敗'}), 500

@shop_banner_api_bp.route('/shops/<int:shop_id>/banner', methods=['DELETE'])
@role_required('admin')
def delete_shop_banner(shop_id):
    """刪除店鋪 Banner"""
    shop = Shop.query.get_or_404(shop_id)
    
    if not shop.banner_image:
        return jsonify({'error': 'Banner 不存在'}), 404
    
    try:
        # 刪除文件
        file_path = os.path.join(current_app.root_path, '..', 'public', shop.banner_image.lstrip('/'))
        if os.path.exists(file_path):
            os.remove(file_path)
        
        old_banner = shop.banner_image
        shop.banner_image = None
        
        log_update(
            action='update',
            table_name='shop',
            record_id=shop.id,
            old_data={'banner_image': old_banner},
            new_data={'banner_image': None},
            description=f'刪除店鋪 Banner: {shop.name}'
        )
        
        db.session.commit()
        
        return jsonify({'message': '刪除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'刪除 Banner 失敗: {str(e)}')
        return jsonify({'error': '刪除失敗'}), 500


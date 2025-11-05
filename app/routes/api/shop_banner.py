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
from app.utils.image_processor import convert_to_webp, allowed_image_file
from datetime import datetime

shop_banner_api_bp = Blueprint('shop_banner_api', __name__)

@shop_banner_api_bp.route('/shops/<int:shop_id>/banner', methods=['POST'])
@role_required('admin', 'store_admin')
def upload_shop_banner(shop_id):
    """上傳店鋪 Banner"""
    from app.utils.decorators import get_current_user
    user = get_current_user()
    shop = Shop.query.get_or_404(shop_id)
    
    # 權限檢查：store_admin 只能上傳自己的店鋪 Banner
    if user.role == 'store_admin':
        if shop.owner_id != user.id:
            return jsonify({'error': 'forbidden', 'message': '無權上傳此店鋪的 Banner'}), 403
    
    if 'banner' not in request.files:
        return jsonify({'error': '沒有上傳文件'}), 400
    
    file = request.files['banner']
    
    if file.filename == '':
        return jsonify({'error': '沒有選擇文件'}), 400
    
    if not allowed_image_file(file.filename):
        return jsonify({'error': '不支持的文件格式，請上傳圖片文件'}), 400
    
    try:
        # 刪除舊的 Banner 文件
        if shop.banner_image:
            old_file_path = os.path.join(current_app.root_path, '..', 'public', shop.banner_image.lstrip('/'))
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        
        # 生成安全的文件名（不含擴展名，因為會轉換為 .webp）
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        filename_base = f"banner_shop_{shop_id}_{timestamp}"
        
        # 確保目錄存在
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'banners')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 轉換為 WebP 並保存（Banner 使用更高分辨率）
        output_path = os.path.join(upload_dir, filename_base)
        filepath = convert_to_webp(file, output_path, quality=90, max_width=2560, max_height=1440)
        
        # 獲取實際的文件名（含 .webp 擴展名）
        filename = os.path.basename(filepath)
        
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
@role_required('admin', 'store_admin')
def delete_shop_banner(shop_id):
    """刪除店鋪 Banner"""
    from app.utils.decorators import get_current_user
    user = get_current_user()
    shop = Shop.query.get_or_404(shop_id)
    
    # 權限檢查：store_admin 只能刪除自己的店鋪 Banner
    if user.role == 'store_admin':
        if shop.owner_id != user.id:
            return jsonify({'error': 'forbidden', 'message': '無權刪除此店鋪的 Banner'}), 403
    
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


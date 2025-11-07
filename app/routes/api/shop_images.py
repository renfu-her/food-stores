"""
店鋪圖片 API 路由
"""
import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from app import db
from app.models import Shop, ShopImage
from app.utils.decorators import login_required, role_required
from app.utils.update_logger import log_update
from app.utils.image_processor import convert_to_webp, allowed_image_file
from app.utils.upload_path import get_upload_file_path
from datetime import datetime

shop_images_api_bp = Blueprint('shop_images_api', __name__)

@shop_images_api_bp.route('/shops/<int:shop_id>/images', methods=['POST'])
@role_required('admin', 'store_admin')
def upload_shop_image(shop_id):
    """上傳店鋪圖片"""
    from app.utils.decorators import get_current_user
    user = get_current_user()
    shop = Shop.query.get_or_404(shop_id)
    
    # 權限檢查：store_admin 只能上傳自己的店鋪圖片
    if user.role == 'store_admin':
        if shop.owner_id != user.id:
            return jsonify({'error': 'forbidden', 'message': '無權上傳此店鋪的圖片'}), 403
    
    if 'image' not in request.files:
        return jsonify({'error': '沒有上傳文件'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': '沒有選擇文件'}), 400
    
    if not allowed_image_file(file.filename):
        return jsonify({'error': '不支持的文件格式，請上傳圖片文件'}), 400
    
    try:
        # 生成安全的文件名（不含擴展名，因為會轉換為 .webp）
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        filename_base = f"shop_{shop_id}_{timestamp}"
        
        # 確保目錄存在
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'shops')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 轉換為 WebP 並保存
        output_path = os.path.join(upload_dir, filename_base)
        filepath = convert_to_webp(file, output_path, quality=85)
        
        # 獲取實際的文件名（含 .webp 擴展名）
        filename = os.path.basename(filepath)
        
        # 獲取當前最大的 display_order
        max_order = db.session.query(db.func.max(ShopImage.display_order)).filter_by(shop_id=shop_id).scalar() or 0
        
        # 創建數據庫記錄
        relative_path = f'/uploads/shops/{filename}'
        shop_image = ShopImage(
            shop_id=shop_id,
            image_path=relative_path,
            display_order=max_order + 1
        )
        
        db.session.add(shop_image)
        db.session.flush()
        
        log_update(
            action='create',
            table_name='shop_image',
            record_id=shop_image.id,
            new_data={'shop_id': shop_id, 'image_path': relative_path, 'display_order': shop_image.display_order},
            description=f'上傳店鋪圖片: {shop.name}'
        )
        
        db.session.commit()
        
        return jsonify({
            'id': shop_image.id,
            'image_path': relative_path,
            'display_order': shop_image.display_order,
            'created_at': shop_image.created_at.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'上傳圖片失敗: {str(e)}')
        return jsonify({'error': '上傳失敗'}), 500

@shop_images_api_bp.route('/shops/<int:shop_id>/images', methods=['GET'])
def get_shop_images(shop_id):
    """獲取店鋪所有圖片"""
    shop = Shop.query.get_or_404(shop_id)
    images = ShopImage.query.filter_by(shop_id=shop_id).order_by(ShopImage.display_order).all()
    
    return jsonify([{
        'id': img.id,
        'image_path': img.image_path,
        'display_order': img.display_order,
        'created_at': img.created_at.isoformat()
    } for img in images])

@shop_images_api_bp.route('/shop-images/<int:image_id>', methods=['DELETE'])
@role_required('admin', 'store_admin')
def delete_shop_image(image_id):
    """刪除店鋪圖片"""
    from app.utils.decorators import get_current_user
    user = get_current_user()
    shop_image = ShopImage.query.get_or_404(image_id)
    shop_id = shop_image.shop_id
    
    # 權限檢查：store_admin 只能刪除自己店鋪的圖片
    if user.role == 'store_admin':
        shop = Shop.query.get(shop_id)
        if not shop or shop.owner_id != user.id:
            return jsonify({'error': 'forbidden', 'message': '無權刪除此圖片'}), 403
    
    try:
        # 刪除文件
        file_path = get_upload_file_path(shop_image.image_path, current_app.root_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        log_update(
            action='delete',
            table_name='shop_image',
            record_id=image_id,
            old_data={'shop_id': shop_id, 'image_path': shop_image.image_path},
            description=f'刪除店鋪圖片'
        )
        
        db.session.delete(shop_image)
        db.session.commit()
        
        return jsonify({'message': '刪除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'刪除圖片失敗: {str(e)}')
        return jsonify({'error': '刪除失敗'}), 500

@shop_images_api_bp.route('/shops/<int:shop_id>/images/reorder', methods=['PUT'])
@role_required('admin', 'store_admin')
def reorder_shop_images(shop_id):
    """重新排序店鋪圖片"""
    from app.utils.decorators import get_current_user
    user = get_current_user()
    shop = Shop.query.get_or_404(shop_id)
    
    # 權限檢查：store_admin 只能排序自己店鋪的圖片
    if user.role == 'store_admin':
        if shop.owner_id != user.id:
            return jsonify({'error': 'forbidden', 'message': '無權排序此店鋪的圖片'}), 403
    
    data = request.get_json()
    
    if not data or 'order' not in data:
        return jsonify({'error': '缺少排序數據'}), 400
    
    order_list = data['order']  # [image_id1, image_id2, ...]
    
    try:
        for index, image_id in enumerate(order_list):
            shop_image = ShopImage.query.filter_by(id=image_id, shop_id=shop_id).first()
            if shop_image:
                shop_image.display_order = index + 1
        
        log_update(
            action='update',
            table_name='shop_image',
            record_id=shop_id,
            new_data={'order': order_list},
            description=f'重新排序店鋪圖片: {shop.name}'
        )
        
        db.session.commit()
        
        return jsonify({'message': '排序成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'排序失敗: {str(e)}')
        return jsonify({'error': '排序失敗'}), 500


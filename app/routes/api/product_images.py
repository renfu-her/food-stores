"""
產品圖片 API 路由
"""
import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Product, ProductImage
from app.utils.decorators import login_required, role_required
from app.utils.update_logger import log_update
from app.utils.image_processor import convert_to_webp, allowed_image_file
from app.utils.upload_path import get_upload_file_path
from datetime import datetime

product_images_api_bp = Blueprint('product_images_api', __name__)

@product_images_api_bp.route('/products/<int:product_id>/images', methods=['POST'])
@role_required('admin', 'store_admin')
def upload_product_image(product_id):
    """上傳產品圖片"""
    from app.utils.decorators import get_current_user
    user = get_current_user()
    product = Product.query.get_or_404(product_id)
    
    # 權限檢查：store_admin 只能上傳自己店鋪的產品圖片
    if user.role == 'store_admin':
        from app.models import Shop
        shop = Shop.query.get(product.shop_id)
        if not shop or shop.owner_id != user.id:
            return jsonify({'error': 'forbidden', 'message': '無權上傳此產品的圖片'}), 403
    
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
        filename_base = f"product_{product_id}_{timestamp}"
        
        # 確保目錄存在
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'products')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 轉換為 WebP 並保存
        output_path = os.path.join(upload_dir, filename_base)
        filepath = convert_to_webp(file, output_path, quality=85)
        
        # 獲取實際的文件名（含 .webp 擴展名）
        filename = os.path.basename(filepath)
        
        # 獲取當前最大的 display_order
        max_order = db.session.query(db.func.max(ProductImage.display_order)).filter_by(product_id=product_id).scalar() or 0
        
        # 創建數據庫記錄
        relative_path = f'/uploads/products/{filename}'
        product_image = ProductImage(
            product_id=product_id,
            image_path=relative_path,
            display_order=max_order + 1
        )
        
        db.session.add(product_image)
        db.session.flush()
        
        log_update(
            action='create',
            table_name='product_image',
            record_id=product_image.id,
            new_data={'product_id': product_id, 'image_path': relative_path, 'display_order': product_image.display_order},
            description=f'上傳產品圖片: {product.name}'
        )
        
        db.session.commit()
        
        return jsonify({
            'id': product_image.id,
            'image_path': relative_path,
            'display_order': product_image.display_order,
            'created_at': product_image.created_at.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'上傳圖片失敗: {str(e)}')
        return jsonify({'error': '上傳失敗'}), 500

@product_images_api_bp.route('/products/<int:product_id>/images', methods=['GET'])
def get_product_images(product_id):
    """獲取產品所有圖片"""
    product = Product.query.get_or_404(product_id)
    images = ProductImage.query.filter_by(product_id=product_id).order_by(ProductImage.display_order).all()
    
    return jsonify([{
        'id': img.id,
        'image_path': img.image_path,
        'display_order': img.display_order,
        'created_at': img.created_at.isoformat()
    } for img in images])

@product_images_api_bp.route('/product-images/<int:image_id>', methods=['DELETE'])
@role_required('admin', 'store_admin')
def delete_product_image(image_id):
    """刪除產品圖片"""
    from app.utils.decorators import get_current_user
    user = get_current_user()
    product_image = ProductImage.query.get_or_404(image_id)
    product_id = product_image.product_id
    
    # 權限檢查：store_admin 只能刪除自己店鋪產品的圖片
    if user.role == 'store_admin':
        product = Product.query.get(product_id)
        from app.models import Shop
        shop = Shop.query.get(product.shop_id)
        if not shop or shop.owner_id != user.id:
            return jsonify({'error': 'forbidden', 'message': '無權刪除此圖片'}), 403
    
    try:
        # 刪除文件
        file_path = get_upload_file_path(product_image.image_path, current_app.root_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        log_update(
            action='delete',
            table_name='product_image',
            record_id=image_id,
            old_data={'product_id': product_id, 'image_path': product_image.image_path},
            description=f'刪除產品圖片'
        )
        
        db.session.delete(product_image)
        db.session.commit()
        
        return jsonify({'message': '刪除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'刪除圖片失敗: {str(e)}')
        return jsonify({'error': '刪除失敗'}), 500

@product_images_api_bp.route('/products/<int:product_id>/images/reorder', methods=['PUT'])
@role_required('admin', 'store_admin')
def reorder_product_images(product_id):
    """重新排序產品圖片"""
    from app.utils.decorators import get_current_user
    user = get_current_user()
    product = Product.query.get_or_404(product_id)
    
    # 權限檢查：store_admin 只能排序自己店鋪產品的圖片
    if user.role == 'store_admin':
        from app.models import Shop
        shop = Shop.query.get(product.shop_id)
        if not shop or shop.owner_id != user.id:
            return jsonify({'error': 'forbidden', 'message': '無權排序此產品的圖片'}), 403
    
    data = request.get_json()
    
    if not data or 'order' not in data:
        return jsonify({'error': '缺少排序數據'}), 400
    
    order_list = data['order']  # [image_id1, image_id2, ...]
    
    try:
        for index, image_id in enumerate(order_list):
            product_image = ProductImage.query.filter_by(id=image_id, product_id=product_id).first()
            if product_image:
                product_image.display_order = index + 1
        
        log_update(
            action='update',
            table_name='product_image',
            record_id=product_id,
            new_data={'order': order_list},
            description=f'重新排序產品圖片: {product.name}'
        )
        
        db.session.commit()
        
        return jsonify({'message': '排序成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'排序失敗: {str(e)}')
        return jsonify({'error': '排序失敗'}), 500


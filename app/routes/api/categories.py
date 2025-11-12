"""
分類 API 路由
"""
from flask import Blueprint, request, jsonify
from app import db, cache
from app.models import Category, Product
from app.utils.decorators import login_required, role_required
from app.utils.update_logger import log_update

categories_api_bp = Blueprint('categories_api', __name__)

@categories_api_bp.route('', methods=['GET'])
@cache.cached(timeout=600, key_prefix='categories_list')  # 快取10分鐘
def get_categories():
    """獲取所有分類"""
    categories = Category.query.order_by(Category.name).all()
    
    result = []
    for cat in categories:
        product_count = Product.query.filter_by(category_id=cat.id).count()
        result.append({
            'id': cat.id,
            'name': cat.name,
            'description': cat.description,
            'product_count': product_count,
            'created_at': cat.created_at.isoformat() if cat.created_at else None,
            'updated_at': cat.updated_at.isoformat() if cat.updated_at else None
        })
    
    return jsonify(result)

@categories_api_bp.route('/<int:category_id>', methods=['GET'])
@cache.cached(timeout=600)  # 快取10分鐘，自動包含category_id參數
def get_category(category_id):
    """獲取單個分類"""
    category = Category.query.get_or_404(category_id)
    product_count = Product.query.filter_by(category_id=category.id).count()
    
    return jsonify({
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'product_count': product_count,
        'created_at': category.created_at.isoformat() if category.created_at else None,
        'updated_at': category.updated_at.isoformat() if category.updated_at else None
    })

@categories_api_bp.route('', methods=['POST'])
@role_required('admin')
def create_category():
    """新增分類"""
    data = request.get_json()
    
    # 驗證必填欄位
    if not data or not data.get('name'):
        return jsonify({'error': '缺少必填欄位：name'}), 400
    
    # 檢查名稱是否已存在
    existing = Category.query.filter_by(name=data['name']).first()
    if existing:
        return jsonify({'error': '分類名稱已存在'}), 400
    
    try:
        category = Category(
            name=data['name'],
            description=data.get('description', '')
        )
        
        db.session.add(category)
        db.session.flush()
        
        log_update(
            action='create',
            table_name='category',
            record_id=category.id,
            new_data={'name': category.name, 'description': category.description},
            description=f'新增分類: {category.name}'
        )
        
        db.session.commit()
        
        # 清除相關快取
        cache.delete('categories_list')
        
        return jsonify({
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'created_at': category.created_at.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@categories_api_bp.route('/<int:category_id>', methods=['PUT'])
@role_required('admin')
def update_category(category_id):
    """更新分類"""
    category = Category.query.get_or_404(category_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '缺少請求數據'}), 400
    
    # 檢查名稱是否與其他分類重複
    if 'name' in data and data['name'] != category.name:
        existing = Category.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': '分類名稱已存在'}), 400
    
    try:
        old_data = {
            'name': category.name,
            'description': category.description
        }
        
        if 'name' in data:
            category.name = data['name']
        if 'description' in data:
            category.description = data['description']
        
        new_data = {
            'name': category.name,
            'description': category.description
        }
        
        log_update(
            action='update',
            table_name='category',
            record_id=category.id,
            old_data=old_data,
            new_data=new_data,
            description=f'更新分類: {category.name}'
        )
        
        db.session.commit()
        
        # 清除相關快取
        cache.delete('categories_list')
        cache.delete_memoized(get_category, category_id)
        
        return jsonify({
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'updated_at': category.updated_at.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@categories_api_bp.route('/<int:category_id>', methods=['DELETE'])
@role_required('admin')
def delete_category(category_id):
    """刪除分類"""
    category = Category.query.get_or_404(category_id)
    
    # 檢查是否有產品使用此分類
    product_count = Product.query.filter_by(category_id=category.id).count()
    if product_count > 0:
        return jsonify({
            'error': '無法刪除',
            'message': f'此分類下有 {product_count} 個產品，請先將產品移至其他分類或刪除產品'
        }), 400
    
    try:
        log_update(
            action='delete',
            table_name='category',
            record_id=category.id,
            old_data={'name': category.name, 'description': category.description},
            description=f'刪除分類: {category.name}'
        )
        
        db.session.delete(category)
        db.session.commit()
        
        # 清除相關快取
        cache.delete('categories_list')
        cache.delete_memoized(get_category, category_id)
        
        return jsonify({'message': '刪除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


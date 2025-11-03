"""
產品API路由
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import Product, Shop, Category, Topping, product_topping
from app.utils.decorators import login_required, get_current_user
from app.utils.validators import validate_decimal, validate_integer
from sqlalchemy import and_

products_api_bp = Blueprint('products_api', __name__)

@products_api_bp.route('/', methods=['GET'])
def get_products():
    """獲取產品列表（公開，可篩選，預設只顯示is_active=true的產品）"""
    try:
        shop_id = request.args.get('shop_id', type=int)
        category_id = request.args.get('category_id', type=int)
        is_active = request.args.get('is_active', type=str)
        
        query = Product.query
        
        # 篩選條件
        if shop_id:
            query = query.filter_by(shop_id=shop_id)
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        # 預設只顯示啟動的產品，除非明確指定
        if is_active is None:
            query = query.filter_by(is_active=True)
        elif is_active.lower() == 'false':
            query = query.filter_by(is_active=False)
        
        products = query.all()
        
        products_data = []
        for product in products:
            # 獲取產品的toppings
            toppings_data = []
            for topping in product.toppings:
                # 獲取產品特定的topping價格
                result = db.session.query(product_topping.c.price).filter(
                    and_(
                        product_topping.c.product_id == product.id,
                        product_topping.c.topping_id == topping.id
                    )
                ).scalar()
                topping_price = float(result) if result is not None else float(topping.price)
                
                toppings_data.append({
                    'id': topping.id,
                    'name': topping.name,
                    'price': topping_price,
                    'display_price': "FREE" if topping_price == 0 else f"${topping_price:.2f}"
                })
            
            products_data.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'shop_id': product.shop_id,
                'category_id': product.category_id,
                'category_name': product.category.name if product.category else None,
                'unit_price': float(product.unit_price),
                'discounted_price': float(product.discounted_price) if product.discounted_price else None,
                'stock_quantity': product.stock_quantity,
                'is_active': product.is_active,
                'toppings': toppings_data,
                'created_at': product.created_at.isoformat() if product.created_at else None
            })
        
        return jsonify({
            'products': products_data,
            'total': len(products_data)
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'internal_error',
            'message': '獲取產品列表失敗',
            'details': {'error': str(e)}
        }), 500

@products_api_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """獲取產品詳情（公開）"""
    try:
        product = Product.query.get_or_404(product_id)
        
        # 獲取產品的toppings
        toppings_data = []
        for topping in product.toppings:
            result = db.session.query(product_topping.c.price).filter(
                and_(
                    product_topping.c.product_id == product.id,
                    product_topping.c.topping_id == topping.id
                )
            ).scalar()
            topping_price = float(result) if result is not None else float(topping.price)
            
            toppings_data.append({
                'id': topping.id,
                'name': topping.name,
                'price': topping_price,
                'display_price': "FREE" if topping_price == 0 else f"${topping_price:.2f}"
            })
        
        return jsonify({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'shop_id': product.shop_id,
            'shop_name': product.shop.name if product.shop else None,
            'category_id': product.category_id,
            'category_name': product.category.name if product.category else None,
            'unit_price': float(product.unit_price),
            'discounted_price': float(product.discounted_price) if product.discounted_price else None,
            'stock_quantity': product.stock_quantity,
            'is_active': product.is_active,
            'toppings': toppings_data,
            'created_at': product.created_at.isoformat() if product.created_at else None,
            'updated_at': product.updated_at.isoformat() if product.updated_at else None
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'not_found',
            'message': '產品不存在',
            'details': {}
        }), 404

@products_api_bp.route('/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    """更新產品（僅店鋪擁有者或管理員）"""
    try:
        user = get_current_user()
        product = Product.query.get_or_404(product_id)
        shop = Shop.query.get_or_404(product.shop_id)
        
        # 權限檢查
        if user.role != 'admin' and shop.owner_id != user.id:
            return jsonify({
                'error': 'forbidden',
                'message': '無權修改此產品',
                'details': {}
            }), 403
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'bad_request',
                'message': '請求資料不能為空',
                'details': {}
            }), 400
        
        # 更新欄位
        if 'name' in data:
            product.name = data['name'].strip()
        if 'description' in data:
            product.description = data['description'].strip()
        if 'category_id' in data:
            category = Category.query.get(data['category_id'])
            if not category:
                return jsonify({
                    'error': 'validation_error',
                    'message': '分類不存在',
                    'details': {}
                }), 400
            product.category_id = data['category_id']
        if 'unit_price' in data:
            is_valid, price_value, error_msg = validate_decimal(data['unit_price'], '單價')
            if not is_valid:
                return jsonify({
                    'error': 'validation_error',
                    'message': error_msg,
                    'details': {}
                }), 400
            product.unit_price = price_value
        if 'discounted_price' in data:
            if data['discounted_price'] is None:
                product.discounted_price = None
            else:
                is_valid, price_value, error_msg = validate_decimal(data['discounted_price'], '折扣價')
                if not is_valid:
                    return jsonify({
                        'error': 'validation_error',
                        'message': error_msg,
                        'details': {}
                    }), 400
                product.discounted_price = price_value
        if 'stock_quantity' in data:
            is_valid, stock_value, error_msg = validate_integer(data['stock_quantity'], '库存數量', min_value=0)
            if not is_valid:
                return jsonify({
                    'error': 'validation_error',
                    'message': error_msg,
                    'details': {}
                }), 400
            product.stock_quantity = stock_value
        if 'is_active' in data:
            product.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        # 觸發SocketIO事件 - 产品更新
        from app import socketio
        socketio.emit('product_updated', {
            'product_id': product.id,
            'shop_id': product.shop_id,
            'unit_price': float(product.unit_price),
            'stock_quantity': product.stock_quantity,
            'is_active': product.is_active
        }, namespace='/public')
        
        return jsonify({
            'message': '產品更新成功',
            'product': {
                'id': product.id,
                'name': product.name,
                'unit_price': float(product.unit_price),
                'stock_quantity': product.stock_quantity,
                'is_active': product.is_active
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '更新產品失敗',
            'details': {'error': str(e)}
        }), 500

@products_api_bp.route('/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    """刪除產品（僅店鋪擁有者或管理員）"""
    try:
        user = get_current_user()
        product = Product.query.get_or_404(product_id)
        shop = Shop.query.get_or_404(product.shop_id)
        
        # 權限檢查
        if user.role != 'admin' and shop.owner_id != user.id:
            return jsonify({
                'error': 'forbidden',
                'message': '無權刪除此產品',
                'details': {}
            }), 403
        
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({
            'message': '產品刪除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '刪除產品失敗',
            'details': {'error': str(e)}
        }), 500

@products_api_bp.route('/<int:product_id>/stock', methods=['PUT'])
@login_required
def update_stock(product_id):
    """更新庫存（僅店鋪擁有者或管理員，觸發SocketIO更新）"""
    try:
        user = get_current_user()
        product = Product.query.get_or_404(product_id)
        shop = Shop.query.get_or_404(product.shop_id)
        
        # 權限檢查
        if user.role != 'admin' and shop.owner_id != user.id:
            return jsonify({
                'error': 'forbidden',
                'message': '無權修改此產品库存',
                'details': {}
            }), 403
        
        data = request.get_json()
        if not data or 'stock_quantity' not in data:
            return jsonify({
                'error': 'bad_request',
                'message': '缺少stock_quantity參數',
                'details': {}
            }), 400
        
        # 驗證庫存數量
        is_valid, stock_value, error_msg = validate_integer(
            data['stock_quantity'], '库存數量', min_value=0
        )
        if not is_valid:
            return jsonify({
                'error': 'validation_error',
                'message': error_msg,
                'details': {}
            }), 400
        
        product.stock_quantity = stock_value
        db.session.commit()
        
        # 觸發SocketIO事件
        from app import socketio
        socketio.emit('product_updated', {
            'product_id': product.id,
            'shop_id': product.shop_id,
            'unit_price': float(product.unit_price),
            'stock_quantity': product.stock_quantity,
            'is_active': product.is_active
        }, namespace='/public')
        
        return jsonify({
            'message': '庫存更新成功',
            'product': {
                'id': product.id,
                'stock_quantity': product.stock_quantity
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '更新庫存失敗',
            'details': {'error': str(e)}
        }), 500

@products_api_bp.route('/<int:product_id>/status', methods=['PUT'])
@login_required
def update_status(product_id):
    """更新產品上架/下架狀態（is_active，僅店鋪擁有者或管理員，觸發SocketIO更新）"""
    try:
        user = get_current_user()
        product = Product.query.get_or_404(product_id)
        shop = Shop.query.get_or_404(product.shop_id)
        
        # 權限檢查
        if user.role != 'admin' and shop.owner_id != user.id:
            return jsonify({
                'error': 'forbidden',
                'message': '無權修改此產品状态',
                'details': {}
            }), 403
        
        data = request.get_json()
        if not data or 'is_active' not in data:
            return jsonify({
                'error': 'bad_request',
                'message': '缺少is_active參數',
                'details': {}
            }), 400
        
        old_status = product.is_active
        product.is_active = bool(data['is_active'])
        db.session.commit()
        
        # 觸發SocketIO事件
        from app import socketio
        socketio.emit('product_status_changed', {
            'product_id': product.id,
            'shop_id': product.shop_id,
            'is_active': product.is_active,
            'old_status': old_status
        }, namespace='/public')
        
        socketio.emit('product_updated', {
            'product_id': product.id,
            'shop_id': product.shop_id,
            'unit_price': float(product.unit_price),
            'stock_quantity': product.stock_quantity,
            'is_active': product.is_active
        }, namespace='/public')
        
        return jsonify({
            'message': '產品狀態更新成功',
            'product': {
                'id': product.id,
                'is_active': product.is_active
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '更新產品狀態失敗',
            'details': {'error': str(e)}
        }), 500

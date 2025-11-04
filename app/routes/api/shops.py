"""
店鋪API路由
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import Shop, User, Topping
from app.utils.decorators import login_required, role_required, shop_access_required, get_current_user
from app.utils.validators import validate_integer, validate_decimal
from app.utils.update_logger import log_update

shops_api_bp = Blueprint('shops_api', __name__)

@shops_api_bp.route('/', methods=['GET'])
def get_shops():
    """獲取店鋪列表（公開）"""
    try:
        shops = Shop.query.filter_by(status='active').all()
        
        shops_data = []
        for shop in shops:
            shops_data.append({
                'id': shop.id,
                'name': shop.name,
                'description': shop.description,
                'owner_id': shop.owner_id,
                'max_toppings_per_order': shop.max_toppings_per_order,
                'status': shop.status,
                'created_at': shop.created_at.isoformat() if shop.created_at else None
            })
        
        return jsonify({
            'shops': shops_data,
            'total': len(shops_data)
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'internal_error',
            'message': '獲取店鋪列表失敗',
            'details': {'error': str(e)}
        }), 500

@shops_api_bp.route('/<int:shop_id>', methods=['GET'])
def get_shop(shop_id):
    """獲取店鋪詳情（公開）"""
    try:
        shop = Shop.query.get_or_404(shop_id)
        
        return jsonify({
            'id': shop.id,
            'name': shop.name,
            'description': shop.description,
            'owner_id': shop.owner_id,
            'max_toppings_per_order': shop.max_toppings_per_order,
            'status': shop.status,
            'created_at': shop.created_at.isoformat() if shop.created_at else None,
            'updated_at': shop.updated_at.isoformat() if shop.updated_at else None
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'not_found',
            'message': '店鋪不存在',
            'details': {}
        }), 404

@shops_api_bp.route('/', methods=['POST'])
@role_required('store_admin', 'admin')
def create_shop():
    """建立店鋪（需要store_admin或admin角色）"""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'bad_request',
                'message': '請求資料不能為空',
                'details': {}
            }), 400
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        max_toppings = data.get('max_toppings_per_order', 5)
        
        if not name:
            return jsonify({
                'error': 'validation_error',
                'message': '店鋪名稱不能為空',
                'details': {}
            }), 400
        
        # 驗證max_toppings
        is_valid, max_toppings_value, error_msg = validate_integer(
            max_toppings, '最大toppings數量', min_value=0, max_value=20
        )
        if not is_valid:
            return jsonify({
                'error': 'validation_error',
                'message': error_msg,
                'details': {}
            }), 400
        
        # 如果使用者是store_admin，檢查是否已有店鋪
        if user.role == 'store_admin':
            existing_shop = Shop.query.filter_by(owner_id=user.id).first()
            if existing_shop:
                return jsonify({
                    'error': 'validation_error',
                    'message': '您已經擁有一個店鋪',
                    'details': {}
                }), 400
        
        # 建立店鋪
        owner_id = data.get('owner_id', user.id) if user.role == 'admin' else user.id
        
        new_shop = Shop(
            name=name,
            description=description,
            owner_id=owner_id,
            max_toppings_per_order=max_toppings_value,
            status='active'
        )
        
        db.session.add(new_shop)
        db.session.flush()  # 獲取店鋪ID
        
        # 如果有 toppings 數據，批量創建
        toppings_data = data.get('toppings', [])
        if toppings_data:
            for topping_item in toppings_data:
                topping = Topping(
                    shop_id=new_shop.id,
                    name=topping_item.get('name', '').strip(),
                    price=topping_item.get('price', 0),
                    is_active=topping_item.get('is_active', True)
                )
                db.session.add(topping)
        
        # 記錄日誌
        log_update(
            action='create',
            table_name='shop',
            record_id=new_shop.id,
            new_data={
                'name': new_shop.name,
                'description': new_shop.description,
                'owner_id': new_shop.owner_id,
                'max_toppings_per_order': new_shop.max_toppings_per_order,
                'status': new_shop.status,
                'toppings_count': len(toppings_data)
            },
            description=f'新增店鋪: {new_shop.name}（含 {len(toppings_data)} 個配料）'
        )
        
        db.session.commit()
        
        return jsonify({
            'message': '店鋪建立成功',
            'shop': {
                'id': new_shop.id,
                'name': new_shop.name,
                'description': new_shop.description,
                'owner_id': new_shop.owner_id,
                'max_toppings_per_order': new_shop.max_toppings_per_order,
                'status': new_shop.status
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '建立店鋪失败',
            'details': {'error': str(e)}
        }), 500

@shops_api_bp.route('/<int:shop_id>', methods=['PUT'])
@login_required
def update_shop(shop_id):
    """更新店鋪（僅店鋪擁有者或管理員）"""
    try:
        user = get_current_user()
        shop = Shop.query.get_or_404(shop_id)
        
        # 權限檢查
        if user.role != 'admin' and shop.owner_id != user.id:
            return jsonify({
                'error': 'forbidden',
                'message': '無權修改此店鋪',
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
            shop.name = data['name'].strip()
        if 'description' in data:
            shop.description = data['description'].strip()
        if 'max_toppings_per_order' in data:
            is_valid, max_toppings_value, error_msg = validate_integer(
                data['max_toppings_per_order'], '最大toppings數量', min_value=0, max_value=20
            )
            if not is_valid:
                return jsonify({
                    'error': 'validation_error',
                    'message': error_msg,
                    'details': {}
                }), 400
            shop.max_toppings_per_order = max_toppings_value
        if 'status' in data and user.role == 'admin':
            shop.status = data['status']
        
        # 記錄日誌
        log_update(
            action='update',
            table_name='shop',
            record_id=shop.id,
            new_data={
                'name': shop.name,
                'description': shop.description,
                'max_toppings_per_order': shop.max_toppings_per_order,
                'status': shop.status
            },
            description=f'更新店鋪: {shop.name}'
        )
        
        db.session.commit()
        
        return jsonify({
            'message': '店鋪更新成功',
            'shop': {
                'id': shop.id,
                'name': shop.name,
                'description': shop.description,
                'owner_id': shop.owner_id,
                'max_toppings_per_order': shop.max_toppings_per_order,
                'status': shop.status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '更新店鋪失敗',
            'details': {'error': str(e)}
        }), 500

@shops_api_bp.route('/<int:shop_id>', methods=['DELETE'])
@login_required
def delete_shop(shop_id):
    """刪除店鋪（僅店鋪擁有者或管理員）"""
    try:
        user = get_current_user()
        shop = Shop.query.get_or_404(shop_id)
        
        # 權限檢查
        if user.role != 'admin' and shop.owner_id != user.id:
            return jsonify({
                'error': 'forbidden',
                'message': '無權刪除此店鋪',
                'details': {}
            }), 403
        
        # 保存店鋪信息用於日誌
        shop_data = {
            'name': shop.name,
            'description': shop.description,
            'owner_id': shop.owner_id
        }
        
        # 記錄日誌
        log_update(
            action='delete',
            table_name='shop',
            record_id=shop.id,
            old_data=shop_data,
            description=f'刪除店鋪: {shop.name}'
        )
        
        db.session.delete(shop)
        db.session.commit()
        
        return jsonify({
            'message': '店鋪刪除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '刪除店鋪失敗',
            'details': {'error': str(e)}
        }), 500

@shops_api_bp.route('/<int:shop_id>/toppings', methods=['GET'])
def get_shop_toppings(shop_id):
    """獲取店鋪toppings列表（僅顯示is_active=true的）"""
    try:
        shop = Shop.query.get_or_404(shop_id)
        
        # 只返回啟動的toppings
        toppings = Topping.query.filter_by(shop_id=shop_id, is_active=True).all()
        
        toppings_data = []
        for topping in toppings:
            toppings_data.append({
                'id': topping.id,
                'name': topping.name,
                'price': float(topping.price),
                'display_price': topping.get_display_price(),
                'is_active': topping.is_active
            })
        
        return jsonify({
            'toppings': toppings_data,
            'total': len(toppings_data)
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'internal_error',
            'message': '獲取toppings列表失敗',
            'details': {'error': str(e)}
        }), 500

@shops_api_bp.route('/<int:shop_id>/toppings', methods=['POST'])
@login_required
def create_topping(shop_id):
    """添加topping（僅店鋪擁有者或管理員）"""
    try:
        user = get_current_user()
        shop = Shop.query.get_or_404(shop_id)
        
        # 權限檢查
        if user.role != 'admin' and shop.owner_id != user.id:
            return jsonify({
                'error': 'forbidden',
                'message': '無權為此店鋪添加配料',
                'details': {}
            }), 403
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'bad_request',
                'message': '請求資料不能為空',
                'details': {}
            }), 400
        
        name = data.get('name', '').strip()
        price = data.get('price', 0)
        is_active = data.get('is_active', True)
        
        if not name:
            return jsonify({
                'error': 'validation_error',
                'message': '配料名稱不能為空',
                'details': {}
            }), 400
        
        # 驗證價格
        is_valid, price_value, error_msg = validate_decimal(price, '價格')
        if not is_valid:
            return jsonify({
                'error': 'validation_error',
                'message': error_msg,
                'details': {}
            }), 400
        
        # 建立topping
        new_topping = Topping(
            name=name,
            shop_id=shop_id,
            price=price_value,
            is_active=is_active
        )
        
        db.session.add(new_topping)
        db.session.commit()
        
        return jsonify({
            'message': '配料建立成功',
            'topping': {
                'id': new_topping.id,
                'name': new_topping.name,
                'price': float(new_topping.price),
                'display_price': new_topping.get_display_price(),
                'is_active': new_topping.is_active
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '建立配料失敗',
            'details': {'error': str(e)}
        }), 500

@shops_api_bp.route('/<int:shop_id>/products', methods=['POST'])
@login_required
def create_product(shop_id):
    """建立產品（僅店鋪擁有者或管理員）"""
    try:
        from app.models import Product, Category
        from app.utils.validators import validate_decimal, validate_integer
        
        user = get_current_user()
        shop = Shop.query.get_or_404(shop_id)
        
        # 權限檢查
        if user.role != 'admin' and shop.owner_id != user.id:
            return jsonify({
                'error': 'forbidden',
                'message': '無權為此店鋪建立產品',
                'details': {}
            }), 403
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'bad_request',
                'message': '請求資料不能為空',
                'details': {}
            }), 400
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        category_id = data.get('category_id')
        unit_price = data.get('unit_price')
        discounted_price = data.get('discounted_price')
        stock_quantity = data.get('stock_quantity', 0)
        is_active = data.get('is_active', True)
        
        # 驗證必填欄位
        if not name:
            return jsonify({
                'error': 'validation_error',
                'message': '產品名稱不能為空',
                'details': {}
            }), 400
        
        if not category_id:
            return jsonify({
                'error': 'validation_error',
                'message': '產品分類不能為空',
                'details': {}
            }), 400
        
        # 驗證分類是否存在
        category = Category.query.get(category_id)
        if not category:
            return jsonify({
                'error': 'validation_error',
                'message': '分類不存在',
                'details': {}
            }), 400
        
        # 驗證價格
        if unit_price is None:
            return jsonify({
                'error': 'validation_error',
                'message': '單價不能為空',
                'details': {}
            }), 400
        
        is_valid, price_value, error_msg = validate_decimal(unit_price, '單價')
        if not is_valid:
            return jsonify({
                'error': 'validation_error',
                'message': error_msg,
                'details': {}
            }), 400
        
        discounted_price_value = None
        if discounted_price is not None:
            is_valid, discounted_price_value, error_msg = validate_decimal(discounted_price, '折扣價')
            if not is_valid:
                return jsonify({
                    'error': 'validation_error',
                    'message': error_msg,
                    'details': {}
                }), 400
        
        # 驗證庫存
        is_valid, stock_value, error_msg = validate_integer(stock_quantity, '库存數量', min_value=0)
        if not is_valid:
            return jsonify({
                'error': 'validation_error',
                'message': error_msg,
                'details': {}
            }), 400
        
        # 创建产品
        new_product = Product(
            name=name,
            description=description,
            shop_id=shop_id,
            category_id=category_id,
            unit_price=price_value,
            discounted_price=discounted_price_value,
            stock_quantity=stock_value,
            is_active=is_active
        )
        
        db.session.add(new_product)
        
        # 處理toppings關聯
        if 'toppings' in data and isinstance(data['toppings'], list):
            from app.models import Topping, product_topping
            for topping_data in data['toppings']:
                topping_id = topping_data.get('topping_id')
                topping_price = topping_data.get('price')
                
                if topping_id:
                    topping = Topping.query.get(topping_id)
                    if topping and topping.shop_id == shop_id:
                        # 如果指定了價格，使用指定價格；否则使用topping的默认價格
                        if topping_price is not None:
                            is_valid, price_val, _ = validate_decimal(topping_price, 'topping價格')
                            if is_valid:
                                # 插入到關聯表
                                db.session.execute(
                                    product_topping.insert().values(
                                        product_id=new_product.id,
                                        topping_id=topping_id,
                                        price=price_val
                                    )
                                )
                            else:
                                db.session.execute(
                                    product_topping.insert().values(
                                        product_id=new_product.id,
                                        topping_id=topping_id,
                                        price=topping.price
                                    )
                                )
        
        db.session.commit()
        
        return jsonify({
            'message': '產品建立成功',
            'product': {
                'id': new_product.id,
                'name': new_product.name,
                'shop_id': new_product.shop_id,
                'category_id': new_product.category_id,
                'unit_price': float(new_product.unit_price),
                'stock_quantity': new_product.stock_quantity,
                'is_active': new_product.is_active
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '建立產品失敗',
            'details': {'error': str(e)}
        }), 500

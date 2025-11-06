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

@shops_api_bp.route('/my-shops', methods=['GET'])
@login_required
def get_my_shops():
    """獲取當前用戶的店鋪列表（排除已軟刪除）"""
    try:
        user = get_current_user()
        
        # 獲取用戶的店鋪（排除已刪除）
        if user.role == 'admin':
            # 管理員可以看到所有未刪除的店鋪
            shops = Shop.query.filter(Shop.deleted_at.is_(None)).all()
        elif user.role == 'store_admin':
            # 店主只能看到自己未刪除的店鋪
            shops = Shop.query.filter_by(owner_id=user.id).filter(Shop.deleted_at.is_(None)).all()
        else:
            # 普通用戶沒有店鋪
            shops = []
        
        shops_data = []
        for shop in shops:
            shops_data.append({
                'id': shop.id,
                'name': shop.name,
                'description': shop.description,
                'shop_order_id': shop.shop_order_id,
                'owner_id': shop.owner_id,
                'max_toppings_per_order': shop.max_toppings_per_order,
                'status': shop.status
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

@shops_api_bp.route('/', methods=['GET'])
def get_shops():
    """獲取店鋪列表（公開，排除已刪除）"""
    try:
        shops = Shop.query.filter_by(status='active').filter(Shop.deleted_at.is_(None)).all()
        
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
        
        # 获取并验证 shop_order_id（必填）
        shop_order_id = data.get('shop_order_id', '').strip().upper()
        if not shop_order_id:
            return jsonify({
                'error': 'validation_error',
                'message': '商店訂單ID不能為空',
                'details': {}
            }), 400
        
        # 验证 shop_order_id 格式（2-20位大写字母和数字）
        import re
        if not re.match(r'^[A-Z0-9]{2,20}$', shop_order_id):
            return jsonify({
                'error': 'validation_error',
                'message': '商店訂單ID格式錯誤（只能使用大寫字母和數字，2-20個字符）',
                'details': {}
            }), 400
        
        # 检查 shop_order_id 是否重复
        existing_shop_with_order_id = Shop.query.filter_by(shop_order_id=shop_order_id).filter(Shop.deleted_at.is_(None)).first()
        if existing_shop_with_order_id:
            return jsonify({
                'error': 'validation_error',
                'message': f'商店訂單ID "{shop_order_id}" 已被使用，請使用其他ID',
                'details': {}
            }), 400
        
        # 建立店鋪（支持多店鋪，移除单店铺限制）
        owner_id = data.get('owner_id', user.id) if user.role == 'admin' else user.id
        
        new_shop = Shop(
            name=name,
            description=description,
            shop_order_id=shop_order_id,
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
        
        # 更新商店訂單ID（必填，驗證唯一性）
        if 'shop_order_id' in data:
            new_shop_order_id = data['shop_order_id']
            
            # 必填驗證
            if not new_shop_order_id or not new_shop_order_id.strip():
                return jsonify({
                    'error': 'validation_error',
                    'message': '商店訂單ID不能為空',
                    'details': {}
                }), 400
            
            new_shop_order_id = new_shop_order_id.strip().upper()
            
            # 驗證格式（只能包含大寫字母和數字）
            import re
            if not re.match(r'^[A-Z0-9]+$', new_shop_order_id):
                return jsonify({
                    'error': 'validation_error',
                    'message': '商店訂單ID只能包含大寫字母和數字',
                    'details': {}
                }), 400
            
            # 驗證長度
            if len(new_shop_order_id) < 2:
                return jsonify({
                    'error': 'validation_error',
                    'message': '商店訂單ID長度至少2個字符',
                    'details': {}
                }), 400
            
            if len(new_shop_order_id) > 20:
                return jsonify({
                    'error': 'validation_error',
                    'message': '商店訂單ID長度不能超過20個字符',
                    'details': {}
                }), 400
            
            # 驗證唯一性（排除自己）
            existing = Shop.query.filter(
                Shop.shop_order_id == new_shop_order_id,
                Shop.id != shop_id
            ).first()
            if existing:
                return jsonify({
                    'error': 'validation_error',
                    'message': f'商店訂單ID "{new_shop_order_id}" 已被店鋪 "{existing.name}" 使用',
                    'details': {}
                }), 400
            
            shop.shop_order_id = new_shop_order_id
        
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
        
        # 更新回饋金比例
        if 'points_rate' in data:
            is_valid, points_rate_value, error_msg = validate_integer(
                data['points_rate'], '回饋金比例', min_value=1, max_value=1000
            )
            if not is_valid:
                return jsonify({
                    'error': 'validation_error',
                    'message': error_msg,
                    'details': {}
                }), 400
            shop.points_rate = points_rate_value
        
        # 更新桌號設置
        if 'qrcode_enabled' in data:
            shop.qrcode_enabled = bool(data['qrcode_enabled'])
        
        if 'max_tables' in data:
            is_valid, max_tables_value, error_msg = validate_integer(
                data['max_tables'], '最大桌號數量', min_value=0, max_value=200
            )
            if not is_valid:
                return jsonify({
                    'error': 'validation_error',
                    'message': error_msg,
                    'details': {}
                }), 400
            shop.max_tables = max_tables_value
        
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
                'points_rate': shop.points_rate,
                'qrcode_enabled': shop.qrcode_enabled,
                'max_tables': shop.max_tables,
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
                'points_rate': shop.points_rate,
                'qrcode_enabled': shop.qrcode_enabled,
                'max_tables': shop.max_tables,
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
    """刪除店鋪（軟刪除 - 僅店鋪擁有者或管理員）"""
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
        
        # 檢查是否已刪除
        if shop.deleted_at:
            return jsonify({
                'error': 'bad_request',
                'message': '店鋪已被刪除',
                'details': {}
            }), 400
        
        # 保存店鋪信息用於日誌
        shop_data = {
            'name': shop.name,
            'description': shop.description,
            'owner_id': shop.owner_id
        }
        
        # 軟刪除：設置 deleted_at 時間戳
        from datetime import datetime
        shop.deleted_at = datetime.utcnow()
        
        # 記錄日誌
        log_update(
            action='soft_delete',
            table_name='shop',
            record_id=shop.id,
            old_data=shop_data,
            description=f'軟刪除店鋪: {shop.name}'
        )
        
        db.session.commit()
        
        return jsonify({
            'message': '店鋪刪除成功（可在後台恢復）'
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

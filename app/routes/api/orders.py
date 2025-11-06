"""
訂單API路由
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import Order, OrderItem, Product, Shop, Topping, Table, OrderPayment, PaymentMethod, order_item_topping
from app.routes.api.points import create_point_transaction
from app.utils.decorators import login_required, get_current_user, role_required
from app.utils.validators import validate_integer, validate_order_status, validate_topping_count
from app.utils.update_logger import log_update
from app.utils.order_number import generate_order_number
from decimal import Decimal
from sqlalchemy import and_

orders_api_bp = Blueprint('orders_api', __name__)

@orders_api_bp.route('/', methods=['GET'])
@login_required
def get_orders():
    """獲取訂單列表（使用者自己的訂單，或店鋪擁有者的訂單，或管理員查看所有）"""
    try:
        user = get_current_user()
        shop_id = request.args.get('shop_id', type=int)
        
        query = Order.query
        
        # 根據角色篩選訂單
        if user.role == 'admin':
            # 管理員可以查看所有訂單
            if shop_id:
                query = query.filter_by(shop_id=shop_id)
        elif user.role == 'store_admin':
            # 店鋪管理者只能查看自己店鋪的訂單
            shops = Shop.query.filter_by(owner_id=user.id).all()
            shop_ids = [s.id for s in shops]
            query = query.filter(Order.shop_id.in_(shop_ids))
            if shop_id:
                query = query.filter_by(shop_id=shop_id)
        else:
            # 普通使用者只能查看自己的訂單
            query = query.filter_by(user_id=user.id)
        
        orders = query.order_by(Order.created_at.desc()).all()
        
        orders_data = []
        for order in orders:
            items_data = []
            for item in order.items:
                toppings_data = []
                for topping in item.toppings:
                    # 獲取訂單項中topping的價格
                    result = db.session.query(order_item_topping.c.price).filter(
                        and_(
                            order_item_topping.c.order_item_id == item.id,
                            order_item_topping.c.topping_id == topping.id
                        )
                    ).scalar()
                    topping_price = float(result) if result is not None else float(topping.price)
                    
                    toppings_data.append({
                        'id': topping.id,
                        'name': topping.name,
                        'price': topping_price,
                        'display_price': "FREE" if topping_price == 0 else f"${topping_price:.2f}"
                    })
                
                items_data.append({
                    'id': item.id,
                    'product_id': item.product_id,
                    'product_name': item.product.name if item.product else None,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'toppings': toppings_data
                })
            
            orders_data.append({
                'id': order.id,
                'user_id': order.user_id,
                'shop_id': order.shop_id,
                'shop_name': order.shop.name if order.shop else None,
                'status': order.status,
                'total_price': float(order.total_price),
                'items': items_data,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'updated_at': order.updated_at.isoformat() if order.updated_at else None
            })
        
        return jsonify({
            'orders': orders_data,
            'total': len(orders_data)
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'internal_error',
            'message': '獲取訂單列表失敗',
            'details': {'error': str(e)}
        }), 500

@orders_api_bp.route('/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    """獲取訂單詳情"""
    try:
        user = get_current_user()
        order = Order.query.get_or_404(order_id)
        
        # 權限檢查
        if user.role == 'customer' and order.user_id != user.id:
            return jsonify({
                'error': 'forbidden',
                'message': '無權查看此訂單',
                'details': {}
            }), 403
        
        if user.role == 'store_admin':
            shop = Shop.query.get(order.shop_id)
            if not shop or shop.owner_id != user.id:
                return jsonify({
                    'error': 'forbidden',
                    'message': '無權查看此訂單',
                    'details': {}
                }), 403
        
        items_data = []
        for item in order.items:
            toppings_data = []
            for topping in item.toppings:
                result = db.session.query(order_item_topping.c.price).filter(
                    and_(
                        order_item_topping.c.order_item_id == item.id,
                        order_item_topping.c.topping_id == topping.id
                    )
                ).scalar()
                topping_price = float(result) if result is not None else float(topping.price)
                
                toppings_data.append({
                    'id': topping.id,
                    'name': topping.name,
                    'price': topping_price,
                    'display_price': "FREE" if topping_price == 0 else f"${topping_price:.2f}"
                })
            
            items_data.append({
                'id': item.id,
                'product_id': item.product_id,
                'product_name': item.product.name if item.product else None,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'toppings': toppings_data
            })
        
        return jsonify({
            'id': order.id,
            'user_id': order.user_id,
            'user_name': order.user.name if order.user else None,
            'shop_id': order.shop_id,
            'shop_name': order.shop.name if order.shop else None,
            'status': order.status,
            'total_price': float(order.total_price),
            'items': items_data,
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'updated_at': order.updated_at.isoformat() if order.updated_at else None
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'internal_error',
            'message': '獲取訂單詳情失败',
            'details': {'error': str(e)}
        }), 500

@orders_api_bp.route('', methods=['POST'])
@login_required
def create_order():
    """建立訂單（需要登入，狀態預設為pending）
    支持兩種模式：
    1. 傳統模式：提供 shop_id 和 items（單店鋪訂單）
    2. 購物車模式：只提供 items，自動按 product.shop_id 分組創建多個訂單
    """
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'bad_request',
                'message': '請求資料不能為空',
                'details': {}
            }), 400
        
        items = data.get('items', [])
        shop_id = data.get('shop_id')  # 可選參數
        
        if not items or not isinstance(items, list):
            return jsonify({
                'error': 'validation_error',
                'message': '訂單項不能為空',
                'details': {}
            }), 400
        
        # 如果沒有提供 shop_id，從商品自動分組
        if not shop_id:
            # 購物車模式：按店鋪分組商品
            shop_groups = {}
            for item_data in items:
                product_id = item_data.get('product_id')
                if not product_id:
                    return jsonify({
                        'error': 'validation_error',
                        'message': '產品ID不能為空',
                        'details': {'item_data': item_data}
                    }), 400
                
                # 獲取產品信息
                product = Product.query.get(product_id)
                if not product:
                    # 列出所有可用產品
                    all_products = Product.query.all()
                    available_ids = [p.id for p in all_products]
                    return jsonify({
                        'error': 'validation_error',
                        'message': f'產品ID {product_id} 不存在',
                        'details': {
                            'requested_id': product_id,
                            'available_product_ids': available_ids
                        }
                    }), 400
                
                # 按店鋪分組
                if product.shop_id not in shop_groups:
                    shop_groups[product.shop_id] = []
                shop_groups[product.shop_id].append(item_data)
            
            # 為每個店鋪創建訂單
            created_orders = []
            for sid, shop_items in shop_groups.items():
                order_data = {
                    'shop_id': sid,
                    'items': shop_items,
                    'recipient_name': data.get('recipient_name'),
                    'recipient_phone': data.get('recipient_phone'),
                    'county': data.get('county'),
                    'district': data.get('district'),
                    'zipcode': data.get('zipcode'),
                    'address': data.get('address'),
                    'delivery_note': data.get('delivery_note'),
                    'payment_method': data.get('payment_method', 'cod')
                }
                order = _create_single_order(user, order_data)
                created_orders.append(order)
            
            return jsonify({
                'message': f'成功建立 {len(created_orders)} 個訂單',
                'orders': [{'order_id': o.id, 'shop_id': o.shop_id, 'total_price': int(o.total_price)} for o in created_orders]
            }), 201
        
        # 傳統模式：單店鋪訂單
        # 驗證店鋪是否存在
        shop = Shop.query.get_or_404(shop_id)
        if shop.status != 'active':
            return jsonify({
                'error': 'validation_error',
                'message': '店鋪不可用',
                'details': {}
            }), 400
        
        # 計算總價並建立訂單項
        total_price = Decimal('0')
        order_items = []
        
        for item_data in items:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity', 1)
            toppings = item_data.get('toppings', [])
            
            if not product_id:
                return jsonify({
                    'error': 'validation_error',
                    'message': '產品ID不能為空',
                    'details': {}
                }), 400
            
            # 驗證產品
            product = Product.query.get(product_id)
            if not product:
                return jsonify({
                    'error': 'validation_error',
                    'message': f'产品ID {product_id} 不存在',
                    'details': {}
                }), 400
            
            if product.shop_id != shop_id:
                return jsonify({
                    'error': 'validation_error',
                    'message': f'产品 {product_id} 不属于此店铺',
                    'details': {}
                }), 400
            
            if not product.is_active:
                return jsonify({
                    'error': 'validation_error',
                    'message': f'产品 {product.name} 已下架',
                    'details': {}
                }), 400
            
            # 驗證庫存
            is_valid, qty_value, error_msg = validate_integer(quantity, '數量', min_value=1)
            if not is_valid:
                return jsonify({
                    'error': 'validation_error',
                    'message': error_msg,
                    'details': {}
                }), 400
            
            if product.stock_quantity < qty_value:
                return jsonify({
                    'error': 'validation_error',
                    'message': f'产品 {product.name} 库存不足',
                    'details': {}
                }), 400
            
            # 验证topping數量
            is_valid, error_msg = validate_topping_count(shop_id, len(toppings))
            if not is_valid:
                return jsonify({
                    'error': 'validation_error',
                    'message': error_msg,
                    'details': {}
                }), 400
            
            # 計算產品價格（使用折扣價如果有）
            unit_price = product.discounted_price if product.discounted_price else product.unit_price
            item_total = unit_price * qty_value
            
            # 添加topping價格
            for topping_id in toppings:
                topping = Topping.query.get(topping_id)
                if not topping or topping.shop_id != shop_id or not topping.is_active:
                    return jsonify({
                        'error': 'validation_error',
                        'message': f'Topping ID {topping_id} 无效',
                        'details': {}
                    }), 400
                
                # 獲取產品特定的topping價格
                from app.models import product_topping
                result = db.session.query(product_topping.c.price).filter(
                    and_(
                        product_topping.c.product_id == product_id,
                        product_topping.c.topping_id == topping_id
                    )
                ).scalar()
                topping_price = Decimal(str(result)) if result is not None else topping.price
                item_total += topping_price
            
            total_price += item_total
            
            # 建立訂單項物件（先不儲存，等訂單建立後再儲存）
            order_item = OrderItem(
                product_id=product_id,
                quantity=qty_value,
                unit_price=unit_price
            )
            order_items.append({
                'order_item': order_item,
                'toppings': toppings
            })
        
        # 建立訂單
        new_order = Order(
            user_id=user.id,
            shop_id=shop_id,
            status='pending',
            total_price=total_price
        )
        
        db.session.add(new_order)
        db.session.flush()  # 獲取訂單ID
        
        # 添加訂單項和toppings
        for item_info in order_items:
            order_item = item_info['order_item']
            order_item.order_id = new_order.id
            db.session.add(order_item)
            db.session.flush()  # 獲取訂單項ID
            
            # 添加toppings關聯
            for topping_id in item_info['toppings']:
                topping = Topping.query.get(topping_id)
                result = db.session.execute(
                    db.select(product_topping.c.price).where(
                        and_(
                            product_topping.c.product_id == order_item.product_id,
                            product_topping.c.topping_id == topping_id
                        )
                    )
                ).scalar()
                topping_price = Decimal(str(result)) if result is not None else topping.price
                
                db.session.execute(
                    order_item_topping.insert().values(
                        order_item_id=order_item.id,
                        topping_id=topping_id,
                        price=topping_price
                    )
                )
            
            # 更新產品庫存
            product = Product.query.get(order_item.product_id)
            product.stock_quantity -= order_item.quantity
        
        db.session.commit()
        
        # 觸發SocketIO事件 - 新訂單通知
        from app import socketio
        # 發送到店鋪頻道（店主可以收到）
        socketio.emit('new_order', {
            'order_id': new_order.id,
            'order_number': new_order.order_number,
            'shop_id': shop_id,
            'user_id': user.id,
            'total_price': float(total_price)
        }, room=f'/shop/{shop_id}')
        
        # 發送到後台管理頻道
        socketio.emit('new_order', {
            'order_id': new_order.id,
            'order_number': new_order.order_number,
            'shop_id': shop_id,
            'user_id': user.id,
            'total_price': float(total_price)
        }, room='/backend')
        
        return jsonify({
            'message': '訂單建立成功',
            'order': {
                'id': new_order.id,
                'shop_id': new_order.shop_id,
                'status': new_order.status,
                'total_price': float(new_order.total_price)
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '建立訂單失败',
            'details': {'error': str(e)}
        }), 500

@orders_api_bp.route('/<int:order_id>/status', methods=['PUT'])
@login_required
def update_order_status(order_id):
    """更新訂單狀態（pending/process/success，僅店鋪擁有者或管理員，觸發SocketIO更新）"""
    try:
        user = get_current_user()
        order = Order.query.get_or_404(order_id)
        shop = Shop.query.get_or_404(order.shop_id)
        
        # 權限檢查
        if user.role != 'admin' and shop.owner_id != user.id:
            return jsonify({
                'error': 'forbidden',
                'message': '無權修改此訂單狀態',
                'details': {}
            }), 403
        
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({
                'error': 'bad_request',
                'message': '缺少status參數',
                'details': {}
            }), 400
        
        new_status = data['status']
        is_valid, error_msg = validate_order_status(new_status)
        if not is_valid:
            return jsonify({
                'error': 'validation_error',
                'message': error_msg,
                'details': {}
            }), 400
        
        old_status = order.status
        order.status = new_status
        db.session.commit()
        
        # 觸發SocketIO事件 - 訂單狀態更新
        from app import socketio
        # 發送到店鋪頻道（店主可以收到）
        socketio.emit('order_updated', {
            'order_id': order.id,
            'status': new_status,
            'old_status': old_status,
            'updated_at': order.updated_at.isoformat() if order.updated_at else None
        }, room=f'/shop/{order.shop_id}')
        
        # 發送到用戶頻道（顧客可以收到）
        socketio.emit('order_updated', {
            'order_id': order.id,
            'status': new_status,
            'old_status': old_status,
            'updated_at': order.updated_at.isoformat() if order.updated_at else None
        }, room=f'/user/{order.user_id}')
        
        # 發送到後台管理頻道
        socketio.emit('order_updated', {
            'order_id': order.id,
            'status': new_status,
            'old_status': old_status,
            'updated_at': order.updated_at.isoformat() if order.updated_at else None
        }, room='/backend')
        
        return jsonify({
            'message': '訂單狀態更新成功',
            'order': {
                'id': order.id,
                'status': order.status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '更新訂單狀態失敗',
            'details': {'error': str(e)}
        }), 500

def _create_single_order(user, data):
    """創建單個訂單的輔助函數
    
    Args:
        user: 當前用戶
        data: 訂單數據，包含 shop_id, items, recipient_name 等
        
    Returns:
        Order: 創建的訂單對象
    """
    shop_id = data.get('shop_id')
    items = data.get('items', [])
    
    # 驗證店鋪
    shop = Shop.query.get(shop_id)
    if not shop or shop.status != 'active':
        raise ValueError(f'店鋪ID {shop_id} 不可用')
    
    # 計算總價並建立訂單項
    total_price = Decimal('0')
    order_items_data = []
    
    for item_data in items:
        product_id = item_data.get('product_id')
        quantity = item_data.get('quantity', 1)
        toppings = item_data.get('toppings', [])
        drink_type = item_data.get('drink_type')  # 'cold', 'hot', or None
        drink_price = item_data.get('drink_price', 0)
        
        # 驗證產品
        product = Product.query.get(product_id)
        if not product:
            raise ValueError(f'產品ID {product_id} 不存在')
        
        if product.shop_id != shop_id:
            raise ValueError(f'產品 {product_id} 不屬於店鋪 {shop_id}')
        
        if not product.is_active:
            raise ValueError(f'產品 {product.name} 已下架')
        
        # 驗證庫存
        is_valid, qty_value, error_msg = validate_integer(quantity, '數量', min_value=1)
        if not is_valid:
            raise ValueError(error_msg)
        
        if product.stock_quantity < qty_value:
            raise ValueError(f'產品 {product.name} 庫存不足')
        
        # 驗證配料數量
        is_valid, error_msg = validate_topping_count(shop_id, len(toppings))
        if not is_valid:
            raise ValueError(error_msg)
        
        # 計算單價
        unit_price = product.discounted_price if product.discounted_price else product.unit_price
        
        # 計算配料價格
        topping_price = Decimal('0')
        topping_instances = []
        for topping_data in toppings:
            topping_id = topping_data.get('topping_id') or topping_data.get('id')
            if topping_id:
                topping = Topping.query.get(topping_id)
                if topping and topping.shop_id == shop_id and topping.is_active:
                    topping_price += topping.price
                    topping_instances.append((topping, topping.price))
        
        # 計算飲品價格
        drink_total_price = Decimal(str(drink_price)) if drink_type and drink_price else Decimal('0')
        
        # 項目總價
        item_unit_price = unit_price + topping_price + drink_total_price
        item_total = item_unit_price * qty_value
        total_price += item_total
        
        # 保存訂單項數據
        order_items_data.append({
            'product': product,
            'quantity': qty_value,
            'unit_price': item_unit_price,
            'toppings': topping_instances,
            'drink_type': drink_type,
            'drink_price': drink_total_price
        })
        
        # 減少庫存
        product.stock_quantity -= qty_value
    
    # 組合完整地址
    county = data.get('county', '')
    district = data.get('district', '')
    zipcode = data.get('zipcode', '')
    address = data.get('address', '')
    full_address = f"{zipcode} {county}{district}{address}".strip()
    
    # 生成訂單編號
    order_number = generate_order_number(shop_id)
    
    # 創建訂單
    order = Order(
        order_number=order_number,
        user_id=user.id,
        shop_id=shop_id,
        total_price=total_price,
        status='pending',
        recipient_name=data.get('recipient_name'),
        recipient_phone=data.get('recipient_phone'),
        recipient_address=full_address,  # 完整地址
        delivery_note=data.get('delivery_note'),
        payment_method=data.get('payment_method', 'cod')
    )
    
    db.session.add(order)
    db.session.flush()
    
    # 更新用戶收貨信息（方便下次自動填充）
    if data.get('recipient_name'):
        user.name = data.get('recipient_name')
    if data.get('recipient_phone'):
        user.phone = data.get('recipient_phone')
    if county:
        user.county = county
    if district:
        user.district = district
    if zipcode:
        user.zipcode = zipcode
    if address:
        user.address = address
    
    # 添加訂單項
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data['product'].id,
            quantity=item_data['quantity'],
            unit_price=item_data['unit_price'],
            drink_type=item_data.get('drink_type'),
            drink_price=item_data.get('drink_price')
        )
        db.session.add(order_item)
        db.session.flush()
        
        # 添加配料關聯
        for topping, topping_price in item_data['toppings']:
            stmt = order_item_topping.insert().values(
                order_item_id=order_item.id,
                topping_id=topping.id,
                price=topping_price
            )
            db.session.execute(stmt)
    
    # 記錄日誌
    log_update(
        action='create',
        table_name='order',
        record_id=order.id,
        new_data={
            'shop_id': order.shop_id,
            'user_id': order.user_id,
            'total_price': float(order.total_price),
            'status': order.status
        },
        description=f'創建訂單: 店鋪 {shop_id}, 用戶 {user.name}, 總價 ${order.total_price}'
    )
    
    # 觸發SocketIO事件
    from app import socketio
    # 發送到店鋪頻道（店主可以收到）
    socketio.emit('new_order', {
        'order_id': order.id,
        'order_number': order.order_number,
        'shop_id': shop_id,
        'user_id': user.id,
        'total_price': float(total_price)
    }, room=f'/shop/{shop_id}')
    
    # 發送到後台管理頻道
    socketio.emit('new_order', {
        'order_id': order.id,
        'order_number': order.order_number,
        'shop_id': shop_id,
        'user_id': user.id,
        'total_price': float(total_price)
    }, room='/backend')
    
    db.session.commit()
    return order

# =========================
# 访客订单和增强结账
# =========================

@orders_api_bp.route('/guest', methods=['POST'])
def create_guest_order():
    """创建访客订单（桌号点餐，无需登入）"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        shop_id = data.get('shop_id')
        table_number = data.get('table_number')
        items = data.get('items', [])
        payment_splits = data.get('payment_splits', [])  # 组合支付
        recipient_info = data.get('recipient_info', {})
        
        if not shop_id or not table_number:
            return jsonify({'error': '缺少店铺ID或桌号'}), 400
        
        if not items:
            return jsonify({'error': '订单项不能为空'}), 400
        
        # 获取店铺
        shop = Shop.query.get(shop_id)
        if not shop:
            return jsonify({'error': '店铺不存在'}), 404
        
        if not shop.qrcode_enabled:
            return jsonify({'error': '此店铺未启用桌号点餐'}), 400
        
        # 获取或创建桌号
        table = Table.query.filter_by(shop_id=shop_id, table_number=table_number).first()
        if not table:
            return jsonify({'error': '桌号不存在'}), 404
        
        # 创建临时用户或使用访客用户（user_id = 1 假设为系统访客账号）
        # 这里简化处理，使用 shop owner 作为订单用户
        guest_user_id = shop.owner_id
        
        # 计算订单总价
        total_price = Decimal('0.00')
        order_items_data = []
        
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            toppings_ids = item.get('toppings', [])
            drink_type = item.get('drink_type')
            
            product = Product.query.get(product_id)
            if not product or product.shop_id != shop_id:
                continue
            
            # 计算单价（使用折扣价或原价）
            if product.discounted_price and product.discounted_price > 0:
                unit_price = product.discounted_price
            else:
                unit_price = product.unit_price
            
            item_total = unit_price * quantity
            
            # 添加饮品价格
            drink_price = Decimal('0.00')
            if drink_type == 'cold' and product.has_cold_drink:
                drink_price = product.cold_drink_price or Decimal('0.00')
            elif drink_type == 'hot' and product.has_hot_drink:
                drink_price = product.hot_drink_price or Decimal('0.00')
            
            item_total += drink_price * quantity
            
            # 处理配料
            toppings_list = []
            for topping_id in toppings_ids:
                topping = Topping.query.get(topping_id)
                if topping and topping.shop_id == shop_id:
                    topping_price = topping.price or Decimal('0.00')
                    toppings_list.append((topping, topping_price))
                    item_total += topping_price * quantity
            
            total_price += item_total
            
            order_items_data.append({
                'product': product,
                'quantity': quantity,
                'unit_price': unit_price,
                'drink_type': drink_type,
                'drink_price': drink_price,
                'toppings': toppings_list
            })
        
        if total_price <= 0:
            return jsonify({'error': '订单总价必须大于0'}), 400
        
        # 生成订单编号
        order_number = generate_order_number(shop_id)
        
        # 获取客户信息（访客提供的）
        customer_name = data.get('customer_name')
        customer_phone = data.get('customer_phone')
        note = data.get('note')
        
        # 创建订单（访客订单）
        order = Order(
            order_number=order_number,
            user_id=guest_user_id,  # 使用店家 owner_id 作为访客订单的用户
            shop_id=shop_id,
            table_id=table.id,  # 记录桌号
            is_guest_order=True,  # 标记为访客订单
            status='pending',
            total_price=total_price,
            points_earned=0,  # 访客订单不赚取回馈金
            points_used=0,  # 访客订单不使用回馈金
            recipient_name=customer_name or '访客',
            recipient_phone=customer_phone,
            recipient_address=f'桌号: {table_number}',  # 用地址栏记录桌号
            delivery_note=note
        )
        
        db.session.add(order)
        db.session.flush()
        
        # 添加订单项
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product'].id,
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                drink_type=item_data.get('drink_type'),
                drink_price=item_data.get('drink_price')
            )
            db.session.add(order_item)
            db.session.flush()
            
            # 添加配料
            for topping, topping_price in item_data['toppings']:
                stmt = order_item_topping.insert().values(
                    order_item_id=order_item.id,
                    topping_id=topping.id,
                    price=topping_price
                )
                db.session.execute(stmt)
        
        # 处理组合支付
        if payment_splits:
            for payment in payment_splits:
                order_payment = OrderPayment(
                    order_id=order.id,
                    payment_method_id=payment['payment_method_id'],
                    amount=Decimal(str(payment['amount'])),
                    status='pending'
                )
                db.session.add(order_payment)
        
        db.session.commit()
        
        # 触发 SocketIO 事件
        from app import socketio
        socketio.emit('new_order', {
            'order_id': order.id,
            'order_number': order.order_number,
            'shop_id': shop_id,
            'table_number': table_number,
            'is_guest_order': True,
            'total_price': float(total_price)
        }, room=f'/shop/{shop_id}')
        
        return jsonify({
            'message': '访客订单创建成功',
            'order_id': order.id,
            'order_number': order.order_number,
            'amount_paid': float(total_price),
            'table_number': table_number,
            'is_guest_order': True
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_api_bp.route('/checkout', methods=['POST'])
@login_required
def checkout_with_points_and_payment():
    """增强结账（支持回馈金使用和组合支付）"""
    try:
        user = get_current_user()
        data = request.get_json()
        
        shop_id = data.get('shop_id')
        items = data.get('items', [])
        points_to_use = data.get('points_to_use', 0)  # 使用的回馈金
        payment_splits = data.get('payment_splits', [])  # 组合支付
        recipient_info = data.get('recipient_info', {})
        
        if not shop_id or not items:
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 获取店铺
        shop = Shop.query.get(shop_id)
        if not shop:
            return jsonify({'error': '店铺不存在'}), 404
        
        # 验证回馈金余额
        if points_to_use > 0:
            if points_to_use > user.points:
                return jsonify({'error': '回馈金余额不足'}), 400
        
        # 计算订单总价
        total_price = Decimal('0.00')
        order_items_data = []
        
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            toppings_ids = item.get('toppings', [])
            drink_type = item.get('drink_type')
            
            product = Product.query.get(product_id)
            if not product or product.shop_id != shop_id:
                continue
            
            # 计算单价
            if product.discounted_price and product.discounted_price > 0:
                unit_price = product.discounted_price
            else:
                unit_price = product.unit_price
            
            item_total = unit_price * quantity
            
            # 添加饮品价格
            drink_price = Decimal('0.00')
            if drink_type == 'cold' and product.has_cold_drink:
                drink_price = product.cold_drink_price or Decimal('0.00')
            elif drink_type == 'hot' and product.has_hot_drink:
                drink_price = product.hot_drink_price or Decimal('0.00')
            
            item_total += drink_price * quantity
            
            # 处理配料
            toppings_list = []
            for topping_id in toppings_ids:
                topping = Topping.query.get(topping_id)
                if topping and topping.shop_id == shop_id:
                    topping_price = topping.price or Decimal('0.00')
                    toppings_list.append((topping, topping_price))
                    item_total += topping_price * quantity
            
            total_price += item_total
            
            order_items_data.append({
                'product': product,
                'quantity': quantity,
                'unit_price': unit_price,
                'drink_type': drink_type,
                'drink_price': drink_price,
                'toppings': toppings_list
            })
        
        if total_price <= 0:
            return jsonify({'error': '订单总价必须大于0'}), 400
        
        # 计算使用回馈金后的应付金额
        points_discount = Decimal(str(points_to_use))  # 1点=1元
        amount_due = total_price - points_discount
        
        if amount_due < 0:
            amount_due = Decimal('0.00')
        
        # 验证组合支付金额
        payment_total = sum(Decimal(str(p['amount'])) for p in payment_splits)
        if payment_total != amount_due:
            return jsonify({'error': f'支付金额不正确。应付：${amount_due}，实付：${payment_total}'}), 400
        
        # 验证至少有一种支付方式
        if not payment_splits:
            return jsonify({'error': '请选择支付方式'}), 400
        
        # 生成订单编号
        order_number = generate_order_number(shop_id)
        
        # 计算本次可赚取的回馈金（基于应付金额，不含回馈金抵扣部分）
        points_rate = shop.points_rate or 30
        points_earned = int(float(amount_due) / points_rate)
        
        # 创建订单
        order = Order(
            order_number=order_number,
            user_id=user.id,
            shop_id=shop_id,
            is_guest_order=False,
            status='pending',
            total_price=total_price,
            points_earned=points_earned,
            points_used=points_to_use,
            recipient_name=recipient_info.get('name') or user.name,
            recipient_phone=recipient_info.get('phone') or user.phone,
            recipient_address=recipient_info.get('address'),
            delivery_note=recipient_info.get('note')
        )
        
        db.session.add(order)
        db.session.flush()
        
        # 添加订单项
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product'].id,
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                drink_type=item_data.get('drink_type'),
                drink_price=item_data.get('drink_price')
            )
            db.session.add(order_item)
            db.session.flush()
            
            # 添加配料
            for topping, topping_price in item_data['toppings']:
                stmt = order_item_topping.insert().values(
                    order_item_id=order_item.id,
                    topping_id=topping.id,
                    price=topping_price
                )
                db.session.execute(stmt)
        
        # 处理组合支付记录
        for payment in payment_splits:
            order_payment = OrderPayment(
                order_id=order.id,
                payment_method_id=payment['payment_method_id'],
                amount=Decimal(str(payment['amount'])),
                status='pending'
            )
            db.session.add(order_payment)
        
        # 处理回馈金使用
        if points_to_use > 0:
            create_point_transaction(
                user_id=user.id,
                transaction_type='use',
                points=-points_to_use,  # 负数表示使用
                order_id=order.id,
                shop_id=shop_id,
                description=f'订单 {order_number} 使用回馈金'
            )
        
        # 处理回馈金赚取
        if points_earned > 0:
            create_point_transaction(
                user_id=user.id,
                transaction_type='earn',
                points=points_earned,
                order_id=order.id,
                shop_id=shop_id,
                description=f'订单 {order_number} 赚取回馈金'
            )
        
        db.session.commit()
        
        # 触发 SocketIO 事件
        from app import socketio
        socketio.emit('new_order', {
            'order_id': order.id,
            'order_number': order.order_number,
            'shop_id': shop_id,
            'user_id': user.id,
            'total_price': float(total_price),
            'points_used': points_to_use,
            'points_earned': points_earned
        }, room=f'/shop/{shop_id}')
        
        return jsonify({
            'message': '订单创建成功',
            'order_id': order.id,
            'order_number': order.order_number,
            'total_price': float(total_price),
            'points_used': points_to_use,
            'points_earned': points_earned,
            'amount_paid': float(amount_due)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

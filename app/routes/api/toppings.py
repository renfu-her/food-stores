"""
Toppings API路由
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import Topping, Shop
from app.utils.decorators import login_required, get_current_user
from app.utils.validators import validate_decimal

toppings_api_bp = Blueprint('toppings_api', __name__)

@toppings_api_bp.route('', methods=['GET'])
def get_toppings():
    """獲取配料列表（公開，可依 shop_id 篩選）"""
    try:
        shop_id = request.args.get('shop_id', type=int)
        is_active = request.args.get('is_active', type=str)
        
        query = Topping.query
        
        # 篩選條件
        if shop_id:
            query = query.filter_by(shop_id=shop_id)
        
        # 篩選啟用狀態
        if is_active == 'true':
            query = query.filter_by(is_active=True)
        elif is_active == 'false':
            query = query.filter_by(is_active=False)
        
        toppings = query.order_by(Topping.name).all()
        
        toppings_data = []
        for topping in toppings:
            toppings_data.append({
                'id': topping.id,
                'name': topping.name,
                'price': int(topping.price),
                'shop_id': topping.shop_id,
                'is_active': topping.is_active,
                'created_at': topping.created_at.isoformat() if topping.created_at else None
            })
        
        return jsonify({
            'toppings': toppings_data,
            'total': len(toppings_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'internal_error',
            'message': '獲取配料列表失敗',
            'details': {'error': str(e)}
        }), 500

@toppings_api_bp.route('/<int:topping_id>', methods=['PUT'])
@login_required
def update_topping(topping_id):
    """更新topping（僅店鋪擁有者或管理員）"""
    try:
        user = get_current_user()
        topping = Topping.query.get_or_404(topping_id)
        shop = Shop.query.get_or_404(topping.shop_id)
        
        # 權限檢查
        if user.role != 'admin' and shop.owner_id != user.id:
            return jsonify({
                'error': 'forbidden',
                'message': '無權修改此配料',
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
            topping.name = data['name'].strip()
        if 'price' in data:
            is_valid, price_value, error_msg = validate_decimal(data['price'], '價格')
            if not is_valid:
                return jsonify({
                    'error': 'validation_error',
                    'message': error_msg,
                    'details': {}
                }), 400
            topping.price = price_value
        if 'is_active' in data:
            topping.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        return jsonify({
            'message': '配料更新成功',
            'topping': {
                'id': topping.id,
                'name': topping.name,
                'price': float(topping.price),
                'display_price': topping.get_display_price(),
                'is_active': topping.is_active
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '更新配料失敗',
            'details': {'error': str(e)}
        }), 500

@toppings_api_bp.route('/<int:topping_id>', methods=['DELETE'])
@login_required
def delete_topping(topping_id):
    """刪除topping（僅店鋪擁有者或管理員）"""
    try:
        user = get_current_user()
        topping = Topping.query.get_or_404(topping_id)
        shop = Shop.query.get_or_404(topping.shop_id)
        
        # 權限檢查
        if user.role != 'admin' and shop.owner_id != user.id:
            return jsonify({
                'error': 'forbidden',
                'message': '無權刪除此配料',
                'details': {}
            }), 403
        
        db.session.delete(topping)
        db.session.commit()
        
        return jsonify({
            'message': '配料刪除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '刪除配料失敗',
            'details': {'error': str(e)}
        }), 500


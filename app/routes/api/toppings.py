"""
Toppings API路由
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import Topping, Shop
from app.utils.decorators import login_required, get_current_user
from app.utils.validators import validate_decimal

toppings_api_bp = Blueprint('toppings_api', __name__)

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
                'message': '無權修改此topping',
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
            'message': 'Topping更新成功',
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
            'message': '更新topping失敗',
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
                'message': '無權刪除此topping',
                'details': {}
            }), 403
        
        db.session.delete(topping)
        db.session.commit()
        
        return jsonify({
            'message': 'Topping刪除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': '刪除topping失敗',
            'details': {'error': str(e)}
        }), 500


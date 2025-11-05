"""
購物車 API 路由
"""
from flask import Blueprint, request, jsonify, session
from app import db
from app.models import Product
from datetime import datetime

cart_api_bp = Blueprint('cart_api', __name__)

def get_cart_from_session():
    """從 session 獲取購物車"""
    if 'cart' not in session:
        session['cart'] = []
    return session['cart']

def save_cart_to_session(cart):
    """保存購物車到 session"""
    session['cart'] = cart
    session.modified = True

@cart_api_bp.route('/add', methods=['POST'])
def add_to_cart():
    """加入購物車（使用 session 存儲）"""
    try:
        data = request.get_json()
        
        if not data or 'product_id' not in data:
            return jsonify({
                'error': 'bad_request',
                'message': '缺少產品 ID'
            }), 400
        
        product_id = data['product_id']
        quantity = data.get('quantity', 1)
        toppings = data.get('toppings', [])
        drink_type = data.get('drink_type')  # 'cold', 'hot', or None
        drink_price = data.get('drink_price', 0)
        
        # 驗證產品
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'error': 'not_found',
                'message': '產品不存在'
            }), 404
        
        # 檢查庫存
        if product.stock_quantity < quantity:
            return jsonify({
                'error': 'insufficient_stock',
                'message': '庫存不足'
            }), 400
        
        # 獲取購物車
        cart = get_cart_from_session()
        
        # 計算配料總價
        toppings_price = sum(t.get('price', 0) for t in toppings)
        
        # 計算飲品價格
        drink_total_price = float(drink_price) if drink_type and drink_price else 0
        
        # 計算單價（產品價格 + 配料價格 + 飲品價格）
        base_price = product.discounted_price if product.discounted_price else product.unit_price
        unit_price = float(base_price) + toppings_price + drink_total_price
        
        # 檢查購物車中是否已有相同產品、配料和飲品組合
        existing_item = None
        topping_ids = sorted([t['id'] for t in toppings])
        
        for item in cart:
            if item['product_id'] == product_id:
                item_topping_ids = sorted([t['id'] for t in item.get('toppings', [])])
                item_drink_type = item.get('drink_type')
                if item_topping_ids == topping_ids and item_drink_type == drink_type:
                    existing_item = item
                    break
        
        if existing_item:
            # 更新數量
            existing_item['quantity'] += quantity
        else:
            # 新增項目
            cart_item = {
                'product_id': product_id,
                'product_name': product.name,
                'quantity': quantity,
                'unit_price': unit_price,
                'toppings': toppings,
                'drink_type': drink_type,
                'drink_price': drink_total_price,
                'added_at': datetime.now().isoformat()
            }
            cart.append(cart_item)
        
        # 保存購物車
        save_cart_to_session(cart)
        
        # 計算購物車總數量
        total_items = sum(item['quantity'] for item in cart)
        
        return jsonify({
            'message': '已加入購物車',
            'cart_count': total_items,
            'cart': cart
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'internal_error',
            'message': '加入購物車失敗',
            'details': {'error': str(e)}
        }), 500

@cart_api_bp.route('', methods=['GET'])
def get_cart():
    """獲取購物車內容"""
    try:
        cart = get_cart_from_session()
        total_items = sum(item['quantity'] for item in cart)
        total_price = sum(item['unit_price'] * item['quantity'] for item in cart)
        
        return jsonify({
            'cart': cart,
            'total_items': total_items,
            'total_price': total_price
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'internal_error',
            'message': '獲取購物車失敗'
        }), 500

@cart_api_bp.route('/update', methods=['PUT'])
def update_cart():
    """更新購物車項目"""
    try:
        data = request.get_json()
        
        if not data or 'product_id' not in data:
            return jsonify({
                'error': 'bad_request',
                'message': '缺少產品 ID'
            }), 400
        
        product_id = data['product_id']
        quantity = data.get('quantity', 1)
        
        cart = get_cart_from_session()
        
        # 查找並更新項目
        for item in cart:
            if item['product_id'] == product_id:
                if quantity <= 0:
                    cart.remove(item)
                else:
                    item['quantity'] = quantity
                break
        
        save_cart_to_session(cart)
        
        return jsonify({
            'message': '購物車已更新',
            'cart': cart
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'internal_error',
            'message': '更新購物車失敗'
        }), 500

@cart_api_bp.route('/remove', methods=['DELETE'])
def remove_from_cart():
    """從購物車移除項目"""
    try:
        data = request.get_json()
        
        if not data or 'product_id' not in data:
            return jsonify({
                'error': 'bad_request',
                'message': '缺少產品 ID'
            }), 400
        
        product_id = data['product_id']
        cart = get_cart_from_session()
        
        # 移除項目
        cart = [item for item in cart if item['product_id'] != product_id]
        
        save_cart_to_session(cart)
        
        return jsonify({
            'message': '已從購物車移除',
            'cart': cart
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'internal_error',
            'message': '移除失敗'
        }), 500

@cart_api_bp.route('/clear', methods=['DELETE'])
def clear_cart():
    """清空購物車"""
    try:
        session['cart'] = []
        session.modified = True
        
        return jsonify({
            'message': '購物車已清空'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'internal_error',
            'message': '清空購物車失敗'
        }), 500


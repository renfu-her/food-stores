"""
回馈金 API
"""
from flask import Blueprint, request, jsonify, session
from app.models import User, PointTransaction, Order, Shop
from app.utils.decorators import login_required, get_current_user
from app import db
from datetime import datetime

points_api_bp = Blueprint('points_api', __name__)

@points_api_bp.route('/users/points', methods=['GET'])
@login_required
def get_user_points():
    """获取当前用户回馈金余额"""
    user = get_current_user()
    
    return jsonify({
        'points': user.points,
        'user_id': user.id,
        'user_name': user.name
    }), 200

@points_api_bp.route('/users/points/transactions', methods=['GET'])
@login_required
def get_point_transactions():
    """获取回馈金交易历史"""
    user = get_current_user()
    
    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 筛选参数
    type_filter = request.args.get('type')  # earn/use/expire
    shop_id = request.args.get('shop_id', type=int)
    
    # 构建查询
    query = PointTransaction.query.filter_by(user_id=user.id)
    
    if type_filter:
        query = query.filter_by(type=type_filter)
    
    if shop_id:
        query = query.filter_by(shop_id=shop_id)
    
    # 按时间倒序
    query = query.order_by(PointTransaction.created_at.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    transactions = []
    for t in pagination.items:
        transaction_data = {
            'id': t.id,
            'type': t.type,
            'points': t.points,
            'balance': t.balance,
            'description': t.description,
            'created_at': t.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'order_id': t.order_id,
            'shop_id': t.shop_id
        }
        
        # 关联订单信息
        if t.order_id:
            order = Order.query.get(t.order_id)
            if order:
                transaction_data['order_number'] = order.order_number
        
        # 关联店铺信息
        if t.shop_id:
            shop = Shop.query.get(t.shop_id)
            if shop:
                transaction_data['shop_name'] = shop.name
        
        transactions.append(transaction_data)
    
    return jsonify({
        'transactions': transactions,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200

@points_api_bp.route('/points/calculate', methods=['POST'])
@login_required
def calculate_points():
    """计算订单可赚取的回馈金"""
    data = request.get_json()
    
    order_total = float(data.get('order_total', 0))
    shop_id = data.get('shop_id')
    
    if not shop_id:
        return jsonify({'error': '缺少店铺ID'}), 400
    
    shop = Shop.query.get(shop_id)
    if not shop:
        return jsonify({'error': '店铺不存在'}), 404
    
    # 计算回馈金（根据店铺设置的比例）
    points_rate = shop.points_rate or 30  # 默认30元=1点
    points_earned = int(order_total / points_rate)
    
    return jsonify({
        'order_total': order_total,
        'points_rate': points_rate,
        'points_earned': points_earned,
        'description': f'每消费 {points_rate} 元可获得 1 点回馈金'
    }), 200

def create_point_transaction(user_id, transaction_type, points, order_id=None, shop_id=None, description=None):
    """
    创建回馈金交易记录（内部函数）
    
    Args:
        user_id: 用户ID
        transaction_type: 交易类型 (earn/use/expire)
        points: 点数（正数=赚取，负数=使用）
        order_id: 关联订单ID（可选）
        shop_id: 关联店铺ID（可选）
        description: 描述（可选）
    
    Returns:
        PointTransaction对象
    """
    user = User.query.get(user_id)
    if not user:
        raise ValueError('用户不存在')
    
    # 如果是使用回馈金，检查余额
    if transaction_type == 'use' and abs(points) > user.points:
        raise ValueError('回馈金余额不足')
    
    # 更新用户余额
    user.points += points
    
    # 创建交易记录
    transaction = PointTransaction(
        user_id=user_id,
        order_id=order_id,
        shop_id=shop_id,
        type=transaction_type,
        points=points,
        balance=user.points,
        description=description
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return transaction


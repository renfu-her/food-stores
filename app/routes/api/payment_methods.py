"""
支付方式 API
"""
from flask import Blueprint, request, jsonify
from app.models import PaymentMethod, ShopPaymentMethod, Shop
from app.utils.decorators import login_required, role_required, get_current_user
from app import db
from datetime import datetime

payment_methods_api_bp = Blueprint('payment_methods_api', __name__)

# =========================
# 系统级管理 (Admin Only)
# =========================

@payment_methods_api_bp.route('/payment-methods', methods=['GET'])
@role_required('admin')
def get_all_payment_methods():
    """获取所有支付方式（系统级）"""
    payment_methods = PaymentMethod.query.order_by(PaymentMethod.display_order).all()
    
    methods_data = []
    for pm in payment_methods:
        methods_data.append({
            'id': pm.id,
            'name': pm.name,
            'code': pm.code,
            'icon': pm.icon,
            'is_active': pm.is_active,
            'display_order': pm.display_order,
            'created_at': pm.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify({
        'payment_methods': methods_data,
        'total': len(methods_data)
    }), 200

@payment_methods_api_bp.route('/payment-methods', methods=['POST'])
@role_required('admin')
def create_payment_method():
    """创建支付方式（系统级）"""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    code = data.get('code', '').strip()
    icon = data.get('icon', '').strip()
    display_order = data.get('display_order', 0)
    
    if not name or not code:
        return jsonify({'error': '名称和代码不能为空'}), 400
    
    # 检查代码是否已存在
    existing = PaymentMethod.query.filter_by(code=code).first()
    if existing:
        return jsonify({'error': '支付方式代码已存在'}), 400
    
    payment_method = PaymentMethod(
        name=name,
        code=code,
        icon=icon,
        display_order=display_order,
        is_active=True
    )
    
    db.session.add(payment_method)
    db.session.commit()
    
    return jsonify({
        'message': '支付方式创建成功',
        'payment_method': {
            'id': payment_method.id,
            'name': payment_method.name,
            'code': payment_method.code,
            'icon': payment_method.icon
        }
    }), 201

@payment_methods_api_bp.route('/payment-methods/<int:method_id>', methods=['PUT'])
@role_required('admin')
def update_payment_method(method_id):
    """更新支付方式（系统级）"""
    payment_method = PaymentMethod.query.get_or_404(method_id)
    data = request.get_json()
    
    # 现金支付不能被禁用
    if payment_method.code == 'cash' and 'is_active' in data and not data['is_active']:
        return jsonify({'error': '现金支付是系统必需的支付方式，不能禁用'}), 400
    
    if 'name' in data:
        payment_method.name = data['name'].strip()
    
    if 'icon' in data:
        payment_method.icon = data['icon'].strip()
    
    if 'display_order' in data:
        payment_method.display_order = data['display_order']
    
    if 'is_active' in data:
        payment_method.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'message': '支付方式更新成功',
        'payment_method': {
            'id': payment_method.id,
            'name': payment_method.name,
            'code': payment_method.code,
            'icon': payment_method.icon,
            'is_active': payment_method.is_active
        }
    }), 200

@payment_methods_api_bp.route('/payment-methods/<int:method_id>', methods=['DELETE'])
@role_required('admin')
def delete_payment_method(method_id):
    """删除支付方式（系统级）"""
    payment_method = PaymentMethod.query.get_or_404(method_id)
    
    # 现金支付不能删除
    if payment_method.code == 'cash':
        return jsonify({'error': '现金支付不能删除'}), 400
    
    db.session.delete(payment_method)
    db.session.commit()
    
    return jsonify({'message': '支付方式删除成功'}), 200

# =========================
# 店家级设置
# =========================

@payment_methods_api_bp.route('/shops/<int:shop_id>/payment-methods', methods=['GET'])
@role_required('admin', 'store_admin')
def get_shop_payment_methods(shop_id):
    """获取店家支付方式设置"""
    user = get_current_user()
    
    # 获取店铺
    shop = Shop.query.get_or_404(shop_id)
    
    # 权限检查
    if user.role == 'store_admin' and shop.owner_id != user.id:
        return jsonify({'error': '无权访问此店铺'}), 403
    
    # 获取所有可用的支付方式
    all_methods = PaymentMethod.query.filter_by(is_active=True).order_by(PaymentMethod.display_order).all()
    
    # 获取店铺已启用的支付方式
    shop_methods = ShopPaymentMethod.query.filter_by(shop_id=shop_id).all()
    enabled_method_ids = {sm.payment_method_id for sm in shop_methods if sm.is_enabled}
    
    methods_data = []
    for pm in all_methods:
        methods_data.append({
            'id': pm.id,
            'name': pm.name,
            'code': pm.code,
            'icon': pm.icon,
            'is_enabled': pm.id in enabled_method_ids,
            'is_required': pm.code == 'cash'  # 现金是必须的
        })
    
    return jsonify({
        'payment_methods': methods_data,
        'total': len(methods_data)
    }), 200

@payment_methods_api_bp.route('/shops/<int:shop_id>/payment-methods', methods=['PUT'])
@role_required('admin', 'store_admin')
def update_shop_payment_methods(shop_id):
    """更新店家支付方式设置"""
    user = get_current_user()
    data = request.get_json()
    
    # 获取店铺
    shop = Shop.query.get_or_404(shop_id)
    
    # 权限检查
    if user.role == 'store_admin' and shop.owner_id != user.id:
        return jsonify({'error': '无权操作此店铺'}), 403
    
    enabled_method_ids = data.get('enabled_method_ids', [])
    
    if not enabled_method_ids:
        return jsonify({'error': '至少需要启用一种支付方式'}), 400
    
    # 确保现金支付被包含
    cash_method = PaymentMethod.query.filter_by(code='cash').first()
    if cash_method and cash_method.id not in enabled_method_ids:
        return jsonify({'error': '现金支付是必需的，不能禁用'}), 400
    
    # 删除所有现有设置
    ShopPaymentMethod.query.filter_by(shop_id=shop_id).delete()
    
    # 创建新设置
    for method_id in enabled_method_ids:
        # 验证支付方式是否存在
        pm = PaymentMethod.query.get(method_id)
        if not pm:
            continue
        
        shop_method = ShopPaymentMethod(
            shop_id=shop_id,
            payment_method_id=method_id,
            is_enabled=True
        )
        db.session.add(shop_method)
    
    db.session.commit()
    
    return jsonify({
        'message': '支付方式设置更新成功',
        'enabled_count': len(enabled_method_ids)
    }), 200

# =========================
# 公开查询（用于前台结账）
# =========================

@payment_methods_api_bp.route('/shops/<int:shop_id>/payment-methods/public', methods=['GET'])
def get_shop_payment_methods_public(shop_id):
    """获取店家启用的支付方式（公开接口，用于前台结账）"""
    shop = Shop.query.get_or_404(shop_id)
    
    # 获取店铺启用的支付方式
    shop_methods = ShopPaymentMethod.query.filter_by(
        shop_id=shop_id,
        is_enabled=True
    ).all()
    
    if not shop_methods:
        # 如果店铺未设置，返回所有可用支付方式
        all_methods = PaymentMethod.query.filter_by(is_active=True).order_by(PaymentMethod.display_order).all()
    else:
        # 返回店铺启用的支付方式
        method_ids = [sm.payment_method_id for sm in shop_methods]
        all_methods = PaymentMethod.query.filter(
            PaymentMethod.id.in_(method_ids),
            PaymentMethod.is_active == True
        ).order_by(PaymentMethod.display_order).all()
    
    methods_data = []
    for pm in all_methods:
        methods_data.append({
            'id': pm.id,
            'name': pm.name,
            'code': pm.code,
            'icon': pm.icon
        })
    
    return jsonify({
        'payment_methods': methods_data,
        'shop_name': shop.name
    }), 200


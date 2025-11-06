"""
訪客路由（不需登入）
"""
from flask import Blueprint, render_template, session, request
from app.models import Shop, Product, Category, Table
from app import db

guest_bp = Blueprint('guest', __name__)

@guest_bp.route('/shop/<int:shop_id>/table/<table_number>')
def order(shop_id, table_number):
    """訪客點餐頁面（掃描桌號 QRCode 進入）"""
    # 獲取店鋪
    shop = Shop.query.filter_by(id=shop_id).filter(Shop.deleted_at.is_(None)).first_or_404()
    
    # 檢查店鋪是否啟用桌號點餐
    if not shop.qrcode_enabled:
        return render_template('guest/error.html', 
                             message='此店鋪未啟用桌號掃碼點餐',
                             shop=shop)
    
    # 獲取桌號
    table = Table.query.filter_by(shop_id=shop_id, table_number=table_number).first()
    if not table:
        return render_template('guest/error.html',
                             message='桌號不存在',
                             shop=shop)
    
    # 更新桌號狀態為使用中
    if table.status == 'available':
        table.status = 'occupied'
        db.session.commit()
    
    # 獲取產品和分類
    products = Product.query.filter_by(shop_id=shop_id, is_active=True).filter(Product.deleted_at.is_(None)).all()
    categories = Category.query.all()
    
    # 序列化產品數據
    products_data = []
    for p in products:
        products_data.append({
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'category_id': p.category_id,
            'unit_price': float(p.unit_price),
            'discounted_price': float(p.discounted_price) if p.discounted_price else None,
            'has_cold_drink': p.has_cold_drink,
            'has_hot_drink': p.has_hot_drink,
            'images': [img.image_path for img in p.images] if p.images else []
        })
    
    categories_data = [{'id': c.id, 'name': c.name} for c in categories]
    
    return render_template('guest/order.html', 
                         shop=shop,
                         table=table,
                         table_number=table_number,
                         products=products_data,
                         categories=categories_data)

@guest_bp.route('/shop/<int:shop_id>/table/<table_number>/cart')
def cart(shop_id, table_number):
    """訪客購物車頁面"""
    # 獲取店鋪和桌號
    shop = Shop.query.filter_by(id=shop_id).filter(Shop.deleted_at.is_(None)).first_or_404()
    table = Table.query.filter_by(shop_id=shop_id, table_number=table_number).first_or_404()
    
    return render_template('guest/cart.html',
                         shop=shop,
                         table=table,
                         table_number=table_number)

@guest_bp.route('/shop/<int:shop_id>/table/<table_number>/checkout')
def checkout(shop_id, table_number):
    """訪客結帳頁面"""
    # 獲取店鋪和桌號
    shop = Shop.query.filter_by(id=shop_id).filter(Shop.deleted_at.is_(None)).first_or_404()
    table = Table.query.filter_by(shop_id=shop_id, table_number=table_number).first_or_404()
    
    # 獲取支付方式
    from app.models import PaymentMethod, ShopPaymentMethod
    enabled_methods = db.session.query(PaymentMethod)\
        .join(ShopPaymentMethod, PaymentMethod.id == ShopPaymentMethod.payment_method_id)\
        .filter(ShopPaymentMethod.shop_id == shop_id, 
                ShopPaymentMethod.is_enabled == True, 
                PaymentMethod.is_active == True)\
        .order_by(PaymentMethod.display_order)\
        .all()
    
    methods_data = []
    for pm in enabled_methods:
        methods_data.append({
            'id': pm.id,
            'name': pm.name,
            'code': pm.code,
            'icon': pm.icon
        })
    
    return render_template('guest/checkout.html',
                         shop=shop,
                         table=table,
                         table_number=table_number,
                         payment_methods=methods_data)



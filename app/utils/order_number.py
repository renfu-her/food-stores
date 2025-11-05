"""
订单编号生成工具
"""
from datetime import datetime
from app.models import Order, Shop, SystemSetting
from app import db


def generate_order_number(shop_id):
    """
    生成订单编号
    
    格式：前缀 + 商店编码 + Ymd + 流水号
    例如：ORDERSHOP0120251106 0001
    
    Args:
        shop_id: 店铺 ID
        
    Returns:
        str: 订单编号
    """
    # 获取店铺
    shop = Shop.query.get(shop_id)
    if not shop:
        raise ValueError(f'店铺 ID {shop_id} 不存在')
    
    # 从系统设置获取订单前缀
    order_prefix = SystemSetting.get('order_prefix', 'ORDER')
    
    # 获取商店订单ID（优先使用 shop_order_id，如果没有则使用 ID 补零）
    shop_order_code = shop.shop_order_id
    if not shop_order_code:
        shop_order_code = str(shop_id).zfill(2)
    
    # 获取当前日期（Ymd格式）
    today = datetime.now()
    date_str = today.strftime('%Y%m%d')
    
    # 获取今天该店铺的订单数量（用于生成流水号）
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # 查询今天该店铺的订单数量
    today_order_count = Order.query.filter(
        Order.shop_id == shop_id,
        Order.created_at >= today_start,
        Order.created_at <= today_end
    ).count()
    
    # 流水号（从 00001 开始，5位数）
    sequence = str(today_order_count + 1).zfill(5)
    
    # 组合订单编号
    order_number = f"{order_prefix}{shop_order_code}{date_str}{sequence}"
    
    # 检查是否已存在（理论上不应该存在）
    existing = Order.query.filter_by(order_number=order_number).first()
    if existing:
        # 如果存在，递增流水号
        sequence = str(today_order_count + 2).zfill(5)
        order_number = f"{order_prefix}{shop_order_code}{date_str}{sequence}"
    
    return order_number


def init_default_settings():
    """
    初始化默认系统设置
    """
    default_settings = [
        # 訂單設定
        {
            'key': 'order_prefix',
            'value': 'ORDER',
            'type': 'text',
            'description': '訂單編號前綴',
            'category': 'order'
        },
        
        # 郵件設定
        {
            'key': 'mail_mailer',
            'value': 'smtp',
            'type': 'text',
            'description': '郵件驅動',
            'category': 'email'
        },
        {
            'key': 'mail_host',
            'value': 'smtp.gmail.com',
            'type': 'text',
            'description': 'SMTP 主機',
            'category': 'email'
        },
        {
            'key': 'mail_port',
            'value': '587',
            'type': 'number',
            'description': 'SMTP 端口',
            'category': 'email'
        },
        {
            'key': 'mail_username',
            'value': '',
            'type': 'text',
            'description': 'SMTP 用戶名',
            'category': 'email'
        },
        {
            'key': 'mail_password',
            'value': '',
            'type': 'text',
            'description': 'SMTP 密碼',
            'category': 'email'
        },
        {
            'key': 'mail_encryption',
            'value': 'tls',
            'type': 'text',
            'description': '加密方式 (tls/ssl)',
            'category': 'email'
        },
        {
            'key': 'mail_from_address',
            'value': '',
            'type': 'text',
            'description': '發件人郵箱',
            'category': 'email'
        },
        {
            'key': 'mail_from_name',
            'value': 'Food Stores',
            'type': 'text',
            'description': '發件人名稱',
            'category': 'email'
        },
    ]
    
    for setting_data in default_settings:
        existing = SystemSetting.query.filter_by(setting_key=setting_data['key']).first()
        if not existing:
            setting = SystemSetting(
                setting_key=setting_data['key'],
                setting_value=setting_data['value'],
                setting_type=setting_data['type'],
                description=setting_data['description'],
                category=setting_data['category']
            )
            db.session.add(setting)
    
    db.session.commit()
    print('✅ 系統設定初始化完成')


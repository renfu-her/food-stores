"""
資料驗證工具
"""
from decimal import Decimal, InvalidOperation
from app.models import Shop, Product, Order

def validate_topping_count(shop_id, topping_count):
    """
    验证topping數量是否超过店铺限制
    
    Args:
        shop_id: 店鋪ID
        topping_count: topping數量
        
    Returns:
        tuple: (is_valid, error_message)
    """
    shop = Shop.query.get(shop_id)
    if not shop:
        return False, "店鋪不存在"
    
    if topping_count > shop.max_toppings_per_order:
        return False, f"topping數量不能超过{shop.max_toppings_per_order}個"
    
    return True, None

def validate_decimal(value, field_name="價格"):
    """
    驗證Decimal值
    
    Args:
        value: 要驗證的值
        field_name: 欄位名稱
        
    Returns:
        tuple: (is_valid, decimal_value, error_message)
    """
    try:
        if value is None:
            return False, None, f"{field_name}不能為空"
        
        if isinstance(value, str):
            decimal_value = Decimal(value)
        elif isinstance(value, (int, float)):
            decimal_value = Decimal(str(value))
        elif isinstance(value, Decimal):
            decimal_value = value
        else:
            return False, None, f"{field_name}格式錯誤"
        
        if decimal_value < 0:
            return False, None, f"{field_name}不能為負數"
        
        return True, decimal_value, None
    except (InvalidOperation, ValueError, TypeError):
        return False, None, f"{field_name}格式錯誤"

def validate_integer(value, field_name="數量", min_value=0, max_value=None):
    """
    驗證整數值
    
    Args:
        value: 要驗證的值
        field_name: 欄位名稱
        min_value: 最小值
        max_value: 最大值
        
    Returns:
        tuple: (is_valid, integer_value, error_message)
    """
    try:
        if value is None:
            return False, None, f"{field_name}不能為空"
        
        integer_value = int(value)
        
        if integer_value < min_value:
            return False, None, f"{field_name}不能小于{min_value}"
        
        if max_value is not None and integer_value > max_value:
            return False, None, f"{field_name}不能大于{max_value}"
        
        return True, integer_value, None
    except (ValueError, TypeError):
        return False, None, f"{field_name}必須是整數"

def validate_order_status(status):
    """
    驗證訂單狀態
    
    Args:
        status: 訂單狀態
        
    Returns:
        tuple: (is_valid, error_message)
    """
    valid_statuses = ['pending', 'process', 'success']
    if status not in valid_statuses:
        return False, f"訂單狀態必须是以下之一: {', '.join(valid_statuses)}"
    return True, None

def validate_email(email):
    """
    驗證郵箱格式
    
    Args:
        email: 郵箱地址
        
    Returns:
        tuple: (is_valid, error_message)
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not email or not re.match(pattern, email):
        return False, "郵箱格式不正確"
    return True, None


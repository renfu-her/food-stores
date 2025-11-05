"""
密码强度验证工具
"""
import re

def check_password_strength(password):
    """
    检查密码强度
    
    Args:
        password: 密码字符串
        
    Returns:
        tuple: (strength_level, score, message)
            strength_level: 'low', 'middle', 'high'
            score: 0-100 的分数
            message: 强度描述
    """
    if not password:
        return 'low', 0, '密碼不能為空'
    
    length = len(password)
    score = 0
    
    # 长度评分 (0-40分)
    if length >= 12:
        score += 40
    elif length >= 10:
        score += 30
    elif length >= 8:
        score += 20
    elif length >= 6:
        score += 10
    else:
        score += 0
    
    # 包含小写字母 (0-15分)
    if re.search(r'[a-z]', password):
        score += 15
    
    # 包含大写字母 (0-15分)
    if re.search(r'[A-Z]', password):
        score += 15
    
    # 包含数字 (0-15分)
    if re.search(r'\d', password):
        score += 15
    
    # 包含特殊字符 (0-15分)
    if re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        score += 15
    
    # 判断强度级别
    if score >= 70:
        return 'high', score, '強密碼'
    elif score >= 45:
        return 'middle', score, '中等密碼'
    else:
        return 'low', score, '弱密碼'


def validate_password_strength(password, min_strength='middle'):
    """
    验证密码是否满足最低强度要求
    
    Args:
        password: 密码字符串
        min_strength: 最低强度要求 ('low', 'middle', 'high')
        
    Returns:
        tuple: (is_valid, error_message)
    """
    strength_levels = {'low': 0, 'middle': 1, 'high': 2}
    
    strength, score, message = check_password_strength(password)
    
    if strength_levels.get(strength, 0) < strength_levels.get(min_strength, 1):
        requirements = []
        
        if min_strength == 'middle':
            requirements = [
                '密碼長度至少 8 個字符',
                '包含大小寫字母',
                '包含數字'
            ]
        elif min_strength == 'high':
            requirements = [
                '密碼長度至少 10 個字符',
                '包含大小寫字母',
                '包含數字',
                '包含特殊字符'
            ]
        
        return False, f'密碼強度不足（當前：{message}），需要滿足：' + '、'.join(requirements)
    
    return True, ''


def get_password_strength_details(password):
    """
    获取密码强度详细信息（供前端显示）
    
    Args:
        password: 密码字符串
        
    Returns:
        dict: 包含 strength, score, message, requirements 的字典
    """
    strength, score, message = check_password_strength(password)
    
    requirements = {
        'length': len(password) >= 8,
        'lowercase': bool(re.search(r'[a-z]', password)),
        'uppercase': bool(re.search(r'[A-Z]', password)),
        'number': bool(re.search(r'\d', password)),
        'special': bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password))
    }
    
    return {
        'strength': strength,
        'score': score,
        'message': message,
        'requirements': requirements
    }


"""
密碼驗證工具
"""
import re

def validate_password_strength(password):
    """
    驗證密碼強度
    
    規則：
    - 至少8個字符
    - 至少1個大寫字母
    - 至少1個小寫字母
    - 至少1個數字
    - 至少1個特殊符號
    
    Returns:
        tuple: (is_valid, strength, message)
        - is_valid: bool - 是否通過驗證（middle 或 high）
        - strength: str - 強度等級 (low/middle/high)
        - message: str - 提示信息
    """
    if not password:
        return False, 'low', '密碼不能為空'
    
    # 檢查長度
    if len(password) < 8:
        return False, 'low', '密碼長度至少需要 8 個字符'
    
    # 計分系統
    score = 0
    checks = {
        'length': False,
        'uppercase': False,
        'lowercase': False,
        'digit': False,
        'special': False
    }
    
    # 1. 長度檢查
    if len(password) >= 8:
        checks['length'] = True
        score += 20
    if len(password) >= 12:
        score += 10
    if len(password) >= 16:
        score += 10
    
    # 2. 大寫字母
    if re.search(r'[A-Z]', password):
        checks['uppercase'] = True
        score += 15
        if len(re.findall(r'[A-Z]', password)) >= 2:
            score += 5
    
    # 3. 小寫字母
    if re.search(r'[a-z]', password):
        checks['lowercase'] = True
        score += 15
        if len(re.findall(r'[a-z]', password)) >= 2:
            score += 5
    
    # 4. 數字
    if re.search(r'\d', password):
        checks['digit'] = True
        score += 15
        if len(re.findall(r'\d', password)) >= 2:
            score += 5
    
    # 5. 特殊符號
    if re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]', password):
        checks['special'] = True
        score += 15
        if len(re.findall(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]', password)) >= 2:
            score += 10
    
    # 檢查必要條件
    required_checks = ['length', 'uppercase', 'lowercase', 'digit', 'special']
    missing = [k for k in required_checks if not checks[k]]
    
    if missing:
        missing_text = {
            'length': '長度不足（需8字符以上）',
            'uppercase': '缺少大寫字母',
            'lowercase': '缺少小寫字母',
            'digit': '缺少數字',
            'special': '缺少特殊符號（!@#$%^&*等）'
        }
        messages = [missing_text[k] for k in missing]
        return False, 'low', '密碼強度不足：' + '、'.join(messages)
    
    # 判斷強度等級
    if score >= 80:
        strength = 'high'
        is_valid = True
        message = '密碼強度：高'
    elif score >= 60:
        strength = 'middle'
        is_valid = True
        message = '密碼強度：中（可接受）'
    else:
        strength = 'low'
        is_valid = False
        message = '密碼強度：低（不建議使用）'
    
    return is_valid, strength, message

def get_password_requirements():
    """
    獲取密碼要求說明
    """
    return {
        'min_length': 8,
        'requirements': [
            '至少 8 個字符',
            '至少 1 個大寫字母 (A-Z)',
            '至少 1 個小寫字母 (a-z)',
            '至少 1 個數字 (0-9)',
            '至少 1 個特殊符號 (!@#$%^&* 等)'
        ],
        'strength_levels': {
            'low': '低（不可接受）',
            'middle': '中（可接受）',
            'high': '高（推薦）'
        }
    }


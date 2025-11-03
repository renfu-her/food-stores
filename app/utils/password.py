"""
Laravel相容的密碼雜湊工具
使用bcrypt庫實現與Laravel相容的密碼雜湊格式
"""
import bcrypt

def hash_password(password: str) -> str:
    """
    使用Laravel相容的方式加密密碼
    
    Args:
        password: 明文密碼
        
    Returns:
        Laravel格式的密码哈希字符串（$2y$...）
    """
    # 生成bcrypt雜湊
    salt = bcrypt.gensalt(rounds=12, prefix=b'2y')  # Laravel使用$2y$前缀
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password: str, password_hash: str) -> bool:
    """
    驗證密碼是否匹配雜湊值
    
    Args:
        password: 明文密碼
        password_hash: 儲存的密碼雜湊值
        
    Returns:
        bool: 密碼是否匹配
    """
    try:
        # bcrypt.checkpw会自动处理$2y$前缀
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


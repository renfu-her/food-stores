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
        Laravel格式的密碼雜湊字串（$2y$...）
    """
    # 生成bcrypt雜湊（使用$2a$前綴，因為bcrypt庫不支持$2y$）
    salt = bcrypt.gensalt(rounds=12, prefix=b'2a')
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    # 將$2a$替換為$2y$以匹配Laravel格式
    hashed_str = hashed.decode('utf-8')
    return hashed_str.replace('$2a$', '$2y$')

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
        # 如果密碼雜湊使用$2y$前綴，先替換為$2a$（bcrypt庫需要）
        password_hash = password_hash.replace('$2y$', '$2a$')
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


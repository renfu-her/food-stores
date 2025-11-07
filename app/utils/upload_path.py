"""
上傳文件路徑輔助函數
統一處理 uploads 目錄路徑（優先使用根目錄的 uploads，否則使用 public/uploads）
"""
import os

def get_upload_folder(root_path=None):
    """
    獲取上傳文件夾路徑
    
    Args:
        root_path: Flask app.root_path（可選）
    
    Returns:
        上傳文件夾的絕對路徑
    """
    if root_path:
        # 使用 Flask app.root_path（相對於 app/ 目錄）
        BASE_DIR = os.path.dirname(root_path)  # app/ 的父目錄 = 專案根目錄
    else:
        # 使用當前文件位置計算（用於非 Flask 上下文）
        # 從 app/utils/upload_path.py 計算
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    uploads_dir = os.path.join(BASE_DIR, 'uploads')
    uploads_dir_public = os.path.join(BASE_DIR, 'public', 'uploads')
    
    # 優先使用根目錄的 uploads，否則使用 public/uploads（向後兼容）
    return uploads_dir if os.path.exists(uploads_dir) else uploads_dir_public

def get_upload_file_path(relative_path, root_path=None):
    """
    根據相對路徑獲取文件的絕對路徑
    
    Args:
        relative_path: 相對路徑，如 '/uploads/shops/xxx.jpg' 或 'uploads/shops/xxx.jpg'
        root_path: Flask app.root_path（可選）
    
    Returns:
        文件的絕對路徑
    """
    # 移除前導斜線
    clean_path = relative_path.lstrip('/')
    
    # 移除 'uploads/' 前綴（如果有的話）
    if clean_path.startswith('uploads/'):
        clean_path = clean_path[8:]  # 移除 'uploads/' (8個字符)
    
    upload_folder = get_upload_folder(root_path)
    return os.path.join(upload_folder, clean_path)


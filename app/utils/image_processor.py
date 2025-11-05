"""
圖片處理工具
將上傳的圖片轉換為 WebP 格式以節省空間
"""
import os
from PIL import Image
from werkzeug.datastructures import FileStorage
from flask import current_app
from datetime import datetime
import io

def convert_to_webp(file, output_path, quality=85, max_width=1920, max_height=1920):
    """
    將上傳的圖片轉換為 WebP 格式
    
    Args:
        file: FileStorage 對象或文件路徑
        output_path: 輸出文件路徑（不含擴展名）
        quality: WebP 質量 (1-100)，默認 85
        max_width: 最大寬度，超過則等比例縮放
        max_height: 最大高度，超過則等比例縮放
    
    Returns:
        str: 保存的文件完整路徑（含 .webp 擴展名）
    """
    try:
        # 打開圖片
        if isinstance(file, FileStorage):
            # 從上傳的文件讀取
            img = Image.open(file.stream)
        else:
            # 從文件路徑讀取
            img = Image.open(file)
        
        # 轉換 RGBA 模式為 RGB（WebP 支持透明度，但某些情況下轉換更安全）
        if img.mode in ('RGBA', 'LA', 'P'):
            # 創建白色背景
            background = Image.new('RGB', img.size, (255, 255, 255))
            # 如果有透明通道，將其合成到白色背景上
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1])  # 使用 alpha 通道作為遮罩
                img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 等比例縮放（如果圖片太大）
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            current_app.logger.info(f'圖片已縮放至: {img.width}x{img.height}')
        
        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 生成 WebP 文件名
        webp_path = f"{output_path}.webp"
        
        # 保存為 WebP 格式
        img.save(webp_path, 'WEBP', quality=quality, method=6)
        
        # 獲取文件大小信息
        file_size = os.path.getsize(webp_path)
        current_app.logger.info(f'圖片已轉換為 WebP: {webp_path} ({file_size / 1024:.2f} KB)')
        
        return webp_path
        
    except Exception as e:
        current_app.logger.error(f'圖片轉換失敗: {str(e)}')
        raise


def allowed_image_file(filename):
    """
    檢查文件是否為允許的圖片格式
    支持：jpg, jpeg, png, gif, bmp, webp
    """
    if not filename or '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
    
    return ext in allowed_extensions


def get_image_info(file):
    """
    獲取圖片基本信息
    
    Returns:
        dict: {'width': int, 'height': int, 'format': str, 'mode': str}
    """
    try:
        img = Image.open(file.stream if isinstance(file, FileStorage) else file)
        return {
            'width': img.width,
            'height': img.height,
            'format': img.format,
            'mode': img.mode
        }
    except Exception as e:
        current_app.logger.error(f'獲取圖片信息失敗: {str(e)}')
        return None


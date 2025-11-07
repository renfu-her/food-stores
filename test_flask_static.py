#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
測試 Flask 靜態文件功能
"""

from app import create_app
from app.config import Config
import os

def test_flask_static():
    """測試 Flask 靜態文件配置"""
    print("\n" + "="*60)
    print("測試 Flask 靜態文件功能")
    print("="*60 + "\n")
    
    app = create_app(Config)
    
    # 1. 檢查配置
    print("1. Flask 靜態文件配置：")
    print(f"   static_folder: {app.static_folder}")
    print(f"   static_url_path: {app.static_url_path}")
    
    # 2. 檢查目錄是否存在
    print("\n2. 檢查靜態文件目錄：")
    if os.path.exists(app.static_folder):
        print(f"   ✓ 目錄存在: {app.static_folder}")
    else:
        print(f"   ✗ 目錄不存在: {app.static_folder}")
        return False
    
    # 3. 測試 URL 生成
    print("\n3. 測試 URL 生成：")
    with app.app_context():
        from flask import url_for
        
        try:
            style_url = url_for('static', filename='css/style.css')
            backend_url = url_for('static', filename='css/backend.css')
            js_url = url_for('static', filename='js/socketio_client.js')
            
            print(f"   ✓ style.css: {style_url}")
            print(f"   ✓ backend.css: {backend_url}")
            print(f"   ✓ socketio_client.js: {js_url}")
        except Exception as e:
            print(f"   ✗ URL 生成失敗: {e}")
            return False
    
    # 4. 檢查文件是否存在
    print("\n4. 檢查靜態文件：")
    files = [
        'css/style.css',
        'css/backend.css',
        'js/socketio_client.js'
    ]
    
    all_exist = True
    for f in files:
        full_path = os.path.join(app.static_folder, f)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"   ✓ {f} ({size:,} bytes)")
        else:
            print(f"   ✗ {f} (不存在)")
            all_exist = False
    
    # 5. 測試 Flask 路由
    print("\n5. 測試 Flask 靜態文件路由：")
    print("   啟動 Flask 後，訪問以下 URL 應該能正常載入：")
    print(f"   http://localhost:5000/static/css/style.css")
    print(f"   http://localhost:5000/static/css/backend.css")
    print(f"   http://localhost:5000/static/js/socketio_client.js")
    
    print("\n" + "="*60)
    
    if all_exist:
        print("✓ Flask 靜態文件配置正確！")
        print("\n提示：")
        print("- Flask 會自動處理 /static/ 路徑的請求")
        print("- 不需要 Nginx 也可以正常工作")
        print("- 如果使用 Nginx，可以讓 Flask 處理靜態文件（只配置反向代理）")
        print("- 或讓 Nginx 處理靜態文件（效能更好）")
    else:
        print("✗ 發現問題：部分靜態文件不存在")
        print("\n解決方案：")
        print("1. 確保文件已上傳到正式主機")
        print("2. 檢查文件路徑是否正確")
        print("3. 設置正確的文件權限")
    
    print("="*60 + "\n")
    
    return all_exist

if __name__ == '__main__':
    import sys
    success = test_flask_static()
    sys.exit(0 if success else 1)


#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
檢查靜態文件是否存在
"""

import os
import sys

def check_static_files():
    """檢查靜態文件"""
    print("\n" + "="*60)
    print("檢查靜態文件")
    print("="*60 + "\n")
    
    # 靜態文件路徑
    static_base = 'public/static'
    
    required_files = [
        'css/style.css',
        'css/backend.css',
        'js/socketio_client.js'
    ]
    
    missing_files = []
    existing_files = []
    
    print("檢查必要靜態文件：\n")
    
    for file_path in required_files:
        full_path = os.path.join(static_base, file_path)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"✓ {file_path} ({size:,} bytes)")
            existing_files.append(file_path)
        else:
            print(f"✗ {file_path} (不存在)")
            missing_files.append(file_path)
    
    print("\n" + "="*60)
    
    if missing_files:
        print("✗ 發現缺失文件：")
        for f in missing_files:
            print(f"  - {f}")
        
        print("\n解決方案：")
        print("="*60)
        print("1. 確保已上傳所有靜態文件到正式主機")
        print("2. 檢查文件權限：")
        print("   chmod -R 755 public/static")
        print("3. 檢查 Nginx/Apache 配置（見下方）")
        return False
    else:
        print("✓ 所有靜態文件都存在")
        
        # 檢查 Flask 配置
        print("\n檢查 Flask 靜態文件配置：")
        try:
            from app import create_app
            from app.config import Config
            
            app = create_app(Config)
            static_folder = app.static_folder
            print(f"✓ Flask static_folder: {static_folder}")
            
            if os.path.exists(static_folder):
                print(f"✓ 靜態文件目錄存在")
            else:
                print(f"✗ 靜態文件目錄不存在: {static_folder}")
                return False
            
            # 測試 URL
            with app.app_context():
                from flask import url_for
                try:
                    style_url = url_for('static', filename='css/style.css')
                    backend_url = url_for('static', filename='css/backend.css')
                    js_url = url_for('static', filename='js/socketio_client.js')
                    
                    print(f"\n✓ 靜態文件 URL 生成正常：")
                    print(f"  - {style_url}")
                    print(f"  - {backend_url}")
                    print(f"  - {js_url}")
                except Exception as e:
                    print(f"✗ URL 生成失敗: {e}")
                    return False
            
        except Exception as e:
            print(f"⚠️  無法檢查 Flask 配置: {e}")
        
        return True
    
    print("="*60 + "\n")

if __name__ == '__main__':
    success = check_static_files()
    sys.exit(0 if success else 1)


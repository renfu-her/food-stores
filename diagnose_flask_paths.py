#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
診斷 Flask 模板和靜態文件路徑
"""

import os
import sys

def diagnose_paths():
    """診斷路徑配置"""
    print("\n" + "="*60)
    print("Flask 路徑診斷")
    print("="*60 + "\n")
    
    # 獲取當前文件位置
    current_file = __file__
    print(f"1. 當前腳本位置: {current_file}")
    
    # 獲取 app/__init__.py 位置
    app_init = os.path.join(os.path.dirname(os.path.dirname(current_file)), 'app', '__init__.py')
    print(f"2. app/__init__.py 位置: {app_init}")
    
    if not os.path.exists(app_init):
        print("   ✗ app/__init__.py 不存在")
        return False
    
    # 計算專案根目錄
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(app_init)))
    print(f"3. 專案根目錄: {BASE_DIR}")
    
    # 檢查模板目錄
    template_dir = os.path.join(BASE_DIR, 'public', 'templates')
    print(f"\n4. 模板目錄配置:")
    print(f"   路徑: {template_dir}")
    if os.path.exists(template_dir):
        print(f"   ✓ 目錄存在")
        
        # 檢查關鍵模板
        templates = [
            'backend/dashboard.html',
            'errors/500.html',
            'base/app.html'
        ]
        
        print(f"\n   檢查關鍵模板:")
        for template in templates:
            template_path = os.path.join(template_dir, template)
            if os.path.exists(template_path):
                print(f"   ✓ {template}")
            else:
                print(f"   ✗ {template} (不存在)")
    else:
        print(f"   ✗ 目錄不存在")
        return False
    
    # 檢查靜態文件目錄
    print(f"\n5. 靜態文件目錄配置:")
    static_dir_root = os.path.join(BASE_DIR, 'static')
    static_dir_public = os.path.join(BASE_DIR, 'public', 'static')
    
    print(f"   根目錄 static: {static_dir_root}")
    if os.path.exists(static_dir_root):
        print(f"   ✓ 存在（將使用此目錄）")
    else:
        print(f"   ✗ 不存在")
    
    print(f"   public/static: {static_dir_public}")
    if os.path.exists(static_dir_public):
        print(f"   ✓ 存在（將使用此目錄）")
    else:
        print(f"   ✗ 不存在")
    
    # 模擬 Flask 的選擇邏輯
    static_dir = static_dir_root if os.path.exists(static_dir_root) else static_dir_public
    print(f"\n   Flask 將使用: {static_dir}")
    
    if os.path.exists(static_dir):
        # 檢查關鍵靜態文件
        static_files = [
            'css/style.css',
            'css/backend.css',
            'js/socketio_client.js'
        ]
        
        print(f"\n   檢查關鍵靜態文件:")
        for static_file in static_files:
            file_path = os.path.join(static_dir, static_file)
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"   ✓ {static_file} ({size:,} bytes)")
            else:
                print(f"   ✗ {static_file} (不存在)")
    
    print("\n" + "="*60)
    print("診斷完成")
    print("="*60 + "\n")
    
    return True

if __name__ == '__main__':
    success = diagnose_paths()
    sys.exit(0 if success else 1)


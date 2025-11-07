#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
將靜態文件從 public/static 移動到專案根目錄的 static
"""

import os
import shutil
import sys

def move_static_files():
    """移動靜態文件"""
    print("\n" + "="*60)
    print("移動靜態文件：public/static -> static")
    print("="*60 + "\n")
    
    source_dir = 'public/static'
    target_dir = 'static'
    
    # 1. 檢查源目錄是否存在
    if not os.path.exists(source_dir):
        print(f"✗ 源目錄不存在: {source_dir}")
        print("\n請確認當前目錄是否正確")
        return False
    
    print(f"✓ 源目錄存在: {source_dir}")
    
    # 2. 檢查目標目錄
    if os.path.exists(target_dir):
        print(f"⚠️  目標目錄已存在: {target_dir}")
        response = input("是否要覆蓋？(y/N): ")
        if response.lower() != 'y':
            print("操作已取消")
            return False
        print(f"   → 將刪除現有目錄: {target_dir}")
        shutil.rmtree(target_dir)
    
    # 3. 移動文件
    try:
        print(f"\n正在移動 {source_dir} -> {target_dir}...")
        shutil.copytree(source_dir, target_dir)
        print(f"✓ 文件複製完成")
        
        # 統計文件
        file_count = sum([len(files) for r, d, files in os.walk(target_dir)])
        print(f"✓ 共移動 {file_count} 個文件")
        
    except Exception as e:
        print(f"✗ 移動失敗: {e}")
        return False
    
    # 4. 顯示移動的文件結構
    print("\n移動後的文件結構：")
    for root, dirs, files in os.walk(target_dir):
        level = root.replace(target_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files[:5]:  # 只顯示前5個文件
            print(f"{subindent}{file}")
        if len(files) > 5:
            print(f"{subindent}... 還有 {len(files) - 5} 個文件")
    
    print("\n" + "="*60)
    print("✓ 移動完成！")
    print("\n下一步：")
    print("1. 更新 Flask 配置：app/__init__.py")
    print("   static_folder='static'")
    print("\n2. 更新 Nginx 配置：")
    print("   alias /path/to/quick-foods/static;")
    print("\n3. 可選：刪除舊目錄 public/static（備份後）")
    print("="*60 + "\n")
    
    return True

if __name__ == '__main__':
    success = move_static_files()
    sys.exit(0 if success else 1)


#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
將上傳文件從 public/uploads 移動到專案根目錄的 uploads
"""

import os
import shutil
import sys

def move_uploads():
    """移動上傳文件"""
    print("\n" + "="*60)
    print("移動上傳文件：public/uploads -> uploads")
    print("="*60 + "\n")
    
    source_dir = 'public/uploads'
    target_dir = 'uploads'
    
    # 1. 檢查源目錄是否存在
    if not os.path.exists(source_dir):
        print(f"✗ 源目錄不存在: {source_dir}")
        print("\n請確認當前目錄是否正確")
        return False
    
    print(f"✓ 源目錄存在: {source_dir}")
    
    # 2. 檢查目標目錄
    if os.path.exists(target_dir):
        print(f"⚠️  目標目錄已存在: {target_dir}")
        response = input("是否要合併現有文件？(y/N): ")
        if response.lower() != 'y':
            print("操作已取消")
            return False
        print(f"   → 將合併到現有目錄: {target_dir}")
    else:
        print(f"✓ 將創建新目錄: {target_dir}")
    
    # 3. 移動文件
    try:
        print(f"\n正在移動 {source_dir} -> {target_dir}...")
        
        # 如果目標目錄不存在，直接複製
        if not os.path.exists(target_dir):
            shutil.copytree(source_dir, target_dir)
            print(f"✓ 文件複製完成")
        else:
            # 合併文件
            for root, dirs, files in os.walk(source_dir):
                # 計算相對路徑
                rel_path = os.path.relpath(root, source_dir)
                target_path = os.path.join(target_dir, rel_path) if rel_path != '.' else target_dir
                
                # 創建目標目錄
                os.makedirs(target_path, exist_ok=True)
                
                # 複製文件
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(target_path, file)
                    if not os.path.exists(dst_file):
                        shutil.copy2(src_file, dst_file)
                        print(f"  ✓ {os.path.join(rel_path, file)}")
                    else:
                        print(f"  ⚠ 跳過（已存在）: {os.path.join(rel_path, file)}")
        
        # 統計文件
        file_count = sum([len(files) for r, d, files in os.walk(target_dir)])
        print(f"\n✓ 共處理 {file_count} 個文件")
        
    except Exception as e:
        print(f"✗ 移動失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. 顯示移動的文件結構
    print("\n移動後的文件結構：")
    for root, dirs, files in os.walk(target_dir):
        level = root.replace(target_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        rel_path = os.path.relpath(root, target_dir)
        if rel_path == '.':
            print(f"{indent}uploads/")
        else:
            print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files[:5]:  # 只顯示前5個文件
            print(f"{subindent}{file}")
        if len(files) > 5:
            print(f"{subindent}... 還有 {len(files) - 5} 個文件")
    
    print("\n" + "="*60)
    print("✓ 移動完成！")
    print("\n下一步：")
    print("1. 更新 Flask 配置：app/__init__.py 和 app/config.py")
    print("2. 更新 Nginx 配置：")
    print("   alias /path/to/quick-foods/uploads;")
    print("3. 重新載入 Nginx：")
    print("   sudo systemctl reload nginx")
    print("4. 重啟 Flask 應用：")
    print("   sudo systemctl restart quick-foods")
    print("5. 可選：備份後刪除舊目錄 public/uploads")
    print("="*60 + "\n")
    
    return True

if __name__ == '__main__':
    success = move_uploads()
    sys.exit(0 if success else 1)


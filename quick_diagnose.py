#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速診斷工具 - 用於排查 500 錯誤
"""

import os
import sys

def quick_diagnose():
    """快速診斷常見問題"""
    print("\n" + "="*60)
    print("Quick Foods 快速診斷工具")
    print("="*60 + "\n")
    
    issues_found = []
    
    # 1. 檢查 .env 文件
    print("1. 檢查 .env 文件...")
    if not os.path.exists('.env'):
        print("   ✗ .env 文件不存在！")
        print("   → 請複製 env.example 為 .env 並填入正確配置")
        issues_found.append(".env 文件缺失")
    else:
        print("   ✓ .env 文件存在")
    
    # 2. 檢查關鍵目錄
    print("\n2. 檢查關鍵目錄...")
    required_dirs = ['public/uploads', 'logs', 'migrations']
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"   ✗ {dir_path} 不存在")
            issues_found.append(f"缺少目錄: {dir_path}")
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"   → 已自動創建 {dir_path}")
            except Exception as e:
                print(f"   → 無法創建: {e}")
        else:
            print(f"   ✓ {dir_path} 存在")
    
    # 3. 檢查 Python 依賴
    print("\n3. 檢查關鍵依賴...")
    critical_packages = {
        'flask': 'Flask',
        'flask_sqlalchemy': 'Flask-SQLAlchemy',
        'pymysql': 'PyMySQL',
        'dotenv': 'python-dotenv'
    }
    
    for package, display_name in critical_packages.items():
        try:
            __import__(package)
            print(f"   ✓ {display_name}")
        except ImportError:
            print(f"   ✗ {display_name} 未安裝")
            issues_found.append(f"缺少套件: {display_name}")
    
    # 4. 嘗試載入配置
    print("\n4. 檢查配置載入...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_env = ['SECRET_KEY', 'DB_HOST', 'DB_USER', 'DB_NAME']
        missing_env = []
        
        for env_var in required_env:
            if not os.environ.get(env_var):
                missing_env.append(env_var)
        
        if missing_env:
            print(f"   ✗ 缺少環境變數: {', '.join(missing_env)}")
            issues_found.append(f"環境變數未設定: {', '.join(missing_env)}")
        else:
            print("   ✓ 環境變數已設定")
            
    except Exception as e:
        print(f"   ✗ 配置載入失敗: {e}")
        issues_found.append(f"配置錯誤: {e}")
    
    # 5. 嘗試連接資料庫
    print("\n5. 檢查資料庫連接...")
    try:
        from dotenv import load_dotenv
        import pymysql
        
        load_dotenv()
        
        conn = pymysql.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            port=int(os.environ.get('DB_PORT', '3306')),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD', ''),
            database=os.environ.get('DB_NAME', 'food-stores'),
            charset='utf8mb4'
        )
        
        print("   ✓ 資料庫連接成功")
        
        # 檢查資料表
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if len(tables) == 0:
            print("   ⚠️  資料庫中沒有資料表")
            print("   → 請執行: flask db upgrade")
            issues_found.append("資料庫未初始化")
        else:
            print(f"   ✓ 找到 {len(tables)} 個資料表")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"   ✗ 資料庫連接失敗: {e}")
        issues_found.append(f"資料庫錯誤: {e}")
    
    # 6. 嘗試初始化應用
    print("\n6. 檢查應用初始化...")
    try:
        from app import create_app
        from app.config import Config
        
        app = create_app(Config)
        print("   ✓ 應用初始化成功")
        
    except Exception as e:
        print(f"   ✗ 應用初始化失敗: {e}")
        issues_found.append(f"應用初始化錯誤: {e}")
        
        # 顯示詳細錯誤
        import traceback
        print("\n詳細錯誤信息:")
        print("-" * 60)
        print(traceback.format_exc())
        print("-" * 60)
    
    # 總結
    print("\n" + "="*60)
    print("診斷結果")
    print("="*60)
    
    if not issues_found:
        print("\n✓ 沒有發現明顯問題")
        print("\n如果仍然出現 500 錯誤，請:")
        print("1. 執行完整檢查: python check_deployment.py")
        print("2. 查看伺服器日誌")
        print("3. 檢查 Web 伺服器（Nginx/Apache）配置")
        print("4. 檢查 WSGI 伺服器（Gunicorn/uWSGI）配置")
    else:
        print(f"\n✗ 發現 {len(issues_found)} 個問題:\n")
        for i, issue in enumerate(issues_found, 1):
            print(f"{i}. {issue}")
        
        print("\n建議的修復步驟:")
        print("-" * 60)
        
        if any(".env" in issue for issue in issues_found):
            print("\n📝 配置 .env 文件:")
            print("   cp env.example .env")
            print("   # 然後編輯 .env，填入正確的資料庫配置")
        
        if any("套件" in issue for issue in issues_found):
            print("\n📦 安裝依賴:")
            print("   pip install -r requirements.txt")
        
        if any("資料庫" in issue for issue in issues_found):
            print("\n🗄️  初始化資料庫:")
            print("   flask db upgrade")
            print("   python init_payment_methods.py")
        
        if any("目錄" in issue for issue in issues_found):
            print("\n📁 創建必要目錄:")
            print("   mkdir -p public/uploads logs")
        
    print("\n" + "="*60 + "\n")
    
    return 0 if not issues_found else 1

if __name__ == '__main__':
    sys.exit(quick_diagnose())


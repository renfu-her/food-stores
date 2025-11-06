#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
部署檢查工具
檢查正式主機部署時的常見問題
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """檢查環境變數"""
    print("\n" + "="*50)
    print("1. 檢查環境變數")
    print("="*50)
    
    load_dotenv()
    
    required_vars = [
        'SECRET_KEY',
        'DB_HOST',
        'DB_USER',
        'DB_PASSWORD',
        'DB_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            if var in ['DB_PASSWORD', 'SECRET_KEY']:
                print(f"✓ {var}: {'*' * len(value)}")
            else:
                print(f"✓ {var}: {value}")
        else:
            print(f"✗ {var}: 未設定")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  缺少環境變數: {', '.join(missing_vars)}")
        return False
    else:
        print("\n✓ 所有環境變數已設定")
        return True

def check_database():
    """檢查資料庫連接"""
    print("\n" + "="*50)
    print("2. 檢查資料庫連接")
    print("="*50)
    
    try:
        import pymysql
        load_dotenv()
        
        host = os.environ.get('DB_HOST', 'localhost')
        port = int(os.environ.get('DB_PORT', '3306'))
        user = os.environ.get('DB_USER', 'root')
        password = os.environ.get('DB_PASSWORD', '')
        database = os.environ.get('DB_NAME', 'food-stores')
        
        print(f"嘗試連接: {user}@{host}:{port}/{database}")
        
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✓ 資料庫連接成功")
        print(f"✓ MySQL 版本: {version[0]}")
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"✓ 資料表數量: {len(tables)}")
        
        if len(tables) == 0:
            print("⚠️  資料庫中沒有資料表，需要執行資料庫遷移")
        else:
            print(f"✓ 現有資料表: {', '.join([t[0] for t in tables[:5]])}{'...' if len(tables) > 5 else ''}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"✗ 資料庫連接失敗: {str(e)}")
        return False

def check_dependencies():
    """檢查 Python 依賴"""
    print("\n" + "="*50)
    print("3. 檢查 Python 依賴")
    print("="*50)
    
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_migrate',
        'flask_socketio',
        'pymysql',
        'bcrypt',
        'werkzeug',
        'PIL',
        'qrcode'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} 未安裝")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少套件: {', '.join(missing_packages)}")
        print("執行: pip install -r requirements.txt")
        return False
    else:
        print("\n✓ 所有依賴已安裝")
        return True

def check_directories():
    """檢查必要目錄"""
    print("\n" + "="*50)
    print("4. 檢查必要目錄")
    print("="*50)
    
    required_dirs = [
        'public/uploads',
        'public/static',
        'public/templates',
        'migrations',
        'app',
        'logs'
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✓ {dir_path}")
        else:
            print(f"⚠️  {dir_path} 不存在，正在創建...")
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"  ✓ 已創建 {dir_path}")
            except Exception as e:
                print(f"  ✗ 創建失敗: {str(e)}")
                return False
    
    return True

def check_permissions():
    """檢查檔案權限"""
    print("\n" + "="*50)
    print("5. 檢查檔案權限")
    print("="*50)
    
    critical_paths = [
        'public/uploads',
        'logs'
    ]
    
    for path in critical_paths:
        if os.path.exists(path):
            if os.access(path, os.W_OK):
                print(f"✓ {path} 可寫入")
            else:
                print(f"✗ {path} 無寫入權限")
                return False
        else:
            print(f"⚠️  {path} 不存在")
    
    return True

def check_app_initialization():
    """檢查應用初始化"""
    print("\n" + "="*50)
    print("6. 檢查應用初始化")
    print("="*50)
    
    try:
        from app import create_app
        from app.config import Config
        
        print("✓ 導入模組成功")
        
        app = create_app(Config)
        print("✓ 應用創建成功")
        
        with app.app_context():
            from app import db
            print("✓ 資料庫對象創建成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 應用初始化失敗: {str(e)}")
        import traceback
        print("\n詳細錯誤:")
        print(traceback.format_exc())
        return False

def main():
    print("\n" + "="*50)
    print("Quick Foods 部署檢查工具")
    print("="*50)
    
    results = []
    
    results.append(("環境變數", check_environment()))
    results.append(("Python 依賴", check_dependencies()))
    results.append(("資料庫連接", check_database()))
    results.append(("必要目錄", check_directories()))
    results.append(("檔案權限", check_permissions()))
    results.append(("應用初始化", check_app_initialization()))
    
    print("\n" + "="*50)
    print("檢查結果摘要")
    print("="*50)
    
    all_passed = True
    for name, result in results:
        status = "✓ 通過" if result else "✗ 失敗"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("✓ 所有檢查通過！應用應該可以正常運行。")
        print("\n如果仍然出現 500 錯誤，請檢查:")
        print("1. Web 伺服器（Nginx/Apache）配置")
        print("2. WSGI 伺服器（Gunicorn/uWSGI）配置")
        print("3. 伺服器日誌檔案")
        print("4. 執行 flask db upgrade 更新資料庫")
    else:
        print("✗ 發現問題，請根據上述錯誤進行修復。")
    print("="*50)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())


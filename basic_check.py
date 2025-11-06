#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基礎檢查工具 - 不需要任何外部依賴
用於檢查 Python 環境和基本配置
"""

import sys
import os

def print_header(text):
    """打印標題"""
    print("\n" + "="*60)
    print(text)
    print("="*60)

def check_python_version():
    """檢查 Python 版本"""
    print_header("1. 檢查 Python 版本")
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✓ Python 版本符合要求 (3.8+)")
        return True
    else:
        print("✗ Python 版本過低，需要 3.8 或更高")
        return False

def check_files():
    """檢查關鍵文件"""
    print_header("2. 檢查關鍵文件")
    
    required_files = [
        'app.py',
        'wsgi.py',
        'requirements.txt',
        'app/__init__.py',
        'app/config.py',
        'app/models.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (不存在)")
            all_exist = False
    
    return all_exist

def check_directories():
    """檢查必要目錄"""
    print_header("3. 檢查必要目錄")
    
    required_dirs = [
        'app',
        'app/routes',
        'public',
        'public/templates',
        'public/static',
        'migrations'
    ]
    
    optional_dirs = [
        'public/uploads',
        'logs'
    ]
    
    all_exist = True
    
    print("必要目錄:")
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} (不存在)")
            all_exist = False
    
    print("\n可選目錄（如果不存在將自動創建）:")
    for dir_path in optional_dirs:
        if os.path.exists(dir_path):
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ⚠ {dir_path} (不存在，需要創建)")
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"    → 已創建 {dir_path}")
            except Exception as e:
                print(f"    → 創建失敗: {e}")
    
    return all_exist

def check_env_file():
    """檢查 .env 文件"""
    print_header("4. 檢查 .env 文件")
    
    if os.path.exists('.env'):
        print("✓ .env 文件存在")
        
        # 嘗試讀取關鍵配置
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                content = f.read()
                
            required_keys = ['SECRET_KEY', 'DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
            missing_keys = []
            
            for key in required_keys:
                if f'{key}=' in content and not content.split(f'{key}=')[1].split('\n')[0].strip() in ['', 'your-', 'your_']:
                    print(f"  ✓ {key} 已設定")
                else:
                    print(f"  ✗ {key} 未設定或使用預設值")
                    missing_keys.append(key)
            
            if missing_keys:
                print(f"\n⚠️  需要設定的環境變數: {', '.join(missing_keys)}")
                return False
            return True
            
        except Exception as e:
            print(f"⚠️  無法讀取 .env 文件: {e}")
            return False
    else:
        print("✗ .env 文件不存在")
        print("\n立即執行:")
        print("  cp env.example .env")
        print("  nano .env  # 或使用 vi .env 編輯")
        return False

def check_requirements():
    """檢查 requirements.txt"""
    print_header("5. 檢查依賴文件")
    
    if not os.path.exists('requirements.txt'):
        print("✗ requirements.txt 不存在")
        return False
    
    print("✓ requirements.txt 存在")
    
    # 讀取所需的包
    try:
        with open('requirements.txt', 'r') as f:
            packages = [line.strip().split('==')[0].split('>=')[0] 
                       for line in f if line.strip() and not line.startswith('#')]
        
        print(f"\n需要安裝 {len(packages)} 個 Python 套件")
        print("\n立即執行以下命令安裝依賴:")
        print("  pip install -r requirements.txt")
        print("\n或使用 pip3:")
        print("  pip3 install -r requirements.txt")
        
    except Exception as e:
        print(f"⚠️  無法讀取 requirements.txt: {e}")
    
    return True

def check_installed_packages():
    """檢查已安裝的套件"""
    print_header("6. 檢查已安裝的 Python 套件")
    
    critical_packages = {
        'flask': 'Flask',
        'flask_sqlalchemy': 'Flask-SQLAlchemy',
        'pymysql': 'PyMySQL',
        'dotenv': 'python-dotenv'
    }
    
    missing = []
    installed = []
    
    for module_name, display_name in critical_packages.items():
        try:
            __import__(module_name)
            print(f"✓ {display_name}")
            installed.append(display_name)
        except ImportError:
            print(f"✗ {display_name} (未安裝)")
            missing.append(display_name)
    
    if missing:
        print(f"\n⚠️  缺少套件: {', '.join(missing)}")
        print("\n立即執行:")
        print("  pip install -r requirements.txt")
        return False
    else:
        print("\n✓ 所有關鍵套件已安裝")
        return True

def main():
    """主函數"""
    print("\n" + "="*60)
    print("Quick Foods 基礎環境檢查")
    print("="*60)
    print("此工具不需要任何外部依賴，可立即運行")
    print("="*60)
    
    results = []
    
    results.append(("Python 版本", check_python_version()))
    results.append(("關鍵文件", check_files()))
    results.append(("目錄結構", check_directories()))
    results.append(("環境變數", check_env_file()))
    results.append(("依賴文件", check_requirements()))
    results.append(("已安裝套件", check_installed_packages()))
    
    # 總結
    print("\n" + "="*60)
    print("檢查結果總結")
    print("="*60)
    
    all_passed = True
    for name, result in results:
        status = "✓ 通過" if result else "✗ 失敗"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print("✓ 基礎環境檢查通過")
        print("\n下一步:")
        print("  python quick_diagnose.py    # 執行完整診斷")
        print("  python test_app.py          # 測試應用")
    else:
        print("✗ 發現問題需要修復")
        print("\n建議的修復順序:")
        print("="*60)
        
        # 根據檢查結果給出具體建議
        if not results[3][1]:  # .env
            print("\n1. 創建並配置 .env 文件:")
            print("   cp env.example .env")
            print("   nano .env")
            print("   # 填入以下資訊:")
            print("   #   SECRET_KEY (使用: python -c \"import secrets; print(secrets.token_hex(32))\")")
            print("   #   DB_HOST (通常是 localhost)")
            print("   #   DB_USER (您的 MySQL 用戶名)")
            print("   #   DB_PASSWORD (您的 MySQL 密碼)")
            print("   #   DB_NAME (food-stores)")
        
        if not results[5][1]:  # 套件
            print("\n2. 安裝 Python 依賴:")
            print("   pip install -r requirements.txt")
            print("   # 或使用 pip3:")
            print("   pip3 install -r requirements.txt")
            print("   # 如果使用虛擬環境:")
            print("   source venv/bin/activate")
            print("   pip install -r requirements.txt")
        
        if not results[2][1]:  # 目錄
            print("\n3. 創建必要目錄:")
            print("   mkdir -p public/uploads logs")
        
        print("\n4. 創建資料庫:")
        print("   mysql -u root -p")
        print("   CREATE DATABASE `food-stores` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print("   EXIT;")
        
        print("\n5. 執行資料庫遷移:")
        print("   flask db upgrade")
        print("   python init_payment_methods.py")
        
        print("\n6. 重新執行檢查:")
        print("   python basic_check.py")
    
    print("="*60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())


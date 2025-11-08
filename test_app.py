#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
應用測試腳本 - 測試應用是否能正常初始化
"""

import sys
import os

def test_app():
    """測試應用初始化"""
    print("\n" + "="*60)
    print("快點訂 應用測試")
    print("="*60 + "\n")
    
    try:
        # 1. 測試導入
        print("1. 測試模組導入...")
        from app import create_app
        from app.config import Config
        print("   ✓ 模組導入成功")
        
        # 2. 測試應用創建
        print("\n2. 測試應用創建...")
        app = create_app(Config)
        print("   ✓ 應用創建成功")
        print(f"   - 應用名稱: {app.name}")
        print(f"   - Debug 模式: {app.debug}")
        
        # 3. 測試資料庫
        print("\n3. 測試資料庫連接...")
        with app.app_context():
            from app import db
            print("   ✓ 資料庫對象創建成功")
            
            # 測試連接
            try:
                result = db.session.execute(db.text('SELECT 1')).scalar()
                print("   ✓ 資料庫連接測試成功")
            except Exception as e:
                print(f"   ✗ 資料庫連接測試失敗: {e}")
                return False
            
            # 4. 測試模型導入
            print("\n4. 測試模型導入...")
            from app.models import (
                User, Shop, Product, Order, OrderItem,
                Table, PaymentMethod, ShopPaymentMethod
            )
            print("   ✓ 所有模型導入成功")
            
            # 5. 檢查資料表
            print("\n5. 檢查資料表...")
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"   ✓ 找到 {len(tables)} 個資料表")
            
            essential_tables = [
                'users', 'shops', 'products', 'orders',
                'tables', 'payment_methods'
            ]
            
            missing_tables = []
            for table in essential_tables:
                if table in tables:
                    print(f"   ✓ {table}")
                else:
                    print(f"   ✗ {table} (不存在)")
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"\n   ⚠️  缺少資料表: {', '.join(missing_tables)}")
                print("   → 請執行: flask db upgrade")
                return False
            
            # 6. 測試路由
            print("\n6. 測試路由註冊...")
            routes = [str(rule) for rule in app.url_map.iter_rules()]
            print(f"   ✓ 註冊了 {len(routes)} 個路由")
            
            # 檢查關鍵路由
            essential_routes = [
                '/',
                '/login',
                '/register',
                '/store_admin/dashboard',
                '/backend/dashboard',
                '/api/shops',
                '/api/products',
                '/api/cart/add'
            ]
            
            for route in essential_routes:
                if any(route in r for r in routes):
                    print(f"   ✓ {route}")
                else:
                    print(f"   ⚠️  {route} (未找到)")
        
        # 7. 測試配置
        print("\n7. 測試配置...")
        print(f"   - SECRET_KEY: {'已設定' if app.config.get('SECRET_KEY') else '未設定'}")
        print(f"   - SQLALCHEMY_DATABASE_URI: {'已設定' if app.config.get('SQLALCHEMY_DATABASE_URI') else '未設定'}")
        print(f"   - UPLOAD_FOLDER: {app.config.get('UPLOAD_FOLDER')}")
        
        if os.path.exists(app.config.get('UPLOAD_FOLDER', '')):
            print(f"   ✓ 上傳目錄存在")
        else:
            print(f"   ⚠️  上傳目錄不存在")
        
        print("\n" + "="*60)
        print("✓ 所有測試通過！應用可以正常運行。")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 測試失敗: {e}\n")
        
        import traceback
        print("詳細錯誤信息:")
        print("-" * 60)
        print(traceback.format_exc())
        print("-" * 60)
        
        return False

if __name__ == '__main__':
    success = test_app()
    sys.exit(0 if success else 1)


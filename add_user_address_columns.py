"""
添加用戶地址欄位到資料庫
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from sqlalchemy import text

def add_user_address_columns():
    app = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            # 檢查欄位是否已存在（MySQL 語法）
            result = conn.execute(text("SHOW COLUMNS FROM user"))
            columns = [row[0] for row in result]
            
            # 添加新欄位
            if 'phone' not in columns:
                conn.execute(text("ALTER TABLE user ADD COLUMN phone VARCHAR(20) NULL"))
                conn.commit()
                print("✅ 已添加 phone 欄位")
            
            if 'county' not in columns:
                conn.execute(text("ALTER TABLE user ADD COLUMN county VARCHAR(50) NULL"))
                conn.commit()
                print("✅ 已添加 county 欄位")
            
            if 'district' not in columns:
                conn.execute(text("ALTER TABLE user ADD COLUMN district VARCHAR(50) NULL"))
                conn.commit()
                print("✅ 已添加 district 欄位")
            
            if 'zipcode' not in columns:
                conn.execute(text("ALTER TABLE user ADD COLUMN zipcode VARCHAR(10) NULL"))
                conn.commit()
                print("✅ 已添加 zipcode 欄位")
            
            if 'address' not in columns:
                conn.execute(text("ALTER TABLE user ADD COLUMN address VARCHAR(500) NULL"))
                conn.commit()
                print("✅ 已添加 address 欄位")
        
        print("\n✅ 所有用戶地址欄位已成功添加！")

if __name__ == '__main__':
    add_user_address_columns()


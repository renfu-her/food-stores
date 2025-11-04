"""
批量更新所有用戶密碼腳本
用於重新哈希所有用戶密碼，確保使用正確的加密方式
"""
from app import create_app, db
from app.models import User
from app.utils.password import hash_password
from app.config import Config

def update_all_passwords():
    """更新所有用戶的密碼哈希"""
    app = create_app(Config)
    
    with app.app_context():
        # 定義需要更新的用戶和密碼
        users_to_update = {
            'admin@admin.com': 'admin123',
            # 可以在這裡添加其他需要重置的用戶
            # 'user@example.com': 'password123',
        }
        
        updated_count = 0
        
        for email, password in users_to_update.items():
            user = User.query.filter_by(email=email).first()
            if user:
                user.password_hash = hash_password(password)
                updated_count += 1
                print(f"✓ 已更新用戶: {email}")
            else:
                print(f"✗ 找不到用戶: {email}")
        
        if updated_count > 0:
            db.session.commit()
            print(f"\n✅ 成功更新 {updated_count} 個用戶的密碼！")
        else:
            print("\n❌ 沒有用戶被更新")

if __name__ == '__main__':
    update_all_passwords()


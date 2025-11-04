"""
重置管理員密碼腳本
用於重置 admin@admin.com 的密碼為 admin123
"""
from app import create_app, db
from app.models import User
from app.utils.password import hash_password
from app.config import Config

def reset_admin_password():
    """重置管理員密碼"""
    app = create_app(Config)
    
    with app.app_context():
        # 查找管理員帳戶
        admin = User.query.filter_by(email='admin@admin.com').first()
        
        if not admin:
            print("❌ 找不到管理員帳戶 admin@admin.com")
            print("請先運行 init_db.py 初始化資料庫")
            return
        
        # 更新密碼
        admin.password_hash = hash_password('admin123')
        db.session.commit()
        
        print("✅ 管理員密碼已重置！")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("帳戶資訊：")
        print(f"  郵箱: {admin.email}")
        print(f"  密碼: admin123")
        print(f"  角色: {admin.role}")
        print(f"  狀態: {'啟用' if admin.is_active else '禁用'}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("\n現在可以使用以下資訊登入：")
        print("  後台登入: http://localhost:5000/backend/login")
        print("  郵箱: admin@admin.com")
        print("  密碼: admin123")

if __name__ == '__main__':
    reset_admin_password()


"""
資料庫初始化腳本
用於建立預設管理員帳戶和其他初始化資料
"""
from app import create_app, db
from app.models import User, Category
from app.utils.password import hash_password
from app.config import Config

def init_db():
    """初始化資料庫"""
    app = create_app(Config)
    
    with app.app_context():
        # 建立所有表
        db.create_all()
        
        # 檢查是否已存在管理員帳戶
        admin = User.query.filter_by(email='admin@admin.com').first()
        if not admin:
            # 建立預設管理員帳戶
            admin = User(
                name='admin',
                email='admin@admin.com',
                password_hash=hash_password('admin123'),
                role='admin',
                is_active=True
            )
            db.session.add(admin)
            print("建立預設管理員帳戶: admin@admin.com / admin123")
        
        # 建立一些預設分類
        categories = [
            {'name': '主食', 'description': '各種主食類產品'},
            {'name': '飲品', 'description': '各種飲品'},
            {'name': '小食', 'description': '各種小食和零食'},
            {'name': '甜點', 'description': '各種甜品和蛋糕'},
        ]
        
        for cat_data in categories:
            category = Category.query.filter_by(name=cat_data['name']).first()
            if not category:
                category = Category(**cat_data)
                db.session.add(category)
                print(f"建立分類: {cat_data['name']}")
        
        db.session.commit()
        print("資料庫初始化完成！")

if __name__ == '__main__':
    init_db()


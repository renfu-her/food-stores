"""
權限測試腳本
用於驗證系統的權限控制是否正常工作
"""
from app import create_app, db
from app.models import User, Shop, Product, Category
from werkzeug.security import generate_password_hash

def create_test_accounts():
    """創建測試帳號和數據"""
    app = create_app()
    with app.app_context():
        print("🔧 開始創建測試帳號...")
        
        # 檢查是否已存在測試帳號
        if User.query.filter_by(email='owner_a@test.com').first():
            print("⚠️  測試帳號已存在，請先刪除舊數據或使用 reset_test_data.py")
            return
        
        # 創建分類（如果不存在）
        category = Category.query.filter_by(name='測試分類').first()
        if not category:
            category = Category(name='測試分類', description='用於測試的分類')
            db.session.add(category)
            db.session.flush()
        
        # ====== 創建店主 A ======
        print("\n📝 創建店主 A...")
        user_a = User(
            name='店主A',
            email='owner_a@test.com',
            password_hash=generate_password_hash('Test123@'),
            role='store_admin',
            phone='0912345678'
        )
        db.session.add(user_a)
        db.session.flush()
        print(f"   ✅ 店主A (ID: {user_a.id})")
        
        # 創建店鋪 A
        shop_a = Shop(
            name='店鋪A',
            description='店主A的店鋪',
            owner_id=user_a.id,
            shop_order_id='TESTA',
            max_toppings_per_order=5,
            status='active'
        )
        db.session.add(shop_a)
        db.session.flush()
        print(f"   ✅ 店鋪A (ID: {shop_a.id}, Order ID: TESTA)")
        
        # 創建產品 A
        product_a = Product(
            name='店鋪A的產品1',
            description='測試產品',
            shop_id=shop_a.id,
            category_id=category.id,
            unit_price=100,
            stock_quantity=50,
            is_active=True,
            has_cold_drink=True,
            cold_drink_price=10,
            has_hot_drink=True,
            hot_drink_price=5
        )
        db.session.add(product_a)
        db.session.flush()
        print(f"   ✅ 產品1 (ID: {product_a.id})")
        
        # ====== 創建店主 B ======
        print("\n📝 創建店主 B...")
        user_b = User(
            name='店主B',
            email='owner_b@test.com',
            password_hash=generate_password_hash('Test123@'),
            role='store_admin',
            phone='0987654321'
        )
        db.session.add(user_b)
        db.session.flush()
        print(f"   ✅ 店主B (ID: {user_b.id})")
        
        # 創建店鋪 B
        shop_b = Shop(
            name='店鋪B',
            description='店主B的店鋪',
            owner_id=user_b.id,
            shop_order_id='TESTB',
            max_toppings_per_order=3,
            status='active'
        )
        db.session.add(shop_b)
        db.session.flush()
        print(f"   ✅ 店鋪B (ID: {shop_b.id}, Order ID: TESTB)")
        
        # 創建產品 B
        product_b = Product(
            name='店鋪B的產品1',
            description='測試產品',
            shop_id=shop_b.id,
            category_id=category.id,
            unit_price=80,
            stock_quantity=30,
            is_active=True,
            has_cold_drink=False,
            has_hot_drink=True,
            hot_drink_price=8
        )
        db.session.add(product_b)
        db.session.flush()
        print(f"   ✅ 產品1 (ID: {product_b.id})")
        
        # 提交所有變更
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ 測試帳號創建完成！")
        print("="*60)
        
        print("\n📋 測試帳號資訊：")
        print("\n【店主 A】")
        print(f"   Email: owner_a@test.com")
        print(f"   密碼: Test123@")
        print(f"   店鋪: {shop_a.name} (ID: {shop_a.id})")
        print(f"   產品: {product_a.name} (ID: {product_a.id})")
        
        print("\n【店主 B】")
        print(f"   Email: owner_b@test.com")
        print(f"   密碼: Test123@")
        print(f"   店鋪: {shop_b.name} (ID: {shop_b.id})")
        print(f"   產品: {product_b.name} (ID: {product_b.id})")
        
        print("\n" + "="*60)
        print("🧪 開始測試權限控制：")
        print("="*60)
        
        print("\n1️⃣  使用「店主 A」登入 http://localhost:5000/shop")
        print("   ✅ 應該只能看到「店鋪A」")
        print("   ✅ 應該只能看到「店鋪A的產品1」")
        print("   ❌ 不應該看到「店鋪B」或其產品")
        
        print("\n2️⃣  測試 API：GET /api/shops/my-shops")
        print("   【店主 A 登入】")
        print("   ✅ 應該只返回店鋪A")
        print("   【店主 B 登入】")
        print("   ✅ 應該只返回店鋪B")
        
        print("\n3️⃣  測試 API：PUT /api/shops/{shop_b_id}")
        print("   【使用店主 A 的帳號】")
        print(f"   ❌ 應該返回 403 Forbidden（無權修改店鋪B）")
        
        print("\n4️⃣  測試 API：PUT /api/products/{product_b_id}")
        print("   【使用店主 A 的帳號】")
        print(f"   ❌ 應該返回 403 Forbidden（無權修改店鋪B的產品）")
        
        print("\n5️⃣  使用「Admin」帳號登入後台")
        print("   ✅ 應該可以看到所有店鋪（店鋪A + 店鋪B）")
        print("   ✅ 應該可以編輯任何店鋪和產品")
        
        print("\n" + "="*60)
        print("📖 詳細測試說明請參閱：docs/PERMISSIONS.md")
        print("="*60)

def cleanup_test_data():
    """清理測試數據"""
    app = create_app()
    with app.app_context():
        print("🧹 開始清理測試數據...")
        
        # 刪除測試用戶和相關數據（CASCADE 會自動刪除店鋪、產品等）
        User.query.filter_by(email='owner_a@test.com').delete()
        User.query.filter_by(email='owner_b@test.com').delete()
        
        # 刪除測試分類（如果沒有其他產品使用）
        test_category = Category.query.filter_by(name='測試分類').first()
        if test_category and Product.query.filter_by(category_id=test_category.id).count() == 0:
            db.session.delete(test_category)
        
        db.session.commit()
        print("✅ 測試數據已清理")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'cleanup':
        # 清理測試數據
        cleanup_test_data()
    else:
        # 創建測試帳號
        create_test_accounts()
        print("\n💡 提示：運行 'python test_permissions.py cleanup' 可清理測試數據")


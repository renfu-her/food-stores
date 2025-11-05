# 權限管理架構說明

## 概述

本系統實現了基於角色的存取控制（RBAC），確保不同角色的使用者只能存取和修改自己權限範圍內的資源。

---

## 三種角色

### 1. **Admin（超級管理員）**
- **權限範圍**：完整系統控制
- **可存取**：
  - ✅ 所有店鋪（查看、編輯、刪除）
  - ✅ 所有產品（查看、編輯、刪除）
  - ✅ 所有訂單（查看、處理）
  - ✅ 系統設定（訂單編號、郵件設定）
  - ✅ 內容管理（Banner、關於我們、最新消息）
  - ✅ 用戶管理

### 2. **Store Admin（店主）**
- **權限範圍**：僅限自己擁有的店鋪
- **可存取**：
  - ✅ 自己的店鋪（`owner_id = user.id`）
  - ✅ 自己店鋪的產品（`product.shop_id` 屬於自己的店鋪）
  - ✅ 自己店鋪的訂單（`order.shop_id` 屬於自己的店鋪）
  - ✅ 自己店鋪的配料（`topping.shop_id` 屬於自己的店鋪）
- **無法存取**：
  - ❌ 其他店主的店鋪
  - ❌ 其他店鋪的產品
  - ❌ 系統設定
  - ❌ 內容管理

### 3. **Customer（顧客）**
- **權限範圍**：瀏覽和購買
- **可存取**：
  - ✅ 瀏覽所有啟用的店鋪和產品
  - ✅ 購物車和結帳
  - ✅ 查看自己的訂單（`order.user_id = user.id`）
  - ✅ 個人資料管理
- **無法存取**：
  - ❌ 任何管理功能
  - ❌ 其他用戶的訂單

---

## 權限實現方式

### 📁 路由層級控制

#### **店鋪管理路由** (`app/routes/store_admin.py`)

所有路由都使用 `@role_required('store_admin')` 裝飾器，並且只查詢當前用戶擁有的店鋪：

```python
@store_admin_bp.route('/products')
@role_required('store_admin')
def products():
    user = get_current_user()
    # ✅ 只查詢 owner_id = user.id 的店鋪
    shop = Shop.query.filter_by(owner_id=user.id).first_or_404()
    # ✅ 只查詢屬於該店鋪的產品
    products_list = Product.query.filter_by(shop_id=shop.id).all()
    return render_template('shop/products.html', products=products_list, shop=shop)
```

**關鍵過濾條件：**
```python
# 店鋪過濾
Shop.query.filter_by(owner_id=user.id)

# 產品過濾
Product.query.filter_by(shop_id=shop.id)

# 訂單過濾
Order.query.filter_by(shop_id=shop.id)

# 配料過濾
Topping.query.filter_by(shop_id=shop.id)
```

#### **後台管理路由** (`app/routes/backend.py`)

使用 `@role_required('admin')` 裝飾器，可查詢所有資源：

```python
@backend_bp.route('/shops')
@role_required('admin')
def shops():
    # ✅ Admin 可以查看所有店鋪
    shops = Shop.query.all()
    return render_template('backend/shops/list.html', shops=shops)
```

---

### 🔌 API 層級控制

#### **店鋪 API** (`app/routes/api/shops.py`)

##### 1. 獲取我的店鋪列表

```python
@shops_api_bp.route('/my-shops', methods=['GET'])
@login_required
def get_my_shops():
    user = get_current_user()
    
    if user.role == 'admin':
        # ✅ Admin 可以看到所有店鋪
        shops = Shop.query.all()
    elif user.role == 'store_admin':
        # ✅ Store Admin 只能看到自己的店鋪
        shops = Shop.query.filter_by(owner_id=user.id).all()
    else:
        shops = []
    
    return jsonify({'shops': shops_data})
```

##### 2. 更新店鋪

```python
@shops_api_bp.route('/<int:shop_id>', methods=['PUT'])
@login_required
def update_shop(shop_id):
    user = get_current_user()
    shop = Shop.query.get_or_404(shop_id)
    
    # ✅ 權限檢查：只有 Admin 或店鋪擁有者可以修改
    if user.role != 'admin' and shop.owner_id != user.id:
        return jsonify({'error': 'forbidden', 'message': '無權修改此店鋪'}), 403
    
    # 執行更新...
    db.session.commit()
    return jsonify({'message': '更新成功'})
```

**權限檢查邏輯：**
```python
# 允許修改的條件（兩者滿足其一）
user.role == 'admin'  OR  shop.owner_id == user.id
```

#### **產品 API** (`app/routes/api/products.py`)

##### 更新產品

```python
@products_api_bp.route('/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    user = get_current_user()
    product = Product.query.get_or_404(product_id)
    shop = Shop.query.get_or_404(product.shop_id)
    
    # ✅ 權限檢查：通過店鋪的 owner_id 來檢查
    if user.role != 'admin' and shop.owner_id != user.id:
        return jsonify({'error': 'forbidden', 'message': '無權修改此產品'}), 403
    
    # 執行更新...
    db.session.commit()
    return jsonify({'message': '更新成功'})
```

**權限檢查流程：**
```
1. 獲取產品 (product)
2. 獲取產品所屬的店鋪 (shop = Shop.query.get(product.shop_id))
3. 檢查：user.role == 'admin' OR shop.owner_id == user.id
```

#### **訂單 API** (`app/routes/api/orders.py`)

##### 獲取訂單列表

```python
@orders_api_bp.route('/', methods=['GET'])
@login_required
def get_orders():
    user = get_current_user()
    
    if user.role == 'admin':
        # ✅ Admin 可以看到所有訂單
        orders = Order.query.all()
    elif user.role == 'store_admin':
        # ✅ Store Admin 只能看到自己店鋪的訂單
        shops = Shop.query.filter_by(owner_id=user.id).all()
        shop_ids = [shop.id for shop in shops]
        orders = Order.query.filter(Order.shop_id.in_(shop_ids)).all()
    else:
        # ✅ Customer 只能看到自己的訂單
        orders = Order.query.filter_by(user_id=user.id).all()
    
    return jsonify({'orders': orders_data})
```

---

## 裝飾器說明

### `@role_required(role)`

用於路由級別的權限控制：

```python
from app.utils.decorators import role_required

@app.route('/admin')
@role_required('admin')
def admin_page():
    # 只有 admin 角色可以訪問
    pass

@app.route('/shop')
@role_required('store_admin')
def shop_page():
    # 只有 store_admin 角色可以訪問
    pass
```

**實現邏輯**（`app/utils/decorators.py`）：

```python
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. 檢查是否登入
            user_id = session.get('user_id')
            if not user_id:
                # 根據路由智能重定向
                if request.path.startswith('/backend'):
                    return redirect(url_for('backend.login'))
                elif request.path.startswith('/shop'):
                    return redirect(url_for('store_admin.login'))
                else:
                    return redirect(url_for('customer.login'))
            
            # 2. 檢查角色
            user = User.query.get(user_id)
            if not user or user.role not in roles:
                return jsonify({'error': 'forbidden'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

---

## 關鍵過濾模式

### 店鋪管理者（Store Admin）的資源過濾

| 資源 | 過濾方式 | 說明 |
|------|---------|------|
| **店鋪** | `Shop.query.filter_by(owner_id=user.id)` | 只查詢 `owner_id` 等於當前用戶的店鋪 |
| **產品** | `Product.query.filter_by(shop_id=shop.id)` | 只查詢屬於該店鋪的產品 |
| **訂單** | `Order.query.filter_by(shop_id=shop.id)` | 只查詢屬於該店鋪的訂單 |
| **配料** | `Topping.query.filter_by(shop_id=shop.id)` | 只查詢屬於該店鋪的配料 |

### 管理員（Admin）的資源過濾

| 資源 | 過濾方式 | 說明 |
|------|---------|------|
| **店鋪** | `Shop.query.all()` | 查詢所有店鋪 |
| **產品** | `Product.query.all()` | 查詢所有產品 |
| **訂單** | `Order.query.all()` | 查詢所有訂單 |

---

## 權限檢查檢查清單

### 新增功能時的權限檢查

✅ **路由層級**
- [ ] 添加 `@role_required(role)` 裝飾器
- [ ] 確認路由只查詢當前用戶有權限的資源

✅ **API 層級**
- [ ] 添加 `@login_required` 裝飾器
- [ ] 在修改/刪除操作前檢查 `owner_id`
- [ ] 為不同角色返回不同的資源列表

✅ **查詢過濾**
- [ ] Store Admin: 使用 `filter_by(owner_id=user.id)` 或 `filter_by(shop_id=shop.id)`
- [ ] Customer: 使用 `filter_by(user_id=user.id)`
- [ ] Admin: 可查詢所有資源

✅ **錯誤處理**
- [ ] 返回 403 Forbidden（無權限）
- [ ] 返回 404 Not Found（資源不存在或無權查看）
- [ ] 提供清晰的錯誤訊息

---

## 測試場景

### 店鋪管理者（Store Admin）

#### ✅ 應該可以：
1. 查看自己的店鋪列表
2. 編輯自己的店鋪資訊
3. 新增/編輯/刪除自己店鋪的產品
4. 新增/編輯/刪除自己店鋪的配料
5. 查看/處理自己店鋪的訂單

#### ❌ 應該不可以：
1. 查看其他店主的店鋪
2. 編輯其他店鋪的資訊
3. 存取其他店鋪的產品
4. 存取系統設定
5. 存取內容管理功能

### 測試方法

**1. 創建測試店主帳號：**
```python
# test_permissions.py
from app import create_app, db
from app.models import User, Shop
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # 創建店主 A
    user_a = User(
        name='店主A',
        email='owner_a@test.com',
        password_hash=generate_password_hash('Test123@'),
        role='store_admin'
    )
    db.session.add(user_a)
    db.session.flush()
    
    # 創建店鋪 A（屬於店主 A）
    shop_a = Shop(
        name='店鋪A',
        owner_id=user_a.id,
        shop_order_id='SHOPA'
    )
    db.session.add(shop_a)
    
    # 創建店主 B
    user_b = User(
        name='店主B',
        email='owner_b@test.com',
        password_hash=generate_password_hash('Test123@'),
        role='store_admin'
    )
    db.session.add(user_b)
    db.session.flush()
    
    # 創建店鋪 B（屬於店主 B）
    shop_b = Shop(
        name='店鋪B',
        owner_id=user_b.id,
        shop_order_id='SHOPB'
    )
    db.session.add(shop_b)
    
    db.session.commit()
    print("測試帳號創建完成！")
```

**2. 測試權限隔離：**

```bash
# 使用店主 A 帳號登入
# 測試：GET /api/shops/my-shops
# 預期：只返回店鋪 A

# 測試：PUT /api/shops/<shop_b_id>
# 預期：返回 403 Forbidden

# 測試：GET /shop/products
# 預期：只顯示店鋪 A 的產品
```

---

## 安全建議

### 1. **永遠在服務端驗證權限**
❌ 不要只依賴前端隱藏按鈕或連結
✅ 在每個 API 端點都進行權限檢查

### 2. **使用白名單而非黑名單**
❌ 不要檢查「哪些角色不能訪問」
✅ 檢查「哪些角色可以訪問」

### 3. **查詢過濾優於事後檢查**
❌ 不要先查詢所有資源再過濾
✅ 在 SQL 查詢時就進行過濾

```python
# ❌ 不推薦
shops = Shop.query.all()
my_shops = [s for s in shops if s.owner_id == user.id]

# ✅ 推薦
my_shops = Shop.query.filter_by(owner_id=user.id).all()
```

### 4. **記錄權限相關操作**
使用 `log_update()` 記錄所有修改操作，便於審計。

### 5. **定期審查權限邏輯**
每次添加新功能時，檢查：
- 是否添加了權限裝飾器
- 是否正確過濾了資源
- 是否測試了權限隔離

---

## 總結

本系統的權限管理通過以下方式確保資料安全：

1. **路由層級**：`@role_required()` 裝飾器控制頁面訪問
2. **API 層級**：檢查 `owner_id` 和 `shop_id` 確保操作權限
3. **查詢過濾**：使用 `filter_by()` 確保只查詢有權限的資源
4. **智能重定向**：根據路由自動重定向到對應的登入頁面

### 核心原則

```
Admin：可以訪問所有資源
Store Admin：只能訪問 owner_id = user.id 的店鋪及其關聯資源
Customer：只能訪問 user_id = user.id 的訂單和公開資源
```

這種設計確保了：
- ✅ **資料隔離**：店主之間無法互相訪問資料
- ✅ **靈活性**：Admin 可以管理整個系統
- ✅ **安全性**：所有修改操作都需要權限驗證
- ✅ **可擴展性**：易於添加新角色或權限規則


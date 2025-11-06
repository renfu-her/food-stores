# 快速參考卡片

## 🗂️ 頁面結構對比

### Backend（Admin 超級管理員）

```
/backend
├── /shops
│   ├── list.html         → 所有店鋪列表
│   ├── add.html          → 新增店鋪（需選擇店主）
│   └── /<id>/edit        → 編輯店鋪
│
├── /products
│   ├── list.html         → 所有產品列表
│   ├── add.html          → 新增產品（需選擇店鋪）
│   └── /<id>/edit        → 編輯產品
│
└── /settings
    ├── 訂單設定（訂單前綴）
    └── 郵件設定（預留）
```

### Shop Admin（店主）

```
/store_admin
├── /shops
│   ├── list.html         → 自己的店鋪列表（owner_id 過濾）
│   ├── add.html          → 新增店鋪（自動為當前用戶）
│   └── /<id>/edit        → 編輯店鋪（權限檢查）
│
├── /products
│   ├── list.html         → 自己店鋪的產品（shop_id 過濾）
│   ├── add.html          → 新增產品（自動鎖定店鋪 + 飲品選項）
│   └── /<id>/edit        → 編輯產品（權限檢查 + 飲品選項）
│
├── /toppings             → 配料管理
├── /orders               → 訂單管理
└── /statistics           → 統計資料
```

---

## 🔐 權限對比

| 功能 | Backend (Admin) | Shop Admin (店主) |
|------|----------------|------------------|
| **店鋪查詢** | `Shop.query.all()` | `Shop.query.filter_by(owner_id=user.id)` |
| **產品查詢** | `Product.query.all()` | `Product.query.filter_by(shop_id=shop.id)` |
| **刪除記錄** | 可查看已刪除 | 無法查看已刪除 |
| **新增店鋪** | 需選擇店主 | 自動為當前用戶 |
| **新增產品** | 需選擇店鋪 | 自動為當前店鋪 |

---

## 🗑️ 軟刪除 vs 硬刪除

| 特性 | 軟刪除（本系統） | 硬刪除 |
|------|---------------|--------|
| **實現方式** | `deleted_at = datetime.now()` | `db.session.delete(obj)` |
| **數據保留** | ✅ 保留 | ❌ 永久刪除 |
| **可恢復** | ✅ 可恢復 | ❌ 不可恢復 |
| **查詢需要** | `.filter(deleted_at.is_(None))` | 無需過濾 |
| **關聯數據** | ✅ 完整保留 | ❌ 可能破壞 |
| **適用範圍** | Shop, Product | 無 |

---

## 🛣️ 路由快速查找

### Store Admin 路由

```python
# 店鋪管理
GET  /store_admin/shops              # 店鋪列表
GET  /store_admin/shops/add          # 新增店鋪
GET  /store_admin/shops/<id>/edit    # 編輯店鋪

# 產品管理
GET  /store_admin/products              # 產品列表
GET  /store_admin/products/add          # 新增產品
GET  /store_admin/products/<id>/edit    # 編輯產品

# 其他
GET  /store_admin/profile            # 店鋪設定
GET  /store_admin/toppings           # 配料管理
GET  /store_admin/orders             # 訂單管理
GET  /store_admin/statistics         # 統計資料
```

### API 路由

```python
# 店鋪 API
GET    /api/shops/my-shops    # 我的店鋪列表
POST   /api/shops             # 創建店鋪
PUT    /api/shops/<id>        # 更新店鋪
DELETE /api/shops/<id>        # 軟刪除店鋪

# 產品 API
GET    /api/products          # 產品列表
GET    /api/products/<id>     # 產品詳情
POST   /api/products          # 創建產品
PUT    /api/products/<id>     # 更新產品
DELETE /api/products/<id>     # 軟刪除產品
```

---

## 🎨 飲品選項快速參考

### 後台設置

```
產品編輯頁面
└── 飲品選項
    ├── ☑ 🧊 提供冷飲 → $ 10
    └── ☑ ☕ 提供熱飲 → $  5
```

### 數據庫字段

```python
Product:
  has_cold_drink: Boolean
  cold_drink_price: Decimal(10,2)
  has_hot_drink: Boolean
  hot_drink_price: Decimal(10,2)

OrderItem:
  drink_type: String(20)      # 'cold', 'hot', or null
  drink_price: Decimal(10,2)
```

### 前台顯示

```
商品詳情
└── 飲品選擇（Radio 單選）
    ◯ 🧊 冷飲 +$10
    ◯ ☕ 熱飲 +$5
    ◉ 不需要（預設）
```

### API 傳遞

```json
{
  "product_id": 1,
  "quantity": 2,
  "drink_type": "cold",
  "drink_price": 10
}
```

---

## 📊 價格計算公式

```javascript
總價 = (商品基礎價 + 配料總價 + 飲品價格) × 數量

範例：
  珍珠奶茶         $50
  + 珍珠（配料）   $10
  + 冷飲           $10
  ────────────────────
  單件價格         $70
  × 數量            2
  ────────────────────
  總價           $140
```

---

## 🔍 查詢過濾模式

### 店主查詢（Store Admin）

```python
# 1. 獲取店鋪
shop = Shop.query.filter_by(owner_id=user.id) \
                 .filter(Shop.deleted_at.is_(None)) \
                 .first_or_404()

# 2. 獲取產品
products = Product.query.filter_by(shop_id=shop.id) \
                        .filter(Product.deleted_at.is_(None)) \
                        .all()

# 3. 獲取訂單
orders = Order.query.filter_by(shop_id=shop.id).all()
```

### 管理員查詢（Admin）

```python
# 查看所有（包括已刪除）
shops = Shop.query.all()
products = Product.query.all()

# 查看未刪除
shops = Shop.query.filter(Shop.deleted_at.is_(None)).all()
```

### 顧客查詢（Customer）

```python
# 只查看啟用且未刪除的店鋪和產品
shops = Shop.query.filter_by(status='active') \
                  .filter(Shop.deleted_at.is_(None)) \
                  .all()

products = Product.query.filter_by(is_active=True) \
                        .filter(Product.deleted_at.is_(None)) \
                        .all()
```

---

## 🚀 快速操作命令

### 創建測試數據

```bash
# 運行應用
python app.py

# 訪問店主後台
http://localhost:5000/store_admin

# 登入帳號
Email: store1@store.com
密碼: Qq123456@
```

### 數據庫遷移

```bash
# 創建遷移
flask db migrate -m "描述變更"

# 應用遷移
flask db upgrade

# 回滾遷移
flask db downgrade

# 查看當前版本
flask db current
```

### 重置密碼

```python
# reset_password.py
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    user = User.query.filter_by(email='store1@store.com').first()
    if user:
        user.password_hash = generate_password_hash('新密碼')
        db.session.commit()
        print("密碼已重置")
```

---

## 📚 文檔導航

| 需求 | 文檔路徑 |
|------|---------|
| 完整項目說明 | [README.md](../README.md) |
| 權限管理架構 | [PERMISSIONS.md](./PERMISSIONS.md) |
| 店主操作指南 | [SHOP_ADMIN_GUIDE.md](./SHOP_ADMIN_GUIDE.md) |
| 更新日誌 | [CHANGELOG.md](../CHANGELOG.md) |
| API 文檔 | [README.md#api-文檔](../README.md#api-文檔) |

---

## 🎯 關鍵差異總結

### 設計理念

**Backend（Admin）：**
- 🌐 全局視角
- 📊 管理所有資源
- ⚙️ 系統設定
- 🔧 高級功能

**Shop Admin（店主）：**
- 🏪 店鋪視角
- 📦 只管理自己的資源
- 🎯 專注日常運營
- 💼 簡化操作

### 操作差異

| 操作 | Backend | Shop Admin |
|------|---------|-----------|
| 新增店鋪 | 選擇店主 ↓ | 自動為當前用戶 |
| 新增產品 | 選擇店鋪 ↓ | 自動為當前店鋪 |
| 查看列表 | 所有記錄 | 只有自己的 |
| 刪除後 | 可查看已刪除 | 自動隱藏 |
| 恢復功能 | ✅ 可恢復 | ❌ 需找管理員 |

---

<div align="center">
  <p>⚡ 快速查找 · 高效管理</p>
  <p>📖 更多詳細說明請參閱完整文檔</p>
</div>


# 更新日誌 (CHANGELOG)

> 本檔案記錄所有重要的系統修改、新增功能、Bug 修復等。

---

## 2025-11-06 18:30 - 產品管理新增冷熱飲選項UI

### ✨ 功能增強

**Backend 與 Shop Admin 產品新增/編輯添加飲品選項：**
- ✅ 添加飲品類型下拉選擇器（4個選項）
- ✅ 選項：不提供飲品、僅提供冷飲、僅提供熱飲、冷熱飲皆有
- ✅ 動態顯示/隱藏價格輸入框
- ✅ 冷飲加價和熱飲加價可獨立設定
- ✅ 價格可為 0（表示不加價）

**UI 設計：**
```html
<select id="drinkOption">
    <option value="none">不提供飲品</option>
    <option value="cold">僅提供冷飲</option>
    <option value="hot">僅提供熱飲</option>
    <option value="both">冷熱飲皆有</option>
</select>

<!-- 根據選擇動態顯示 -->
<div id="drinkPricesContainer">
    <div id="coldDrinkPriceGroup">  <!-- 選擇cold或both時顯示 -->
        <label>冷飲加價</label>
        <input type="number" id="coldDrinkPrice" value="0">
    </div>
    <div id="hotDrinkPriceGroup">   <!-- 選擇hot或both時顯示 -->
        <label>熱飲加價</label>
        <input type="number" id="hotDrinkPrice" value="0">
    </div>
</div>
```

**JavaScript 邏輯：**
```javascript
function toggleDrinkPrices() {
    const drinkOption = $('#drinkOption').val();
    
    if (drinkOption === 'none') {
        // 隱藏所有價格輸入
        $('#drinkPricesContainer').hide();
    } else if (drinkOption === 'cold') {
        // 只顯示冷飲價格
        $('#drinkPricesContainer').show();
        $('#coldDrinkPriceGroup').show();
        $('#hotDrinkPriceGroup').hide();
    } else if (drinkOption === 'hot') {
        // 只顯示熱飲價格
        $('#drinkPricesContainer').show();
        $('#coldDrinkPriceGroup').hide();
        $('#hotDrinkPriceGroup').show();
    } else if (drinkOption === 'both') {
        // 顯示所有價格輸入
        $('#drinkPricesContainer').show();
        $('#coldDrinkPriceGroup').show();
        $('#hotDrinkPriceGroup').show();
    }
}

// 提交表單時處理
const drinkOption = $('#drinkOption').val();
const data = {
    has_cold_drink: (drinkOption === 'cold' || drinkOption === 'both'),
    cold_drink_price: (drinkOption === 'cold' || drinkOption === 'both') ? parseInt($('#coldDrinkPrice').val()) : null,
    has_hot_drink: (drinkOption === 'hot' || drinkOption === 'both'),
    hot_drink_price: (drinkOption === 'hot' || drinkOption === 'both') ? parseInt($('#hotDrinkPrice').val()) : null
};
```

**編輯頁面初始化：**
```javascript
// 根據現有數據初始化選擇器
{% if product.has_cold_drink and product.has_hot_drink %}
    $('#drinkOption').val('both');
{% elif product.has_cold_drink %}
    $('#drinkOption').val('cold');
{% elif product.has_hot_drink %}
    $('#drinkOption').val('hot');
{% else %}
    $('#drinkOption').val('none');
{% endif %}
toggleDrinkPrices();
```

**更新的文件：**
- ✅ `public/templates/backend/products/add.html`
- ✅ `public/templates/backend/products/edit.html`
- ✅ `public/templates/shop/products/add.html`
- ✅ `public/templates/shop/products/edit.html`

**使用場景：**
```
場景 1：珍珠奶茶（冷熱皆有）
- 選擇：冷熱飲皆有
- 冷飲加價：+5 元
- 熱飲加價：+0 元
→ has_cold_drink=true, cold_drink_price=5, has_hot_drink=true, hot_drink_price=0

場景 2：冰淇淋（僅冷飲）
- 選擇：僅提供冷飲
- 冷飲加價：+0 元
→ has_cold_drink=true, cold_drink_price=0, has_hot_drink=false, hot_drink_price=null

場景 3：漢堡（不提供飲品）
- 選擇：不提供飲品
→ has_cold_drink=false, cold_drink_price=null, has_hot_drink=false, hot_drink_price=null
```

---

## 2025-11-06 18:15 - 移除 Shop Admin 列表的副標題描述

### 🎨 UI 優化

**移除產品列表的描述副標題：**
- ✅ 移除 `/shop/products` 列表中產品名稱下方的描述文字
- ✅ 只顯示產品名稱（簡潔顯示）
- ✅ 描述文字仍保留在新增/編輯頁面

**移除店鋪列表的描述副標題：**
- ✅ 移除 `/shop/shops` 列表中店鋪名稱下方的描述文字
- ✅ 只顯示店鋪名稱（簡潔顯示）
- ✅ 描述文字仍保留在新增/編輯頁面

**修改前：**
```javascript
<td>
    <strong>${product.name}</strong>
    <br><small class="text-muted">這是產品描述...</small>  ❌ 移除
</td>
```

**修改後：**
```javascript
<td>
    <strong>${product.name}</strong>  ✅ 簡潔
</td>
```

**效果對比：**
```
修改前：
┌────┬─────────────────────────┐
│ ID │ 產品名稱                │
├────┼─────────────────────────┤
│ 1  │ 珍珠奶茶                │
│    │ 香濃奶茶加上Q彈珍珠...  │  ← 副標題
└────┴─────────────────────────┘

修改後：
┌────┬──────────┐
│ ID │ 產品名稱 │
├────┼──────────┤
│ 1  │ 珍珠奶茶 │  ← 清爽簡潔
└────┴──────────┘
```

---

## 2025-11-06 18:00 - 修復 Backend 店鋪列表不顯示商店訂單ID

### 🐛 Bug 修復

**Backend 路由缺少 shop_order_id 序列化：**
- ✅ 修復 `app/routes/backend.py` 的 `shops()` 函數
- ✅ 在序列化字典中添加 `'shop_order_id': s.shop_order_id`
- ✅ 現在前端可以正確接收並顯示商店訂單ID

**修復前（缺少字段）：**
```python
shops_data.append({
    'id': s.id,
    'name': s.name,
    'description': s.description,
    'owner_id': s.owner_id,
    # ❌ 缺少 shop_order_id
    'max_toppings_per_order': s.max_toppings_per_order,
    'status': s.status,
    'created_at': s.created_at.isoformat()
})
```

**修復後（添加字段）：**
```python
shops_data.append({
    'id': s.id,
    'name': s.name,
    'description': s.description,
    'shop_order_id': s.shop_order_id,  # ✅ 添加
    'owner_id': s.owner_id,
    'max_toppings_per_order': s.max_toppings_per_order,
    'status': s.status,
    'created_at': s.created_at.isoformat()
})
```

**注意事項：**
- ⚠️ 如果舊店鋪在數據庫中 `shop_order_id` 為 NULL，仍會顯示 "-"
- ⚠️ 需要手動編輯這些店鋪，添加商店訂單ID
- ✅ 新創建的店鋪都必須填入商店訂單ID（已有驗證）

---

## 2025-11-06 17:45 - 店鋪列表添加商店訂單ID列

### ✨ 功能增強

**Backend 店鋪列表增加商店訂單ID列：**
- ✅ 在表頭添加"商店訂單ID"列
- ✅ 在表格中顯示 `shop_order_id`（藍色徽章）
- ✅ 列順序：ID | 店鋪名稱 | 店主 | **商店訂單ID** | 最大配料 | 狀態 | 建立時間 | 操作
- ✅ 更新 colspan 從 7 改為 8

**Shop Admin 店鋪列表統一標題：**
- ✅ 將"訂單ID"改為"商店訂單ID"（與 Backend 一致）
- ✅ 列順序：ID | 店鋪名稱 | **商店訂單ID** | 最大配料 | 狀態 | 建立時間 | 操作

**顯示效果：**
```html
<!-- Backend & Shop Admin -->
<th>商店訂單ID</th>
<!-- ... -->
<td><span class="badge bg-info">${shop.shop_order_id || '-'}</span></td>
```

**範例顯示：**
```
ID | 店鋪名稱      | 店主   | 商店訂單ID | 最大配料 | 狀態   | 建立時間
1  | 珍珠奶茶店    | Admin  | [SHOP01]   | 5       | 營業中 | 2025-11-06
2  | 咖啡小棧      | Store1 | [CAFE01]   | 3       | 營業中 | 2025-11-06
```

---

## 2025-11-06 17:30 - 修復店鋪新增失敗問題

### 🐛 Bug 修復

**移除單店鋪限制：**
- ✅ 移除 `create_shop` API 中的舊限制代碼
- ✅ 舊代碼：`if user.role == 'store_admin' and existing_shop: return error`
- ✅ 現在：允許 shop_admin 創建多個店鋪

**添加 shop_order_id 驗證：**
- ✅ 驗證 `shop_order_id` 為必填欄位
- ✅ 驗證格式：只能使用大寫字母和數字，2-20 個字符
- ✅ 驗證唯一性：檢查是否已被其他店鋪使用
- ✅ 自動轉換為大寫：`shop_order_id.strip().upper()`

**修復代碼：**
```python
# app/routes/api/shops.py - create_shop()

# ❌ 移除舊限制
# if user.role == 'store_admin':
#     existing_shop = Shop.query.filter_by(owner_id=user.id).first()
#     if existing_shop:
#         return error('您已經擁有一個店鋪')

# ✅ 添加 shop_order_id 驗證
shop_order_id = data.get('shop_order_id', '').strip().upper()
if not shop_order_id:
    return error('商店訂單ID不能為空')

# 驗證格式
import re
if not re.match(r'^[A-Z0-9]{2,20}$', shop_order_id):
    return error('格式錯誤')

# 檢查重複
existing_shop_with_order_id = Shop.query.filter_by(
    shop_order_id=shop_order_id
).filter(Shop.deleted_at.is_(None)).first()
if existing_shop_with_order_id:
    return error(f'商店訂單ID "{shop_order_id}" 已被使用')

# 創建店鋪（支持多店鋪）
new_shop = Shop(
    name=name,
    description=description,
    shop_order_id=shop_order_id,  # 新增
    owner_id=owner_id,
    max_toppings_per_order=max_toppings_value,
    status='active'
)
```

---

## 2025-11-06 17:15 - 支持商店管理者擁有多個店鋪

### 🏪 核心業務邏輯變更

**商店管理者多店鋪支持：**
- ✅ 商店管理者（shop_admin）可以擁有**多個店鋪**
- ✅ Backend Admin 和 Shop Admin 權限處理方式完全一致
- ✅ 唯一差異：shop_admin 只能查看/管理 `owner_id = user.id` 的店鋪
- ✅ 恢復配料設置到店鋪新增頁面（與 Backend 一致）

### 📦 產品管理頁面升級

**顯示所有自己的店鋪的產品：**
- ✅ 查詢邏輯：`Product.query.filter(Product.shop_id.in_(shop_ids))`
- ✅ 不再只顯示第一個店鋪的產品
- ✅ 恢復"店鋪"列，顯示產品所屬店鋪名稱
- ✅ 恢復"店鋪篩選器"，可按店鋪過濾產品
- ✅ 列表佈局：ID | 產品名稱 | **店鋪** | 分類 | 價格 | 庫存 | 飲品 | 狀態 | 操作

**產品新增/編輯支持選擇店鋪：**
- ✅ 新增頁面：添加"所屬店鋪"下拉選擇框（必填）
- ✅ 編輯頁面：添加"所屬店鋪"下拉選擇框（可更換店鋪）
- ✅ 只顯示當前用戶擁有的店鋪
- ✅ 提交時包含 `shop_id` 欄位

### 📊 Dashboard 儀表板多店鋪支持

**統計數據為所有店鋪加總：**
- ✅ 產品總數：所有店鋪的產品總和
- ✅ 訂單總數：所有店鋪的訂單總和
- ✅ 待處理/處理中/已完成：所有店鋪統計
- ✅ 最近訂單：顯示所有店鋪的最近訂單

**新增店鋪卡片列表：**
- ✅ 顯示"管理 X 個店鋪"而非單一店鋪名稱
- ✅ 新增"我的店鋪"區塊，以卡片方式展示
- ✅ 每個卡片顯示：店鋪名稱、描述、營業狀態、編輯按鈕

### 🔧 店鋪新增頁面恢復配料設置

**初始配料設置區塊：**
- ✅ 恢復"初始配料"HTML 區塊（與 Backend 完全相同）
- ✅ 支持動態新增/移除配料行
- ✅ 每個配料可設置：名稱、價格、啟用狀態
- ✅ 配料為可選（可留空，後續在編輯頁面添加）
- ✅ 提交時收集 `toppings` 數據並發送到 API

**JavaScript 函數：**
```javascript
addToppingRow()        // 添加配料行
removeToppingRow(btn)  // 移除配料行（保留至少一行）
// 表單提交時自動收集 toppings 數據
data.toppings = toppings;
```

### 📝 代碼實現

**app/routes/store_admin.py:**
```python
@store_admin_bp.route('/products')
def products():
    # 獲取用戶擁有的所有店鋪
    shops_list = Shop.query.filter_by(owner_id=user.id).filter(Shop.deleted_at.is_(None)).all()
    shop_ids = [s.id for s in shops_list]
    
    # 獲取所有自己店鋪的產品
    products_list = Product.query.filter(
        Product.shop_id.in_(shop_ids)
    ).filter(Product.deleted_at.is_(None)).all()
    
    # 序列化為字典（供 JavaScript 使用）
    products_data = [...]
    shops_data = [{'id': s.id, 'name': s.name} for s in shops_list]

@store_admin_bp.route('/dashboard')
def dashboard():
    shops = Shop.query.filter_by(owner_id=user.id).filter(Shop.deleted_at.is_(None)).all()
    shop_ids = [s.id for s in shops]
    
    # 統計所有店鋪的數據
    total_products = Product.query.filter(Product.shop_id.in_(shop_ids)).count()
    total_orders = Order.query.filter(Order.shop_id.in_(shop_ids)).count()
    
    return render_template('shop/dashboard.html',
                         shops=shops,
                         total_shops=len(shops),
                         ...)

@store_admin_bp.route('/products/add')
def product_add():
    shops = Shop.query.filter_by(owner_id=user.id).filter(Shop.deleted_at.is_(None)).all()
    return render_template('shop/products/add.html', shops=shops, ...)

@store_admin_bp.route('/products/<int:product_id>/edit')
def product_edit(product_id):
    shops = Shop.query.filter_by(owner_id=user.id).filter(Shop.deleted_at.is_(None)).all()
    shop_ids = [s.id for s in shops]
    # 檢查產品是否屬於自己的店鋪
    product = Product.query.filter(
        Product.id == product_id,
        Product.shop_id.in_(shop_ids)
    ).first_or_404()
    return render_template('shop/products/edit.html', product=product, shops=shops, ...)
```

**public/templates/shop/products/list.html:**
```html
<!-- 店鋪篩選器 -->
<select id="shopFilter" onchange="performSearch()">
    <option value="">所有店鋪</option>
    {% for shop in shops %}
    <option value="{{ shop.id }}">{{ shop.name }}</option>
    {% endfor %}
</select>

<!-- 表格增加店鋪列 -->
<thead>
    <tr>
        <th>ID</th>
        <th>產品名稱</th>
        <th>店鋪</th>  <!-- 新增 -->
        <th>分類</th>
        <th>價格</th>
        <th>庫存</th>
        <th>飲品</th>
        <th>狀態</th>
        <th>操作</th>
    </tr>
</thead>

<script>
function renderProductRow(product) {
    const shop = allShops.find(s => s.id === product.shop_id);
    const shopName = shop ? shop.name : '-';
    // ... 顯示 shopName ...
}

function performSearch() {
    const shopFilter = document.getElementById('shopFilter').value;
    filteredItems = allProducts.filter(product => {
        const matchShop = !shopFilter || product.shop_id == shopFilter;
        // ... 其他過濾條件 ...
        return matchSearch && matchShop && ...;
    });
}
</script>
```

**public/templates/shop/products/add.html & edit.html:**
```html
<div class="mb-3">
    <label for="productShop">所屬店鋪 <span class="text-danger">*</span></label>
    <select id="productShop" required>
        <option value="">請選擇店鋪</option>
        {% for shop in shops %}
        <option value="{{ shop.id }}" {% if shop.id == product.shop_id %}selected{% endif %}>
            {{ shop.name }}
        </option>
        {% endfor %}
    </select>
</div>

<script>
const data = {
    name: $('#productName').val(),
    shop_id: parseInt($('#productShop').val()),  // 現在是動態選擇
    category_id: parseInt($('#productCategory').val()),
    // ...
};
</script>
```

**public/templates/shop/dashboard.html:**
```html
<div class="hero-section">
    <h1>歡迎回來，{{ user.name }}！</h1>
    <p>管理 {{ total_shops }} 個店鋪</p>
</div>

<!-- 我的店鋪列表 -->
{% if shops %}
<div class="mb-4">
    <h2>我的店鋪</h2>
    <div class="row">
        {% for shop in shops %}
        <div class="col-md-4 mb-3">
            <div class="card h-100">
                <div class="card-body">
                    <h5>{{ shop.name }}</h5>
                    <p class="text-muted">{{ shop.description[:60] }}...</p>
                    <span class="badge">{{ shop.status }}</span>
                    <a href="{{ url_for('store_admin.shop_edit', shop_id=shop.id) }}" 
                       class="btn btn-sm btn-outline-primary">
                        <i class="bi bi-pencil"></i> 編輯
                    </a>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endif %}
```

**public/templates/shop/shops/add.html:**
```html
<!-- 恢復初始配料區塊 -->
<hr class="my-4">
<h5 class="mb-3">
    <i class="bi bi-list-ul me-2"></i>初始配料
    <button type="button" class="btn btn-sm btn-outline-primary ms-2" onclick="addToppingRow()">
        <i class="bi bi-plus-circle me-1"></i>添加配料
    </button>
</h5>

<div id="toppingsContainer">
    <div class="row mb-2 topping-row">
        <div class="col-md-3">
            <input type="text" class="form-control topping-name" placeholder="配料名稱（例如：珍珠）">
        </div>
        <div class="col-md-2">
            <input type="number" class="form-control topping-price" placeholder="價格" min="0" value="0">
        </div>
        <div class="col-md-2">
            <div class="form-check form-switch">
                <input class="form-check-input topping-active" type="checkbox" checked>
                <label>啟用</label>
            </div>
        </div>
        <div class="col-md-5">
            <button type="button" class="btn btn-outline-danger w-100" onclick="removeToppingRow(this)">
                <i class="bi bi-trash"></i> 移除
            </button>
        </div>
    </div>
</div>
<small>配料可選填，也可在店鋪創建後再添加</small>

<script>
function addToppingRow() { /* ... */ }
function removeToppingRow(btn) { /* ... */ }

$('#shopForm').on('submit', function(e) {
    // 收集 Toppings
    const toppings = [];
    $('.topping-row').each(function() {
        const name = $(this).find('.topping-name').val().trim();
        if (name) {
            toppings.push({
                name: name,
                price: parseInt($(this).find('.topping-price').val()) || 0,
                is_active: $(this).find('.topping-active').is(':checked')
            });
        }
    });
    data.toppings = toppings;
});
</script>
```

### 🎯 權限控制總結

| 功能 | Backend Admin | Shop Admin |
|------|---------------|------------|
| 查看店鋪 | 所有店鋪 | `owner_id = user.id` |
| 查看產品 | 所有產品 | `shop_id.in_(user.shop_ids)` |
| 新增店鋪 | 可選擇店主 | 自動為當前用戶 |
| 新增產品 | 可選擇店鋪 | 只能選擇自己的店鋪 |
| 編輯產品 | 可更換店鋪 | 可更換為自己的其他店鋪 |
| 店鋪數量 | 無限制 | 無限制（多店鋪） ✅ |

---

## 2025-11-06 16:30 - Shop Admin 頁面完全對齊 Backend 設計

### 🐛 Bug 修復

**JSON 序列化錯誤修復：**
- ✅ 修復 `TypeError: Object of type Shop is not JSON serializable`
- ✅ 修復 `TypeError: Object of type Product is not JSON serializable`
- ✅ store_admin.py 的 shops() 函數現在序列化對象為字典
- ✅ store_admin.py 的 products() 函數現在序列化對象為字典
- ✅ 與 Backend 的實現方式完全一致

**模板字段修復：**
- ✅ 移除 products/edit.html 中的"所屬店鋪"下拉選單
- ✅ 移除 products/edit.html 中的"管理分類"齒輪按鈕
- ✅ 移除 JavaScript 中對 `$('#productShop')` 的引用
- ✅ 編輯產品時不允許修改所屬店鋪（shop_id 固定）
- ✅ 將 shops/edit.html 中的"店主"改為禁用的文本框（不可修改）
- ✅ 移除 JavaScript 中對 `owner_id` 的提交
- ✅ 店鋪擁有者不可更改（shop_admin 只能管理，不能轉讓）

**路由引用修復：**
- ✅ 修復 `BuildError: Could not build url for endpoint 'store_admin.toppings'`
- ✅ 移除 dashboard.html 中的"配料管理"快速操作按鈕
- ✅ 改為"店鋪管理"按鈕
- ✅ 所有 `url_for('store_admin.toppings')` 引用已移除

**產品列表頁面修復：**
- ✅ 移除"店鋪"欄位，改為"飲品"欄位
- ✅ 顯示飲品圖標（🧊 冷飲、☕ 熱飲）
- ✅ 移除"所有店鋪"篩選下拉選單
- ✅ 移除"詳情"按鈕
- ✅ 修改所有 `/backend/` 路径為 `/shop/`
- ✅ 編輯按鈕連結：`/shop/products/${id}/edit`
- ✅ JavaScript 過濾移除 `matchShop` 條件

**店鋪新增頁面配料設置：**
- ✅ 恢復"初始配料"設置區塊（與 Backend 相同）
- ✅ 支持添加多個配料（動態新增/移除行）
- ✅ 每個配料可設置：名稱、價格、啟用狀態
- ✅ 配料為可選（可留空，後續在編輯頁面添加）
- ✅ 提交時收集 toppings 數據並發送到 API

**序列化實現：**
```python
# 將 SQLAlchemy 對象轉為字典
shops_data = []
for s in shops_list:
    shops_data.append({
        'id': s.id,
        'name': s.name,
        'shop_order_id': s.shop_order_id,
        # ... 其他欄位
    })
return render_template('...', shops=shops_data)
```

### 🔄 重大重構

**完全複製 Backend 實現：**
- ✅ `/shop` 的店鋪管理和產品管理完全複製 `/backend` 的設計
- ✅ 採用相同的頁面結構（list.html, add.html, edit.html）
- ✅ 採用相同的表格樣式和按鈕排列
- ✅ 採用相同的表單佈局和驗證邏輯
- ✅ 唯一差異：權限過濾（`owner_id` 和 `shop_id`）

### ⚡ 簡化功能

**移除功能：**
- ❌ 刪除「店鋪設定」功能（合併到店鋪管理）
- ❌ 刪除「配料管理」功能（簡化操作流程）

**保留功能：**
- ✅ 儀表板（Dashboard）
- ✅ 店鋪管理（Shops - list/add/edit）
- ✅ 產品管理（Products - list/add/edit）
- ✅ 訂單管理（Orders）
- ✅ 統計（Statistics）

### 📂 最終頁面結構

```
/shop (Store Admin 店主後台)
├── shops/
│   ├── list.html     ← 完全複製 backend/shops/list.html
│   ├── add.html      ← 複製並移除"選擇店主"欄位
│   └── edit.html     ← 完全複製 backend/shops/edit.html
│
└── products/
    ├── list.html     ← 完全複製 backend/products/list.html
    ├── add.html      ← 複製並移除"選擇店鋪"欄位
    └── edit.html     ← 完全複製 backend/products/edit.html

所有頁面：
  - extends "base/shop_base.html" (非 backend_base.html)
  - url_for('store_admin.xxx') (非 backend.xxx)
  - 權限過濾：owner_id = user.id, shop_id = shop.id
```

### 🎨 側邊欄導航（最終版）

```
儀表板（Dashboard）
店鋪管理（Shops）        ← list/add/edit
產品管理（Products）      ← list/add/edit
訂單管理（Orders）
統計（Statistics）
```

**移除項目：**
- ❌ 店鋪設定（Profile）- 功能已合併到店鋪管理
- ❌ 配料管理（Toppings）- 簡化操作流程

### 🆚 與 Backend 的對比

**完全相同：**
- ✅ 頁面結構（list.html, add.html, edit.html）
- ✅ 表格樣式和佈局
- ✅ 表單設計和驗證
- ✅ Banner 上傳功能
- ✅ 圖片管理功能
- ✅ 飲品選項設置
- ✅ 軟刪除實現

**僅修改：**
- ✅ 模板繼承：`backend_base.html` → `shop_base.html`
- ✅ 路由引用：`url_for('backend.xxx')` → `url_for('store_admin.xxx')`
- ✅ 權限過濾：添加 `filter_by(owner_id=user.id)`
- ✅ 簡化欄位：移除「選擇店主」、「選擇店鋪」
- ✅ 調整篩選：移除「店主篩選」、「店鋪篩選」

### 📊 側邊欄對比

```
Backend (9 項)               Shop Admin (5 項)
─────────────────────────────────────────────
儀表板                      儀表板
用戶管理 ✘                  
店鋪管理                    店鋪管理 ✓
產品管理                    產品管理 ✓
訂單管理 ✘                  訂單管理 ✓
分類管理 ✘                  
首頁管理 ✘                  
內容管理 ✘                  
系統設定 ✘                  統計 ✓
```

### 📚 新增文檔

- ✅ `docs/BACKEND_VS_SHOP.md` - Backend 和 Shop Admin 詳細對比說明
  - 設計理念對比
  - 頁面結構對比
  - 功能對比表格
  - 權限實現對比
  - 數據流對比
  - UI/UX 差異
  - shop_id 和 owner_id 處理說明
- ✅ `TEST_CHECKLIST.md` - 完整測試清單（60+ 測試項目）
  - 店鋪管理測試（列表/新增/編輯）
  - 產品管理測試（列表/新增/編輯/飲品）
  - 權限隔離測試
  - 軟刪除測試
  - UI/UX 一致性測試
  - 完整業務流程測試
  - 測試報告模板

---

## 2025-11-06 16:00 - 店鋪列表管理 & 軟刪除功能 & 獨立頁面重構

### ✨ 新增功能

**🏪 店鋪列表管理（Store Admin）**
- ✅ 新增 `/shop/shops` 路由 - 店主的店鋪列表頁面
- ✅ 店主可以查看自己擁有的所有店鋪
- ✅ 支持搜尋（名稱、描述）
- ✅ 支持狀態篩選（營業中/已關閉）
- ✅ 採用獨立頁面設計（list.html, add.html, edit.html）
- ✅ 新增店鋪頁面（`/shop/shops/add`）
- ✅ 編輯店鋪頁面（`/shop/shops/<id>/edit`）
- ✅ 軟刪除店鋪功能

**📦 產品管理頁面重構（Store Admin）**
- ✅ 將模態框改為獨立頁面（參考 Backend 設計）
- ✅ 產品列表頁面（`shop/products/list.html`）
- ✅ 新增產品頁面（`shop/products/add.html`）
- ✅ 編輯產品頁面（`shop/products/edit.html`）
- ✅ 包含完整的飲品選項設置
- ✅ 表格顯示飲品圖標（🧊 冷飲、☕ 熱飲）

**🗑️ 軟刪除系統**
- ✅ Shop 模型新增 `deleted_at` 字段（DateTime, nullable）
- ✅ Product 模型新增 `deleted_at` 字段（DateTime, nullable）
- ✅ 刪除操作改為設置 `deleted_at` 時間戳，而非真實刪除
- ✅ 產品軟刪除同時設置 `is_active = False`
- ✅ 軟刪除後可在後台恢復

**🔍 查詢過濾更新**
- ✅ 所有店鋪查詢添加 `.filter(Shop.deleted_at.is_(None))`
- ✅ 所有產品查詢添加 `.filter(Product.deleted_at.is_(None))`
- ✅ 前台（Customer）無法看到已刪除的店鋪和產品
- ✅ 店主（Store Admin）無法看到已刪除的店鋪和產品
- ✅ 管理員（Admin）可以查看所有記錄（包含已刪除）

### 🎨 UI/UX 改進

**店鋪列表頁面：**
- ✅ 仿照 Backend 的設計風格
- ✅ 表格顯示：ID、店鋪名稱、訂單ID、最大配料、狀態、建立時間
- ✅ 操作按鈕：詳情、編輯、刪除（一排顯示）
- ✅ 空狀態提示：「您還沒有店鋪，點擊『新增店鋪』開始建立！」

**側邊欄更新：**
```
儀表板
店鋪管理    ← 新增（列表）
店鋪設定    ← 改名（原「店鋪資訊」）
產品管理    ← 改為獨立頁面
配料管理
訂單管理
統計
```

**頁面結構（參考 Backend 設計）：**
```
shop/
├── shops/
│   ├── list.html    ← 店鋪列表（搜尋、篩選、操作按鈕）
│   ├── add.html     ← 新增店鋪（獨立頁面）
│   └── edit.html    ← 編輯店鋪（獨立頁面 + 刪除按鈕）
│
└── products/
    ├── list.html    ← 產品列表（搜尋、分類、狀態篩選）
    ├── add.html     ← 新增產品（含飲品選項設置）
    └── edit.html    ← 編輯產品（含飲品選項設置 + 刪除按鈕）
```

**路由結構：**
```
店鋪管理：
  GET  /shop/shops           → list.html
  GET  /shop/shops/add       → add.html
  GET  /shop/shops/<id>/edit → edit.html

產品管理：
  GET  /shop/products           → list.html
  GET  /shop/products/add       → add.html
  GET  /shop/products/<id>/edit → edit.html
```

### 🗄️ 數據庫變更
- ✅ 創建遷移：`add_soft_delete_fields_to_shop_and_product`
- ✅ Shop 表新增：`deleted_at` (DATETIME, NULL)
- ✅ Product 表新增：`deleted_at` (DATETIME, NULL)
- ✅ 為 `deleted_at` 添加索引（提升查詢效率）

### 🔄 API 更新

**軟刪除實現：**
```python
# DELETE /api/shops/<id>
shop.deleted_at = datetime.utcnow()

# DELETE /api/products/<id>
product.deleted_at = datetime.utcnow()
product.is_active = False
```

**查詢過濾：**
```python
# 所有店鋪查詢
Shop.query.filter(Shop.deleted_at.is_(None))

# 所有產品查詢
Product.query.filter(Product.deleted_at.is_(None))
```

### 📊 權限控制確認

**店主（Store Admin）**
- ✅ 只能查看 `owner_id = user.id` 的店鋪
- ✅ 只能編輯自己擁有的店鋪
- ✅ 只能刪除自己擁有的店鋪
- ✅ 只能管理自己店鋪的產品（`shop_id` 過濾）

**管理員（Admin）**
- ✅ 可以查看所有店鋪（包含已刪除）
- ✅ 可以編輯任何店鋪
- ✅ 可以刪除任何店鋪
- ✅ 可以恢復已刪除的店鋪

### 🔒 安全性提升

- ✅ 軟刪除避免誤刪重要數據
- ✅ 刪除操作記錄在 `update_log` 表
- ✅ 刪除確認提示：「此操作可以在後台恢復」
- ✅ 防止重複刪除（檢查 `deleted_at` 是否已存在）
- ✅ 所有公開查詢自動排除已刪除記錄

### 📝 日誌記錄

軟刪除操作記錄為：
```python
log_update(
    action='soft_delete',  # 區分硬刪除
    table_name='shop',
    record_id=shop.id,
    old_data={...},
    description=f'軟刪除店鋪: {shop.name}'
)
```

### 📂 檔案變更

**新增檔案：**
- `public/templates/shop/shops/list.html` - 店鋪列表頁面
- `public/templates/shop/shops/add.html` - 新增店鋪頁面
- `public/templates/shop/shops/edit.html` - 編輯店鋪頁面
- `public/templates/shop/products/list.html` - 產品列表頁面
- `public/templates/shop/products/add.html` - 新增產品頁面（含飲品選項）
- `public/templates/shop/products/edit.html` - 編輯產品頁面（含飲品選項）
- `docs/PERMISSIONS.md` - 權限管理架構文檔（1000+ 行）
- `docs/SHOP_ADMIN_GUIDE.md` - 店主管理後台使用指南（完整操作流程）
- `docs/QUICK_REFERENCE.md` - 快速參考卡片（頁面結構對比、權限對比、路由查找）

**刪除檔案：**
- `public/templates/shop/shops.html` - 舊模態框版本
- `public/templates/shop/products.html` - 舊模態框版本

**修改檔案：**
- `app/models.py` - Shop & Product 添加 deleted_at
- `app/routes/store_admin.py` - 新增 shop_add, shop_edit, product_add, product_edit 路由
- `app/routes/api/shops.py` - 軟刪除實現
- `app/routes/api/products.py` - 軟刪除實現
- `app/routes/customer.py` - 查詢過濾
- `public/templates/base/shop_base.html` - 側邊欄導航更新

---

## 2025-11-06 15:45 - 權限管理架構文檔

### 📚 新增文檔
- ✅ 創建 `docs/PERMISSIONS.md` - 完整的權限管理架構說明（1000+ 行）
- ✅ 詳細說明三種角色的權限範圍
- ✅ 說明權限實現方式（路由層級 + API 層級）
- ✅ 提供權限檢查檢查清單
- ✅ 包含測試場景和測試方法
- ✅ 提供安全建議和最佳實踐
- ✅ 創建 `test_permissions.py` - 權限測試腳本
- ✅ 更新 `README.md` - 添加權限管理章節和流程圖

### 🔐 權限架構說明

**核心原則：**
```
Admin (超級管理員)
  └─ 可以訪問所有資源

Store Admin (店主)
  └─ 只能訪問 owner_id = user.id 的店鋪
  └─ 只能訪問 shop_id 屬於自己店鋪的產品/訂單/配料

Customer (顧客)
  └─ 只能訪問 user_id = user.id 的訂單
  └─ 可以瀏覽所有公開的店鋪和產品
```

**實現方式：**
- 🛡️ 路由層級：`@role_required('store_admin')` 裝飾器
- 🛡️ API 層級：檢查 `owner_id` 和 `shop_id`
- 🛡️ 查詢過濾：`Shop.query.filter_by(owner_id=user.id)`
- 🛡️ 智能重定向：根據路由重定向到對應登入頁

**文檔內容：**
- 三種角色的詳細權限說明
- 路由和 API 的權限實現範例
- 裝飾器使用說明
- 關鍵過濾模式表格
- 權限檢查檢查清單
- 測試場景和測試代碼
- 安全建議（5 條最佳實踐）

---

## 2025-11-06 15:30 - README.md 完整更新

### 📚 文檔更新
- ✅ 完整重寫 README.md（從 188 行擴充至 1000+ 行）
- ✅ 新增完整的功能特性說明
- ✅ 新增系統架構圖和資料模型關係圖
- ✅ 新增詳細的安裝和配置指南
- ✅ 新增三個角色的完整操作手冊：
  - 後台管理（Admin）操作指南
  - 店鋪管理（Store Admin）操作指南  
  - 商城前台（Customer）操作指南
- ✅ **重點說明飲品選項功能的完整使用流程** ⭐
- ✅ 新增 API 完整文檔和範例
- ✅ 新增 WebSocket 事件說明和範例代碼
- ✅ 新增詳細的專案結構樹狀圖
- ✅ 新增常見問題解答（FAQ）
- ✅ 新增貢獻指南和代碼規範

### 📖 操作手冊亮點
- 訂單編號系統完整說明（前綴 + 商店ID + 日期 + 流水號）
- 飲品選項設定和使用的完整流程（店主端 + 顧客端）
- 價格計算公式詳細說明
- 購物流程圖示（選擇 → 購物車 → 結帳 → 訂單）
- 即時通知系統使用說明（聲音 + 橫幅）
- 配料和飲品的差異說明（Checkbox vs Radio）

### 📊 文檔結構
```
README.md
├── 功能特性（核心功能、權限管理、即時功能）
├── 系統架構（角色權限圖、資料模型關係圖）
├── 技術棧（後端、前端、資料庫）
├── 安裝說明（7步驟詳細指南）
├── 使用指南（預設帳號、訪問路徑）
├── 操作手冊 ⭐
│   ├── 後台管理（系統設定、Banner、內容管理、商店管理）
│   ├── 店鋪管理（商品管理、配料管理、訂單管理）
│   │   └── 飲品選項詳細說明 ⭐⭐⭐
│   └── 商城前台（註冊登入、瀏覽商品、查看詳情、結帳）
├── API 文檔（認證、商品、購物車、訂單）
├── WebSocket 事件（連接、監聽、範例代碼）
├── 專案結構（完整目錄樹）
└── 常見問題（8個常見問題和解決方案）
```

---

## 2025-11-06 15:20 - 商品冷飲/熱飲選項功能

### ✨ 新增功能

**🥤 商品飲品選項系統**
- ✅ Product 模型新增冷飲/熱飲字段：
  - `has_cold_drink`: 是否提供冷飲（Boolean）
  - `cold_drink_price`: 冷飲加價（Decimal）
  - `has_hot_drink`: 是否提供熱飲（Boolean）
  - `hot_drink_price`: 熱飲加價（Decimal）
- ✅ OrderItem 模型新增飲品記錄字段：
  - `drink_type`: 飲品類型（'cold'/'hot'/null）
  - `drink_price`: 飲品價格（Decimal）

**🛠️ 後台商品管理**
- ✅ 商品添加/編輯表單新增飲品選項區塊
- ✅ 勾選「提供冷飲」/「提供熱飲」可設定加價（預設 0）
- ✅ 飲品選項為可選功能，非必填
- ✅ 價格輸入框動態顯示/隱藏
- ✅ 編輯時自動載入現有飲品設定

**🛍️ 前台購物體驗**
- ✅ 商品詳情模態框新增「飲品選擇」區塊
- ✅ 顯示冷飲（🧊）和熱飲（☕）選項
- ✅ 顯示飲品加價（+$XX）或免費
- ✅ 包含「不需要」選項（預設選中）
- ✅ 總價計算自動包含飲品價格
- ✅ 購物車顯示選擇的飲品類型和價格
- ✅ 結帳頁面保留飲品選擇信息

**📦 訂單系統整合**
- ✅ 訂單 API 接收並保存飲品選擇
- ✅ 飲品價格計入訂單總價
- ✅ 訂單詳情頁顯示飲品信息（前台 & 後台）
- ✅ 飲品數據正確傳遞給店主

### 🗄️ 數據庫變更
- ✅ 創建遷移：`add_drink_options_to_product_and_order_item`
- ✅ 為現有產品設置預設值（has_cold_drink=0, has_hot_drink=0）
- ✅ 新增字段均可為 NULL（兼容舊數據）

### 🔄 API 更新
- ✅ GET `/api/products/`: 返回飲品字段
- ✅ GET `/api/products/<id>`: 返回完整飲品信息
- ✅ POST `/api/products`: 支持創建時設置飲品
- ✅ PUT `/api/products/<id>`: 支持更新飲品設置
- ✅ POST `/api/cart/add`: 接收 drink_type 和 drink_price
- ✅ POST `/api/orders`: 保存飲品數據到 OrderItem

### 💰 價格計算邏輯
```
總價 = (商品基礎價 + 配料總價 + 飲品價格) × 數量
```

### 📱 UI/UX 改進
- ✅ 飲品選項使用 Radio 按鈕（單選）
- ✅ 配料選項使用 Checkbox（多選，有上限）
- ✅ 清晰的圖標：🧊 冷飲、☕ 熱飲
- ✅ 訂單詳情使用彩色徽章顯示飲品
- ✅ 購物車完整顯示飲品和配料信息

---

## 2025-11-06 02:30 - 店鋪產品卡片交互優化 & 店主訂單通知改進

### 🎨 產品卡片交互改進
- ✅ 產品圖片可點擊（打開詳情模態框）
- ✅ 產品名稱可點擊（打開詳情模態框）
- ✅ 圖片懸停效果：
  - 半透明黑色遮罩（rgba(0,0,0,0.5)）
  - 白色眼睛圖標（👁️ 3rem）
  - 平滑過渡動畫（0.3秒）
- ✅ 標題懸停時鼠標變為手型（cursor: pointer）
- ✅ 統一交互方式：圖片、標題、按鈕都可打開詳情

### 🔔 店主訂單通知系統改進（頂部橫幅統一通知）
- ✅ 移除 Toast 彈出通知
- ✅ 移除 Alert 彈窗
- ✅ 統一使用頂部橫幅通知（所有頁面）
- ✅ 頂部橫幅設計：
  - 綠色 Alert 樣式（alert-success）
  - 左側 4px 綠色邊框
  - 滑下動畫（slideDown，0.5秒）
  - 淺綠色陰影效果
  - 訂單編號（藍色徽章）
  - 訂單金額（綠色粗體）
  - 接收時間（剛剛收到）
  - 訂單狀態（待處理徽章）
  - 「查看訂單」按鈕（綠色）
  - 「關閉」按鈕
- ✅ 自動隱藏：10秒後自動收起
- ✅ 鈴鐺點擊功能：
  - 關閉頂部橫幅
  - 立即隱藏紅點
  - 跳轉到訂單管理頁面
- ✅ 鈴鐺紅點樣式優化：
  - 純紅點顯示（不顯示數字）
  - 圓形紅點（10px × 10px）
  - 位置調整（右上角，與鈴鐺有距離）
- ✅ 紅點顯示邏輯：
  - 點擊鈴鐺後紅點消失
  - 只有收到新訂單時紅點才再次出現
  - 使用 `shouldShowRedDot` 標誌控制
- ✅ WebSocket 通知包含 `order_number`
- ✅ 鈴鐺震動動畫（所有頁面）
- ✅ 提示音播放（所有頁面，音量 50%，立即播放）
- ✅ 紅點徽章更新（所有頁面）
- ✅ 訂單狀態更新時自動刷新頁面（訂單管理頁面）
- ✅ 所有頁面統一顯示方式（無 Alert 干擾）

### 🔧 新增 API 端點
- ✅ `GET /api/shops/my-shops` - 獲取當前用戶的店鋪列表
  - 管理員：返回所有店鋪
  - 店主：返回自己的店鋪
  - 普通用戶：返回空列表

### 🎯 通知流程改進
```
【修改前】Toast 方式
顧客下單 → WebSocket → Toast 彈窗右上角 → 8秒後消失

【修改後】頂部橫幅通知方式
顧客下單 → WebSocket → 所有頁面統一處理
  ↓
  ├─ 頂部橫幅從上滑下
  ├─ 鈴鐺震動 0.8秒
  ├─ 鈴鐺變紅色
  ├─ 紅點徽章顯示數字
  ├─ 播放提示音
  └─ 10秒後自動隱藏
```

### 🎨 橫幅顯示效果
```
┌──────────────────────────────────────────────────────────┐
│ 🔔  新訂單通知                                            │
│     ┌────────────────────────┐                           │
│     │ 訂單編號：ORDERBAO2025110600001                    │
│     │ 訂單金額：$150          待處理                      │
│     │ 🕐 剛剛收到                                         │
│     └────────────────────────┘                           │
│                               [查看訂單] [✕]              │
└──────────────────────────────────────────────────────────┘
```

### 📊 通知方式對比

| 特性 | Toast（舊） | 頂部橫幅（新） |
|------|-----------|---------------|
| **觸發** | 所有頁面 | 所有頁面 |
| **位置** | 右上角彈窗 | 頁面內容最頂部 |
| **消失** | 8秒自動消失 | 10秒自動+手動關閉 |
| **可見性** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **訊息量** | 有限 | 豐富（編號+金額+狀態） |
| **操作** | 按鈕查看 | 按鈕查看+手動關閉 |
| **干擾性** | 中 | 低（嵌入頁面頂部） |
| **遺漏風險** | 高（可能錯過） | 低（醒目位置） |

### 🐛 Bug 修復
- ✅ 移除 `shop/dashboard.html` 中舊的 Alert 彈窗代碼
- ✅ 避免重複通知（舊 window.addEventListener 與新 socket.on 衝突）
- ✅ 新增調試日誌（console.log）幫助診斷紅點顯示問題

### 🔄 修改文件
- ✅ `public/templates/store/shop.html` - 產品卡片交互優化
- ✅ `public/templates/base/shop_base.html` - 移除 Toast，頂部橫幅通知，紅點邏輯，調試日誌
- ✅ `public/templates/shop/dashboard.html` - 移除舊 Alert 代碼
- ✅ `app/routes/api/orders.py` - WebSocket 通知包含 order_number
- ✅ `app/routes/api/shops.py` - 新增 `/my-shops` 端點

### 🎯 用戶體驗提升

**產品卡片**：
```
【修改前】
- 只有底部「查看詳情」按鈕可點擊
- 標題鏈接跳轉到產品頁面
- 圖片不可點擊

【修改後】
- 圖片可點擊 → 打開詳情模態框
- 標題可點擊 → 打開詳情模態框
- 按鈕可點擊 → 打開詳情模態框
- 圖片懸停顯示眼睛圖標提示
```

**訂單通知**：
```
【修改前】
- Toast 彈窗（8秒消失）
- 位置不明顯
- 可能錯過通知

【修改後】
- 頂部橫幅（所有頁面統一）
- 位置最醒目（內容區域最上方）
- 10秒自動隱藏+手動關閉
- 不會錯過通知
```

### ✨ 新功能
- ✅ 頂部橫幅通知（統一方式）
- ✅ 訂單編號顯示在橫幅中
- ✅ 訂單狀態徽章
- ✅ 直接查看訂單按鈕
- ✅ 手動關閉功能
- ✅ 10秒自動隱藏
- ✅ 鈴鐺點擊智能處理（關閉橫幅+重算數量+跳轉）
- ✅ 提示音無條件播放（所有頁面）
- ✅ 訂單頁面自動刷新（狀態更新時）
- ✅ `/api/shops/my-shops` API 端點

---

## 2025-11-06 02:00 - 訂單編號系統 & 系統設定管理

### 📋 訂單編號系統
- ✅ Order 模型新增 `order_number` 字段（VARCHAR(50), UNIQUE, NOT NULL）
- ✅ 訂單編號格式：`前綴 + 商店訂單ID + Ymd + 流水號`
- ✅ 示例：`ORDERBAO2025110600001`
  - `ORDER` - 訂單前綴（可在系統設定修改）
  - `BAO` - 商店訂單ID（每個店鋪必填，全局唯一）
  - `20251106` - 日期（年月日）
  - `00001` - 當日流水號（5位數，00001-99999）
- ✅ 自動生成訂單編號（創建訂單時）
- ✅ 流水號每日自動重置
- ✅ 已有訂單自動生成歷史編號（遷移時執行）

### 🏪 商店訂單ID系統
- ✅ Shop 模型新增 `shop_order_id` 字段（VARCHAR(20), UNIQUE, NOT NULL）
- ✅ 商店訂單ID為必填字段
- ✅ 格式驗證：只能包含大寫字母和數字
- ✅ 長度驗證：2-20 個字符
- ✅ 唯一性驗證：不能與其他店鋪重複
- ✅ 自動轉大寫
- ✅ 後台店鋪編輯頁面新增輸入框
- ✅ 創建和更新店鋪時驗證
- ✅ 示例：BAO, S01, DUMPLING, NOODLE

### ⚙️ 系統設定管理
- ✅ 創建 SystemSetting 模型（設定鍵值對系統）
- ✅ 支持多種類型：text, number, boolean, json
- ✅ 按分類管理：order（訂單）, email（郵件）, general（通用）
- ✅ 靜態方法：
  - `SystemSetting.get(key, default)` - 獲取設定（自動類型轉換）
  - `SystemSetting.set(key, value, ...)` - 設置值（自動類型檢測）
- ✅ 後台系統設定頁面（`/backend/settings`）
- ✅ 標籤頁設計：訂單設定、郵件設定
- ✅ 系統設定 API（GET, POST, PUT, DELETE, BATCH）

### 📧 郵件配置預設
- ✅ 預設 Gmail SMTP 配置：
  - `mail_host`: smtp.gmail.com
  - `mail_port`: 587
  - `mail_username`: renfu.her@gmail.com
  - `mail_password`: cpvyctpwnnxfxaqb
  - `mail_encryption`: tls
  - `mail_from_address`: renfu.her@gmail.com
  - `mail_from_name`: Food Stores
- ✅ Gmail 應用專用密碼提示
- ✅ 批量儲存功能

### 🎨 系統設定頁面功能
- ✅ **訂單設定標籤頁**：
  - 訂單編號前綴輸入框（可修改）
  - 實時預覽訂單編號格式
  - 前綴驗證（大寫字母+數字，2-20字符）
  - 格式說明和示例
- ✅ **郵件設定標籤頁**：
  - SMTP 完整配置表單
  - 主機、端口、用戶名、密碼
  - 加密方式選擇（TLS/SSL）
  - 發件人郵箱和名稱
  - Gmail 設定提示

### 🔧 訂單編號生成邏輯
- ✅ 創建訂單編號生成工具（`app/utils/order_number.py`）
- ✅ `generate_order_number(shop_id)` 函數
- ✅ 從 SystemSetting 讀取訂單前綴
- ✅ 使用 shop.shop_order_id（必填）
- ✅ 計算當日該店鋪訂單數量
- ✅ 生成5位流水號（00001-99999）
- ✅ 唯一性檢查（防止重複）
- ✅ 訂單創建時自動調用

### 🗄️ 數據庫變更

**新增表**：
- `system_setting` - 系統設定表
  - setting_key (VARCHAR(100), UNIQUE)
  - setting_value (TEXT)
  - setting_type (VARCHAR(20))
  - description (VARCHAR(500))
  - category (VARCHAR(50))
  - is_encrypted (BOOLEAN)

**Shop 表新增字段**：
- `shop_order_id` (VARCHAR(20), UNIQUE, NOT NULL) - 商店訂單ID

**Order 表新增字段**：
- `order_number` (VARCHAR(50), UNIQUE, NOT NULL) - 訂單編號

**索引**：
- `ix_shop_shop_order_id` - 商店訂單ID唯一索引
- `ix_order_order_number` - 訂單編號唯一索引
- `ix_system_setting_setting_key` - 設定鍵唯一索引
- `idx_setting_category` - 設定分類索引

### 📁 新增文件
- ✅ `app/utils/order_number.py` - 訂單編號生成工具
- ✅ `app/routes/api/system_settings.py` - 系統設定 API
- ✅ `public/templates/backend/settings.html` - 系統設定頁面
- ✅ `migrations/versions/8668db9120be_add_order_number_and_system_settings.py` - 訂單編號+系統設定遷移
- ✅ `migrations/versions/66628b571df0_add_shop_order_id_to_shop.py` - 商店訂單ID遷移
- ✅ `migrations/versions/53a409aac578_make_shop_order_id_required.py` - 商店訂單ID必填遷移

### 🔄 修改文件
- ✅ `app/models.py` - Order 添加 order_number，Shop 添加 shop_order_id，新增 SystemSetting 模型
- ✅ `app/__init__.py` - 註冊 system_settings_api_bp
- ✅ `app/routes/backend.py` - 新增 `/settings` 路由
- ✅ `app/routes/api/orders.py` - 導入並使用 generate_order_number
- ✅ `app/routes/api/shops.py` - 驗證 shop_order_id 必填和唯一性
- ✅ `app/utils/order_number.py` - 使用 shop_order_id 生成編號
- ✅ `public/templates/base/backend_base.html` - 新增系統設定菜單
- ✅ `public/templates/backend/shops/edit.html` - 新增商店訂單ID輸入框（必填）
- ✅ `public/templates/backend/settings.html` - 訂單編號格式說明更新

### 📊 訂單編號示例對比

| 店鋪 | 商店訂單ID | 訂單編號 |
|------|-----------|---------|
| 包子鋪 | BAO | `ORDERBAO2025110600001` |
| 小籠包 | XLB | `ORDERXLB2025110600001` |
| 餃子館 | DUMPLING | `ORDERDUMPLING2025110600001` |
| 麵館 | NOODLE | `ORDERNOODLE2025110600001` |

### 🎯 使用流程

**設置商店訂單ID**：
1. 後台管理 → 店鋪管理 → 編輯店鋪
2. 填寫「商店訂單ID」（必填）
3. 只能使用大寫字母和數字（2-20字符）
4. 保存後該店鋪的訂單將使用此ID

**修改訂單前綴**：
1. 後台管理 → 系統設定
2. 訂單設定標籤頁
3. 修改「訂單編號前綴」
4. 保存後新訂單使用新前綴

**配置郵件**：
1. 後台管理 → 系統設定
2. 郵件設定標籤頁
3. 填寫 SMTP 完整配置
4. 保存後系統可發送郵件

### 🔒 驗證和安全
- ✅ 商店訂單ID全局唯一性檢查
- ✅ 訂單編號全局唯一性保證
- ✅ 格式驗證（正則表達式）
- ✅ 長度限制
- ✅ 必填驗證
- ✅ 前後端雙重驗證

### ✨ 特色功能
- ✅ 訂單編號可讀性高（包含店鋪標識）
- ✅ 訂單編號可追溯（包含日期信息）
- ✅ 每日流水號自動重置
- ✅ 系統設定靈活可配置
- ✅ 支持批量更新設定
- ✅ 設定值自動類型轉換

---

## 2025-11-06 01:00 - 店主管理系統完善 & 實時訂單通知

### 🏪 店主管理系統獨立登錄
- ✅ 創建專屬店主登錄頁面 (`/shop/login`)
- ✅ 美化登錄界面（漸變綠色背景、商店圖標、卡片式設計）
- ✅ 智能重定向系統：
  - 未登錄訪問 `/shop` → 自動跳轉到 `/shop/login`
  - 非 store_admin 用戶訪問店主管理 → 清除 session 並跳轉登錄頁
  - 店主路由重定向到店主登錄，後台路由重定向到後台登錄
- ✅ 登錄狀態反饋（加載動畫、成功提示）
- ✅ 自動聚焦郵箱輸入框
- ✅ 實時錯誤提示（輸入時自動隱藏）
- ✅ 返回網站首頁鏈接

### 🔔 店主實時訂單通知系統（Toast 消息）
- ✅ 導航欄鈴鐺圖標（點擊跳轉訂單管理）
- ✅ 紅點徽章（顯示待處理訂單數量）
- ✅ 鈴鐺顏色變化：
  - 無訂單：灰色 (#6c757d)
  - 有訂單：紅色 (#dc3545)
- ✅ WebSocket 實時通知：
  - `new_order` 事件：新訂單通知
  - `order_updated` 事件：訂單狀態更新
- ✅ Toast 消息通知（取代桌面通知）：
  - 右上角滑入動畫
  - 訂單信息展示（訂單號、金額）
  - "立即查看"按鈕
  - 8秒後自動隱藏
  - 手動關閉按鈕
- ✅ 鈴鐺震動動畫（收到新訂單時）
- ✅ 提示音播放
- ✅ 頁面加載時自動檢查待處理訂單
- ✅ 完全自定義樣式（綠色左邊框、漸變 Header）

### 🎨 Toast 消息設計
- ✅ 位置：右上角（`position-fixed top-0 end-0`）
- ✅ 寬度：最小 320px
- ✅ 動畫：
  - 滑入動畫（slideInRight，0.3秒）
  - 鈴鐺震動動畫（ring，0.8秒）
  - 淡出效果（8秒後）
- ✅ 結構：
  - Header：🔔 新訂單通知 + 時間 + 關閉按鈕
  - Body：📄 訂單信息 + 綠色查看按鈕
- ✅ 樣式：
  - 左邊框：4px 綠色
  - 深色陰影增強視覺效果
  - Header 漸變灰色背景
  - Body 白色背景
- ✅ Z-index：9999（最高層級）

### 🔧 裝飾器優化
- ✅ `@role_required` 裝飾器智能重定向：
  - 後台路由 (`/backend`) → `/backend/login`
  - 店主路由 (`/shop`) → `/shop/login`
  - 前台路由 → `/login`
  - API 路由 → JSON 錯誤
- ✅ 權限不足處理：
  - 清除 session 並重定向到對應登錄頁

### 📡 WebSocket 通知改進
- ✅ 修改 `socketio.emit()` 參數：
  - 從 `namespace` 改為 `room`
  - 正確發送到店鋪頻道 `room=f'/shop/{shop_id}'`
  - 正確發送到後台頻道 `room='/backend'`
  - 正確發送到用戶頻道 `room=f'/user/{user_id}'`
- ✅ 訂單創建時發送通知：
  - 發送到店鋪頻道（店主接收）
  - 發送到後台管理頻道（管理員接收）
- ✅ 訂單狀態更新時發送通知：
  - 發送到店鋪頻道（店主接收）
  - 發送到用戶頻道（顧客接收）
  - 發送到後台頻道（管理員接收）

### 🔐 店主密碼管理
- ✅ 密碼重置腳本（`reset_store1_password.py`）
- ✅ 店主測試帳號：
  - 郵箱：`store1@store.com`
  - 密碼：`Qq123456@`（高強度密碼）
  - 角色：`store_admin`

### 📁 新增文件
- ✅ `public/templates/shop/login.html` - 店主登錄頁面（完全重構）

### 🔄 修改文件
- ✅ `app/utils/decorators.py` - role_required 裝飾器智能重定向（支持三種登錄系統）
- ✅ `public/templates/base/shop_base.html` - 添加鈴鐺圖標、Toast 容器、WebSocket 監聽、CSS 動畫
- ✅ `app/routes/api/orders.py` - WebSocket 通知改為 `room` 參數

### 🌐 三種登錄系統對比

| 系統 | 路由前綴 | 登錄頁面 | 主色調 | 圖標 | 角色要求 |
|------|---------|---------|--------|------|----------|
| 後台管理 | `/backend` | `/backend/login` | 🟣 紫色 | 🛡️ 盾牌 | admin |
| 店主管理 | `/shop` | `/shop/login` | 🟢 綠色 | 🏪 商店 | store_admin |
| 前台商城 | `/` | `/login` | 🔵 藍色 | 👤 用戶 | customer |

### 📊 Toast vs 桌面通知對比

| 特性 | 桌面通知（舊） | Toast 消息（新） |
|------|---------------|-----------------|
| **權限** | ❌ 需要用戶授權 | ✅ 無需權限 |
| **樣式** | ❌ 系統默認 | ✅ 完全自定義 |
| **動畫** | ❌ 無 | ✅ 滑入+震動 |
| **按鈕** | ❌ 無 | ✅ 立即查看按鈕 |
| **位置** | ❌ 系統通知欄 | ✅ 網頁右上角 |
| **兼容性** | ❌ 部分瀏覽器 | ✅ 所有現代瀏覽器 |

### 🎯 完整通知流程
```
顧客下單
  ↓
創建訂單成功
  ↓
WebSocket 發送 new_order 事件 → room: /shop/{shop_id}
  ↓
店主瀏覽器接收事件
  ↓
├─ 鈴鐺震動 0.8秒
├─ Toast 從右側滑入
├─ 顯示訂單信息
├─ 更新紅點徽章
├─ 鈴鐺變紅色
└─ 播放提示音
  ↓
8秒後 Toast 自動隱藏
```

### 🎨 用戶體驗改進
- ✅ 鈴鐺點擊跳轉到訂單管理
- ✅ Toast 內"立即查看"按鈕直達訂單列表
- ✅ 待處理訂單數量實時更新
- ✅ 鈴鐺顏色隨訂單狀態變化
- ✅ 震動動畫增強視覺反饋
- ✅ 提示音提醒（可靜默失敗）

### 🔒 安全特性
- ✅ 店主登錄與後台登錄完全分離
- ✅ 角色驗證加強（store_admin only）
- ✅ Session 管理優化（權限不足自動清除）
- ✅ WebSocket 頻道隔離（每個店鋪獨立頻道）

### 🎯 測試帳號
- **店主帳號**: store1@store.com / Qq123456@
- **後台帳號**: admin@admin.com / admin123
- **角色要求**: 
  - 店主管理需要 `store_admin` 角色
  - 後台管理需要 `admin` 角色

---

## 2025-11-05 23:30 - 後台登錄系統重構 & 密碼強度驗證

### 🔐 後台獨立登錄系統
- ✅ 創建專屬後台登錄頁面 (`/backend/login`)
- ✅ 美化登錄界面（渐變紫色背景、盾牌圖標、卡片式設計）
- ✅ 智能重定向系統：
  - 未登錄訪問 `/backend` → 自動跳轉到 `/backend/login`
  - 非 admin 用戶訪問後台 → 清除 session 並跳轉登錄頁
  - 後台路由重定向到後台登錄，前台路由重定向到前台登錄
- ✅ 登錄狀態反馈（加載動畫、成功提示）
- ✅ 自動聚焦郵箱輸入框
- ✅ 實時錯誤提示（輸入時自動隱藏）
- ✅ 返回網站首頁鏈接

### 🔑 密碼強度驗證系統
- ✅ 創建密碼強度檢查工具 (`app/utils/password_strength.py`)
- ✅ 三級強度評分系統（Low / Middle / High）
- ✅ 評分規則：
  - 長度評分（0-40分）：≥12字符 40分，≥10字符 30分，≥8字符 20分
  - 包含小寫字母：15分
  - 包含大寫字母：15分
  - 包含數字：15分
  - 包含特殊字符：15分
- ✅ 註冊要求：密碼強度必須達到 **Middle** 以上
- ✅ 前端實時密碼強度顯示：
  - 動態進度條（紅色/黃色/綠色）
  - 強度文字（弱密碼/中等密碼/強密碼）
  - 要求檢查列表（✓/✗）
    - ✓ 至少8個字符
    - ✓ 包含小寫字母
    - ✓ 包含大寫字母
    - ✓ 包含數字
- ✅ 前後端雙重驗證
- ✅ 提交時檢查強度，不符合要求立即提示

### 🏠 首頁 Banner 顯示修復
- ✅ 修復首頁 Banner 不顯示問題
- ✅ `customer.index()` 函數添加 Banner 數據查詢
- ✅ 從數據庫讀取已啟用的 Banner 並排序
- ✅ 傳遞給模板進行輪播顯示

### 📝 收貨信息自動更新功能
- ✅ 訂單創建時自動保存收貨信息到 User 表
- ✅ 前端分別發送地址字段：
  - `county` - 縣市
  - `district` - 區域
  - `zipcode` - 郵遞區號
  - `address` - 詳細地址
- ✅ 後端組合完整地址存入訂單
- ✅ 同步更新用戶資料：
  - `user.name` - 收貨人姓名
  - `user.phone` - 聯絡電話
  - `user.county` - 縣市
  - `user.district` - 區域
  - `user.zipcode` - 郵遞區號
  - `user.address` - 詳細地址
- ✅ 下次結帳自動填充上次地址

### 🎨 UI/UX 優化
- ✅ 後台登錄頁面樣式修復：
  - 移除卡片內部圓角設置
  - 使用 `overflow: hidden` 裁剪內容
  - 修復左上角和右上角白色間隙問題
- ✅ 密碼輸入框提示文字優化
- ✅ 註冊表單布局改進

### 🔧 裝飾器優化
- ✅ `@role_required` 裝飾器智能重定向：
  - 檢測請求路徑 (`request.path`)
  - 後台路由 (`/backend`) → `/backend/login`
  - 前台路由 → `/login`
  - API 路由 → JSON 錯誤
- ✅ 權限不足處理：
  - 後台：清除 session 並重定向
  - API：返回 403 JSON
  - 前台：返回 403 JSON

### 📁 新增文件
- ✅ `app/utils/password_strength.py` - 密碼強度檢查工具

### 🔄 修改文件
- ✅ `app/routes/customer.py` - index() 添加 Banner 查詢
- ✅ `app/routes/auth.py` - 註冊 API 添加密碼強度驗證
- ✅ `app/routes/api/orders.py` - 訂單創建時更新用戶收貨信息
- ✅ `app/utils/decorators.py` - role_required 裝飾器智能重定向
- ✅ `public/templates/backend/login.html` - 完全重構，獨立頁面設計
- ✅ `public/templates/store/login.html` - 添加密碼強度實時檢測
- ✅ `public/templates/store/checkout.html` - 分別發送地址字段
- ✅ `app/__init__.py` - 路由前綴調整（customer_bp 無前綴）

### 🌐 路由變更
```
【前台路由】從 /store/* 改為 /*
- / (首頁)
- /about (關於我們)
- /news (最新消息)
- /login (登入)
- /cart (購物車)
- /checkout (結帳)
- /orders (我的訂單)
- /profile (個人資料)

【後台路由】保持 /backend/*
- /backend (Dashboard - 需要 admin)
- /backend/login (登錄頁面 - 無需登錄)
```

### 🔒 安全改進
- ✅ 密碼強度要求提升（至少 Middle）
- ✅ 後台登錄與前台登錄完全分離
- ✅ 角色驗證加強（admin only）
- ✅ Session 管理優化（權限不足自動清除）
- ✅ 前後端雙重密碼驗證

### 📊 密碼強度標準
| 等級 | 分數範圍 | 要求 | 示例 |
|------|---------|------|------|
| 🔴 Low | 0-44 | 只有數字或字母 | `123456`, `abcdef` |
| 🟡 Middle | 45-69 | 大小寫+數字，≥8字符 | `Test1234`, `Abcdef12` |
| 🟢 High | 70-100 | 大小寫+數字+特殊字符，≥10字符 | `MyP@ssw0rd`, `Abcdef1234!` |

### 🎯 測試帳號
- **Backend**: admin@admin.com / admin123
- **註冊要求**: 新用戶密碼必須達到 Middle 強度

---

## 2025-11-04 21:15 - 購物車空狀態布局優化 & 後台選單順序調整

### 🎨 UI 優化
- ✅ 購物車為空時改為全寬顯示（col-12）
- ✅ 購物車有商品時顯示左右分欄（col-lg-8 + col-lg-4）
- ✅ 動態切換布局（根據購物車狀態）
- ✅ 後台側邊欄選單順序調整（首頁 Banner 移到第二位）

### 🔄 修改文件
- ✅ `public/templates/store/cart.html` - 動態布局切換邏輯
- ✅ `public/templates/base/backend_base.html` - 調整選單順序（首頁 Banner 位置）

---

## 2025-11-04 21:00 - 訂單創建邏輯重構（自動從 Product 獲取 Shop ID）

### ✨ 新增功能
- ✅ 訂單創建支持不提供 shop_id（從 product_id 自動獲取）
- ✅ 後端自動按店鋪分組商品
- ✅ 單次 API 調用創建多個店鋪的訂單
- ✅ 新增 `_create_single_order()` 輔助函數
- ✅ 詳細錯誤信息（顯示可用 product_id 列表）

### 🐛 Bug 修復
- ✅ 修復「店鋪ID不能為空」錯誤
- ✅ 修復訂單創建權限過於嚴格的問題
- ✅ 將 `@role_required('customer')` 改為 `@login_required`
- ✅ 允許所有登入用戶（admin, customer, store_admin）建立訂單

### 🔄 修改文件
- ✅ `app/routes/api/orders.py` - 重構訂單創建邏輯，新增輔助函數，添加詳細錯誤信息
- ✅ `public/templates/store/checkout.html` - 簡化前端邏輯，移除手動分組

### 📊 數據流程改進
```
【修改前】前端手動分組
items → 前端按 shop_id 分組 → 多次 POST /api/orders

【修改後】後端自動分組
items → 單次 POST /api/orders → 後端自動分組並創建多個訂單

【優勢】
✓ 前端邏輯簡化
✓ 減少網絡請求
✓ 利用資料庫關聯（Product.shop_id）
✓ 更好的錯誤處理
```

---

## 2025-11-04 20:45 - 修復訂單權限問題（已合併到上方）

---

## 2025-11-04 20:30 - 結帳頁面整合個人資料

### ✨ 新增功能
- ✅ 結帳頁面自動填充個人資料
- ✅ 整合 TWzipcode 地址選擇器到結帳頁面
- ✅ 收貨人姓名、電話自動填充
- ✅ 完整地址（縣市、區域、郵遞區號、詳細地址）自動填充
- ✅ 完整地址即時預覽
- ✅ 提交訂單時組合完整地址

### 🔄 修改文件
- ✅ `public/templates/store/checkout.html` - 整合 TWzipcode，自動填充收貨信息

### 📊 數據流程
```
User 表 → 結帳頁面
- name      → 收貨人姓名
- phone     → 聯絡電話
- county    → 縣市下拉選單
- district  → 區域下拉選單
- zipcode   → 郵遞區號
- address   → 詳細地址

提交訂單時組合完整地址：
full_address = zipcode + county + district + address
例：300 新竹市東區中正路 123 號
```

---

## 2025-11-04 20:00 - 會員個人資料頁面整合 TWzipcode

### ✨ 新增功能
- ✅ 會員個人資料頁面重新設計（左右分欄佈局）
- ✅ 整合 jQuery TWzipcode 插件（台灣地址選擇器）
- ✅ 縣市、區域、郵遞區號三級聯動
- ✅ 完整地址預覽功能
- ✅ 個人資料更新 API（姓名、電話、地址）
- ✅ 密碼修改功能（密碼強度驗證）
- ✅ 用戶地址欄位（phone, county, district, zipcode, address）

### 📁 新增文件
- ✅ `public/static/js/jquery.twzipcode.js` - TWzipcode 插件
- ✅ `add_user_address_columns.py` - 數據庫遷移腳本

### 🔄 修改文件
- ✅ `app/models.py` - User 模型新增 phone, county, district, zipcode, address 欄位
- ✅ `app/routes/api/users.py` - 新增 `/profile` 和 `/change-password` API 端點
- ✅ `app/utils/password.py` - 新增 verify_password 函數別名
- ✅ `app/__init__.py` - 移除 try-except 讓錯誤顯示
- ✅ `public/templates/base/app.html` - jQuery 在所有腳本之前載入
- ✅ `public/templates/store/profile.html` - 完整重新設計，使用 TWzipcode.set() 方法

### 🗄️ 數據庫變更
- ✅ `user.phone` - 聯絡電話（VARCHAR(20)）
- ✅ `user.county` - 縣市（VARCHAR(50)）
- ✅ `user.district` - 區域（VARCHAR(50)）
- ✅ `user.zipcode` - 郵遞區號（VARCHAR(10)）
- ✅ `user.address` - 詳細地址（VARCHAR(500)）

---

## 2025-11-04 19:00 - 結帳頁面完整實現

### ✨ 新增功能
- ✅ 結帳頁面 (`/store/checkout`)
- ✅ 收貨信息表單（姓名、電話、地址、備註）
- ✅ 訂單商品顯示（含配料）
- ✅ 支付方式選擇（貨到付款、信用卡、銀行轉帳）
- ✅ 訂單摘要（Sticky 側邊欄）
- ✅ 提交訂單流程（按店鋪分組、清空購物車）

### 📁 新增文件
- ✅ `public/templates/store/checkout.html` - 結帳頁面（Bootstrap 5 設計）

### 🔄 修改文件
- ✅ `app/routes/customer.py` - 新增 `/checkout` 路由

---

## 2025-11-04 16:00 - 前台店鋪頁面間距優化

### 🎨 店鋪頁面 UI 優化
- ✅ 分類選擇器改用 Bootstrap 5 `.form-select` 樣式
- ✅ 移除自定義 `.filter-select` 類
- ✅ 選擇器最大寬度限制為 300px
- ✅ Banner 下方間距：mb-4 → mb-3 (24px → 16px)
- ✅ 分類區塊間距：mb-3 (16px)
- ✅ 產品網格間距：g-4 → g-3 (24px → 16px)

### 🎴 產品卡片內部間距優化（縮小約 5px）
- ✅ 卡片內距：p-3 → p-2 (16px → 8px，減少 8px)
- ✅ 卡片標題間距：mb-2 → mb-1 (8px → 4px，減少 4px)
- ✅ 卡片描述間距：mb-2 → mb-1 (8px → 4px，減少 4px)
- ✅ 價格區塊間距：mb-2 → mb-1 (8px → 4px，減少 4px)
- ✅ 庫存徽章間距：mb-2 → mb-1 (8px → 4px，減少 4px)
- ✅ 總計縮小：約 24px 垂直間距，卡片更緊湊

### 🎯 重構為標準 Bootstrap 5 Card 結構
- ✅ 完全符合 Bootstrap 5 標準結構
- ✅ 圖片標籤順序：`<img class="card-img-top" src="..." style="width:100%">`
- ✅ 標題標籤：`<h5>` → `<h4 class="card-title">`
- ✅ 移除 Flexbox：`.card-body` 不再使用 `d-flex flex-column`
- ✅ 按鈕簡化：移除 `mt-auto`，保留 `w-100`
- ✅ 圖片自然適應：移除固定比例，保持原始長寬比
- ✅ 移除自定義 position-relative 容器
- ✅ 保留緊湊間距：`p-2`, `mb-1`（比標準更緊湊）
- ✅ 參考：[W3Schools Bootstrap 5 Cards](https://www.w3schools.com/bootstrap5/bootstrap_cards.php)

### 🎨 卡片樣式優化
- ✅ 移除 `.card` 的 padding 和 margin-bottom
- ✅ `.card-body` padding 調整為 0.7rem（比 p-2 的 0.5rem 更寬敞）
- ✅ `.card-img-top` 統一高度 200px，使用 `object-fit: cover`
- ✅ 使用 `!important` 強制覆蓋
- ✅ 卡片更緊湊，無多餘間距
- ✅ 所有產品圖片高度一致，網格整齊美觀

### 🛒 產品詳情模態框（新增）
- ✅ 點擊「查看詳情」彈出模態框
- ✅ 左圖右文佈局（modal-lg 大尺寸）
- ✅ 產品圖片輪播（Bootstrap 5 Carousel）
  - 支持多張圖片左右切換（◀ ▶ 按鈕）
  - 單張圖片時自動隱藏切換按鈕
  - 無圖片時顯示預設圖標（📦）
  - 圖片保持原始比例（max-height: 400px, object-fit: contain）
  - 支持鍵盤導航（← → 鍵）和觸控滑動
- ✅ 顯示完整產品資訊（名稱、描述、價格、庫存）
- ✅ 配料勾選功能
  - 從店鋪獲取配料列表（GET /api/toppings?shop_id=X&is_active=true）
  - 從店鋪獲取配料上限（shop.max_toppings）
  - 勾選框（checkbox）選擇配料
  - 顯示配料名稱和價格（+$X，價格為 0 時顯示 "FREE"）
  - 顯示店鋪最大配料數量限制（例如：最多 5 個）
  - 達到上限時自動禁用未選項
  - 已選配料數量實時顯示
  - 可滾動配料列表（max-height: 150px）
  - 所有產品共用店鋪的統一配料列表
- ✅ 實時價格計算
  - 公式：總價 = (產品價格 + 配料總價) × 數量
  - 配料勾選時立即更新
  - 數量修改時立即更新
  - 大字體顯示總價（bg-light 背景）
- ✅ 數量選擇器（含庫存驗證）
- ✅ 兩個操作按鈕：
  - 🛒 加入購物車（POST /api/cart/add + toppings，停留當前頁）
  - 💳 直接結帳（加入購物車 + toppings 後跳轉 /store/checkout）
- ✅ 完整錯誤處理和提示
- ✅ 缺貨時停用數量輸入
- ✅ 完全使用 Bootstrap 5 原生模態框樣式（無自定義 CSS）

### 🧹 CSS 清理優化
- ✅ 從 4 個 CSS 文件移除所有模態框自定義樣式（共 107 行）
- ✅ 完全使用 Bootstrap 5 原生模態框樣式
- ✅ 移除 z-index、pointer-events、body.modal-open 等自定義規則
- ✅ 減少代碼量，提升可維護性

### 🛒 購物車 API 系統（新增）
- ✅ 創建完整購物車 API（`app/routes/api/cart.py`）
- ✅ POST /api/cart/add - 加入購物車
- ✅ GET /api/cart - 獲取購物車內容
- ✅ PUT /api/cart/update - 更新數量
- ✅ DELETE /api/cart/remove - 移除項目
- ✅ DELETE /api/cart/clear - 清空購物車
- ✅ 使用 Flask Session 存儲（支持訪客購物車）
- ✅ 智能合併相同產品和配料組合
- ✅ 自動計算價格（產品 + 配料）× 數量
- ✅ 庫存驗證
- ✅ 導航欄購物車數量徽章（紅色圓點 + 數字）
- ✅ 實時更新購物車數量（加入/移除時自動更新）

### 🐛 Bug 修復
- ✅ 修復後台配料添加失敗問題（數據格式錯誤）
- ✅ 免費配料（價格 0）顯示為 "FREE" 而非 "+$0"
- ✅ API 訊息中文化：所有 "topping/Topping" 改為 "配料"（共 11 處）
- ✅ 修正配料上限字段：`max_toppings` → `max_toppings_per_order`
- ✅ 修復購物車 404 錯誤（創建購物車 API）

### 📁 新增文件
- ✅ `app/routes/api/cart.py` - 購物車 API（完整 CRUD）

### 🔄 修改文件
- ✅ `app/__init__.py` - 註冊 cart_api_bp
- ✅ `public/templates/base/store_base.html` - 購物車徽章改用 API 獲取數量
- ✅ `public/templates/store/cart.html` - Bootstrap 5 設計，改用 API，移除 localStorage，左右分欄佈局，數量控制按鈕，訂單摘要側邊欄
- ✅ `public/templates/store/shop.html` - 間距優化、Bootstrap 5 Card 結構、產品詳情模態框、圖片輪播、配料勾選、FREE 顯示
- ✅ `public/templates/backend/shops/edit.html` - 修復配料添加數據格式
- ✅ `app/routes/api/products.py` - GET /<product_id> 端點新增 images 陣列
- ✅ `app/routes/api/toppings.py` - 新增 GET / 端點（支持 shop_id 和 is_active 篩選）、訊息中文化
- ✅ `app/routes/api/shops.py` - 訊息中文化
- ✅ `public/static/css/store.css` - 卡片樣式，移除模態框 CSS
- ✅ `public/static/css/backend.css` - 移除模態框自定義樣式
- ✅ `public/static/css/shop_admin.css` - 移除模態框自定義樣式
- ✅ `public/static/css/style.css` - 移除模態框自定義樣式

---

## 2025-11-04 15:30 - 首頁 Banner 管理系統與 UI 優化

### 🎪 首頁 Banner 管理系統（新增）
- ✅ HomeBanner 數據模型（name, image_path, is_active, display_order）
- ✅ 完整 CRUD API（/api/home-banners）
  - GET - 獲取列表（支持篩選啟用狀態）
  - POST - 新增 Banner（含圖片上傳）
  - PUT - 更新 Banner（名稱、狀態）
  - DELETE - 刪除 Banner（同步刪除文件）
  - PUT /reorder - 拖拽排序
- ✅ 後台管理頁面（/backend/home-banners）
  - 卡片式 2 列網格布局
  - 拖拽排序（SortableJS）
  - 啟用/停用切換
  - 新增/編輯/刪除功能
- ✅ 前台首頁輪播顯示
  - Bootstrap 5 Carousel 組件
  - 3:1 橫幅比例（1200x400）
  - 自動輪播、指示器、控制按鈕
  - 只顯示啟用的 Banner
  - 無 Banner 時顯示預設歡迎訊息
- ✅ 後台菜單新增「首頁 Banner」項目

### 🎨 UI/UX 優化（統一 Bootstrap 5 間距）
- ✅ 調整所有表單標籤與輸入框間距（mb-2, mt-2 約 8px）
- ✅ 調整卡片內部元素間距（mt-2, py-2）
- ✅ 統一使用 Bootstrap 5 間距工具類（mt-1/2/3, mb-1/2/3）
- ✅ 優化模態框表單布局（標籤與輸入框間距約 5px）
- ✅ Banner 圖片預覽增加外邊距（mx-2, mt-2）和圓角（border-radius: 4px）
- ✅ 卡片標題與內容間距優化（py-2, mt-2）

### 📁 新增文件
- ✅ `app/routes/api/home_banners.py` - 首頁 Banner API
- ✅ `public/templates/backend/home_banners.html` - 管理頁面

### 🔄 修改文件
- ✅ `app/models.py` - 新增 HomeBanner 模型
- ✅ `app/__init__.py` - 註冊 home_banners API，首頁載入 Banner 數據
- ✅ `app/routes/backend.py` - 新增 home_banners 路由
- ✅ `public/templates/base/backend_base.html` - 新增菜單項
- ✅ `public/templates/store/index.html` - 整合輪播組件
- ✅ `CHANGELOG.md` - 新增時間戳記格式（HH:MM）

---

## 2025-11-04 14:00 - 產品管理與分類系統完善

### 🖼️ 商店與產品多圖片管理系統
- ✅ 新增 ShopImage 數據模型（圖片路徑、排序、索引）
- ✅ Shop 模型新增 images 關係和 get_primary_image() 方法
- ✅ 圖片上傳 API（POST /api/shops/:id/images）
- ✅ 圖片刪除 API（DELETE /api/shop-images/:id）
- ✅ 圖片排序 API（PUT /api/shops/:id/images/reorder）
- ✅ 後台圖片管理界面（拖拽排序、主圖標記）
- ✅ 使用 SortableJS 實現拖拽排序
- ✅ 前台顯示第一張圖片或默認 icon
- ✅ 圖片比例：1:1 正方形（padding-top: 100%）
- ✅ 文件上傳配置（16MB、支持 PNG/JPG/GIF/WEBP）
- ✅ 創建上傳目錄：public/uploads/shops/
- ✅ 新增 ProductImage 數據模型（同樣支持排序和索引）
- ✅ Product 模型新增 images 關係和 get_primary_image() 方法
- ✅ 產品圖片上傳 API（POST /api/products/:id/images）
- ✅ 產品圖片刪除 API（DELETE /api/product-images/:id）
- ✅ 產品圖片排序 API（PUT /api/products/:id/images/reorder）
- ✅ products/edit.html 新增圖片管理區域
- ✅ 前台產品卡片和詳情頁顯示主圖
- ✅ 創建上傳目錄：public/uploads/products/

### 🎪 Banner 橫幅系統
**店鋪 Banner（單張）**
- ✅ Shop 模型新增 banner_image 字段（單張橫幅）
- ✅ Banner 上傳 API（POST /api/shops/:id/banner）
- ✅ Banner 刪除 API（DELETE /api/shops/:id/banner）
- ✅ 自動替換舊 Banner（上傳新的時刪除舊的）
- ✅ shops/edit.html 新增 Banner 管理區域
- ✅ Banner 比例：4:1 橫幅（padding-top: 25%）
- ✅ 建議尺寸：1200x300 像素
- ✅ 前台店鋪頁面頂部全寬顯示
- ✅ 漸層遮罩和文字疊加效果
- ✅ 無 Banner 時顯示傳統標題

**首頁 Banner（多張輪播）**
- ✅ HomeBanner 數據模型（name, image_path, is_active, display_order）
- ✅ 完整 CRUD API（/api/home-banners）
- ✅ 後台管理頁面（/backend/home-banners）
- ✅ 卡片式列表、拖拽排序
- ✅ 啟用/停用切換（只顯示啟用的）
- ✅ 前台 Bootstrap 輪播組件
- ✅ 3:1 橫幅比例（padding-top: 33.33%）
- ✅ 建議尺寸：1200x400 像素
- ✅ 自動輪播、指示器、控制按鈕
- ✅ 漸層遮罩效果
- ✅ 創建上傳目錄：public/uploads/banners/

### 📦 產品管理系統完善
- ✅ 修復產品列表頁面（完整的 HTML 結構）
- ✅ 創建產品新增頁面（/backend/products/add）
- ✅ 創建產品編輯頁面（/backend/products/:id/edit）
- ✅ 產品表單包含：名稱、店鋪、分類、描述、單價、折扣價、庫存、狀態
- ✅ 價格驗證：折扣價必須小於單價
- ✅ 修復數據字段：stock → stock_quantity
- ✅ 產品列表包含：搜索、5個篩選器、分頁
- ✅ 新增產品 API（POST /api/products）含完整驗證
- ✅ 產品 CRUD 操作全部記錄到 update_log
- ✅ 前台產品列表優化為響應式網格
  - 桌面：4 列（col-lg-3）
  - 平板：3 列（col-md-4）
  - 手機：2 列（col-sm-6）
  - 間隔：g-4 (24px)
  - 使用 Bootstrap Card 組件

### 🏷️ 分類管理完整系統
- ✅ 創建分類 API（/api/categories）
  - GET - 獲取所有分類（含產品數量統計）
  - POST - 新增分類（名稱唯一性驗證）
  - PUT - 更新分類
  - DELETE - 刪除分類（檢查關聯產品）
- ✅ 後台分類管理頁面（/backend/categories）
- ✅ 分類 CRUD 操作（搜索、新增、編輯、刪除）
- ✅ 產品頁面分類管理鏈接
  - 齒輪按鈕 → 新分頁開啟分類管理
  - 無模態框干擾
- ✅ 數據保護：有產品的分類無法刪除
- ✅ 禁用刪除按鈕並顯示提示
- ✅ 左側菜單新增「分類管理」

### 🔧 JavaScript 和 URL 修復
- ✅ 修復 shops/list.html 語法錯誤（移除廢棄代碼）
- ✅ 修復 products/list.html 語法錯誤（移除不完整結構）
- ✅ 修復所有列表頁面 URL 生成問題
  - shops/list.html：詳情和編輯鏈接
  - users/list.html：編輯鏈接
  - products/list.html：詳情和編輯鏈接
  - orders/list.html：詳情和編輯鏈接
- ✅ 從 Jinja2 模板語法改為 JavaScript 模板字符串

### 💰 價格系統標準化
- ✅ 所有價格改為整數（無小數點）
- ✅ 移除所有 step="0.01" 屬性
- ✅ parseFloat → parseInt
- ✅ toFixed(2) → Math.round() 或 |int 過濾器
- ✅ 影響文件：
  - 配料價格輸入（shops/add.html, shops/edit.html）
  - 產品價格顯示（shop_detail.html, product_detail.html）
  - 訂單價格顯示（orders/list.html, order_detail.html）

### 📐 配料表單優化
- ✅ 配料名稱框：col-5 (42%) → col-3 (25%)
- ✅ 價格框：col-3/4 → col-2 (17%)
- ✅ 新增狀態開關：col-2 (17%)
- ✅ 按鈕區域擴大：col-2/3 → col-5 (41%)
- ✅ 統一 shops/add.html 和 shops/edit.html 布局
- ✅ 新增配料表單支持狀態字段

### 🌏 繁體中文完善
- ✅ Backend 所有用戶可見文本檢查
- ✅ Topping/Toppings → 配料（13 個文件）
- ✅ 影響範圍：
  - 後台管理界面（6 個文件）
  - 店主管理界面（4 個文件）
  - 前台顧客界面（3 個文件）
- ✅ 保留技術名稱（變量、函數、API 路徑）

### 🐛 Bug 修復
- ✅ 修復產品編輯頁面 JavaScript 代碼重複
- ✅ 修復訂單列表移除廢棄的 confirmUpdateStatus() 函數
- ✅ 修復所有列表頁面的 404 問題
- ✅ 清理所有模態框重構遺留的廢代碼
- ✅ 移除產品頁面的分類管理模態框（改為新分頁開啟）
- ✅ 代碼精簡：移除 ~320 行模態框相關代碼
- ✅ 修復產品 API：新增缺少的 POST /api/products 端點
- ✅ 修復使用者角色選單：
  - 新增「請選擇角色」空白選項
  - 相容舊角色名（shop_owner）
  - 顯示當前角色提示
- ✅ 修復側邊欄菜單激活邏輯：
  - 從精確匹配改為前綴匹配（startswith）
  - 子頁面（add/edit）也會高亮對應菜單項

### 📊 數據統計
- ✅ 分類顯示產品數量統計
- ✅ 產品列表顯示庫存徽章
- ✅ 店鋪列表顯示配料數量

### 📁 新增文件
- ✅ `app/routes/api/categories.py` - 分類 API
- ✅ `app/routes/api/shop_images.py` - 商店圖片 API
- ✅ `app/routes/api/product_images.py` - 產品圖片 API
- ✅ `app/routes/api/shop_banner.py` - 店鋪 Banner API
- ✅ `app/routes/api/home_banners.py` - 首頁 Banner API
- ✅ `public/templates/backend/categories.html` - 分類管理頁面
- ✅ `public/templates/backend/home_banners.html` - 首頁 Banner 管理頁面
- ✅ `public/templates/backend/products/add.html` - 產品新增頁面
- ✅ `public/templates/backend/products/edit.html` - 產品編輯頁面（含圖片管理）
- ✅ `public/uploads/shops/.gitkeep` - 商店上傳目錄
- ✅ `public/uploads/products/.gitkeep` - 產品上傳目錄
- ✅ `public/uploads/banners/.gitkeep` - Banner 上傳目錄
- ✅ `public/uploads/.gitignore` - Git 忽略規則（shops + products + banners）

### 🔄 修改文件
- ✅ `app/models.py` - 新增 ShopImage, ProductImage, HomeBanner 模型
- ✅ `app/__init__.py` - 註冊所有圖片 API、首頁 Banner
- ✅ `app/config.py` - 文件上傳配置
- ✅ `app/routes/backend.py` - 新增 categories, home_banners 路由
- ✅ `app/routes/api/products.py` - 新增 POST 端點、update_log 整合
- ✅ `public/templates/base/backend_base.html` - 新增分類管理、首頁 Banner 菜單、修復菜單激活邏輯
- ✅ `public/templates/backend/shops/add.html` - 配料表單優化、繁體中文
- ✅ `public/templates/backend/shops/edit.html` - Banner、圖片、配料管理
- ✅ `public/templates/backend/shops/list.html` - 修復 URL、語法錯誤
- ✅ `public/templates/backend/users/add.html` - 角色選單空白選項
- ✅ `public/templates/backend/users/edit.html` - 角色選單優化、相容舊角色
- ✅ `public/templates/backend/users/list.html` - 修復 URL、角色徽章相容
- ✅ `public/templates/backend/products/list.html` - 修復結構、URL
- ✅ `public/templates/backend/orders/list.html` - 修復 URL、價格顯示
- ✅ `public/templates/store/index.html` - Banner 輪播、商店圖片顯示
- ✅ `public/templates/store/shop.html` - 店鋪 Banner、產品網格布局（4列）
- ✅ `public/templates/store/product.html` - 產品主圖顯示、價格整數化
- ✅ 其他 10+ 個模板文件（價格、繁體中文調整）

### 📈 項目規模
```
當前統計：
├── HTML 模板：43 個
├── CSS 文件：4 個
├── JavaScript 文件：4 個
├── API 路由：12 個
│   ├── users, shops, products, orders, toppings, categories
│   └── shop_images, product_images, shop_banner, home_banners, auth, websocket
├── 數據模型：11 個
│   ├── User, Shop, Product, Category, Topping
│   ├── Order, OrderItem
│   ├── ShopImage, ProductImage, HomeBanner
│   └── UpdateLog
└── 後台管理頁面：10 個
    ├── 儀表板、使用者、店鋪、產品、分類、訂單
    ├── 首頁 Banner、系統 Log
    └── 各種詳情頁（shop_detail, product_detail, order_detail）
```

### 🎯 圖片管理功能對比
```
首頁 Banner（輪播）：
├── 上傳目錄：public/uploads/banners/
├── 文件命名：home_banner_{timestamp}.{ext}
├── 數量：多張（可排序、啟用/停用）
├── 比例：3:1 橫幅（1200x400）
├── 前台顯示：首頁頂部輪播
└── 管理位置：/backend/home-banners

店鋪 Banner（單張）：
├── 上傳目錄：public/uploads/banners/
├── 文件命名：banner_shop_{id}_{timestamp}.{ext}
├── 數量：1 張（自動替換）
├── 比例：4:1 橫幅（1200x300）
├── 前台顯示：店鋪頁面頂部
└── 管理位置：/backend/shops/:id/edit

商店圖片管理：
├── 上傳目錄：public/uploads/shops/
├── 文件命名：shop_{id}_{timestamp}.{ext}
├── 數量：多張（可排序）
├── 比例：1:1 正方形
├── 前台顯示：首頁店鋪列表
└── 管理位置：/backend/shops/:id/edit

產品圖片管理：
├── 上傳目錄：public/uploads/products/
├── 文件命名：product_{id}_{timestamp}.{ext}
├── 數量：多張（可排序）
├── 比例：1:1 正方形
├── 前台顯示：產品列表、產品詳情頁
└── 管理位置：/backend/products/:id/edit

共同特點：
├── 拖拽排序（SortableJS）
├── 無圖片顯示 icon 或預設樣式
├── 關聯刪除（刪除記錄時刪除文件）
└── 更新日誌記錄
```

---

## 2025-11-04 10:00 - CSS 架構優化與模態框重構

### ��� CSS 架構優化
- ✅ 創建 4 個獨立 CSS 文件（22.4KB）
- ✅ 從 14 個頁面移除內聯樣式
- ✅ 改善代碼維護性和緩存效率

### ��� Backend 完整 CRUD 系統
- ✅ Users 管理：搜索、過濾、新增/編輯/刪除、分頁
- ✅ Shops 管理：搜索、過濾、新增/編輯/刪除、分頁
- ✅ Products 管理：搜索、過濾、新增/編輯/刪除、分頁
- ✅ Orders 管理：搜索、過濾、狀態更新、統計、分頁
- ✅ 每頁筆數可選：10/20/50/100 筆
- ✅ Bootstrap 5 模態框表單

### ��� 系統更新 Log
- ✅ 新增 UpdateLog 數據模型
- ✅ 自動記錄所有 CRUD 操作
- ✅ 保存修改前後數據對比（JSON格式）
- ✅ 記錄操作者和 IP 地址
- ✅ Backend 查看頁面（搜索、過濾、分頁）
- ✅ 詳情模態框（數據對比視圖）
- ✅ 已集成 Users 和 Shops API

### ��� JavaScript 優化
- ✅ 創建 backend_common.js 通用組件庫
- ✅ jQuery 載入順序修復（確保最先載入）
- ✅ 所有頁面添加 {{ super() }} 保留父模板腳本
- ✅ 側邊欄導航點擊問題修復
- ✅ 模態框 z-index 衝突修復
- ✅ Socket.IO 錯誤優雅處理

### ⚙️ 環境配置
- ✅ 使用 python-dotenv 載入 .env
- ✅ 環境變數從 MYSQL_ 改為 DB_
- ✅ 創建 env.example 範例文件
- ✅ 完整的中文註釋和說明

### ��� 錯誤處理
- ✅ 創建友好的錯誤頁面（400/401/403/404/500）
- ✅ 區分 API 和網頁請求
- ✅ Socket.IO 會話斷開錯誤靜默處理
- ✅ KeyError 處理器

### ��� UI/UX 改進
- ✅ 登入/註冊合併為一個按鈕
- ✅ 登入頁面使用 Bootstrap 選項卡
- ✅ Font Awesome 7 圖標集成
- ✅ 用戶下拉菜單（個人資料、登出）
- ✅ 響應式設計優化

### ��� 重命名和重構
- ✅ shop_owner → store_admin
- ✅ admin → backend（路由）
- ✅ 簡體中文 → 繁體中文
- ✅ 管理員密碼重置腳本

### ��� 項目結構
```
public/
├── static/
│   ├── css/
│   │   ├── style.css (6.5KB)
│   │   ├── backend.css (2.9KB)
│   │   ├── store.css (5.9KB)
│   │   └── shop_admin.css (7.1KB)
│   └── js/
│       ├── backend_common.js (5.4KB)
│       └── socketio_client.js (3.9KB)
└── templates/
    ├── base/ (4個基礎模板)
    ├── backend/ (9個頁面 + update_logs)
    ├── shop/ (8個頁面)
    ├── store/ (6個頁面)
    └── errors/ (5個錯誤頁面)
```

### ��� 測試帳號
- **Backend**: admin@admin.com / admin123
- **環境配置**: 複製 env.example 為 .env

---
更新者：AI Assistant  
日期：2025-11-04

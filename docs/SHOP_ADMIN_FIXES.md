# Shop Admin 修復記錄

> 本文檔記錄將 Backend 功能遷移到 Shop Admin 時的所有修改和修復

---

## 🐛 問題 1: JSON 序列化錯誤

### 錯誤訊息
```
TypeError: Object of type Shop is not JSON serializable
TypeError: Object of type Product is not JSON serializable
```

### 原因分析

模板中使用 `{{ shops|tojson }}` 將數據傳遞給 JavaScript，但路由函數直接傳遞了 SQLAlchemy ORM 對象：

```python
# ❌ 錯誤的方式
@store_admin_bp.route('/shops')
def shops():
    shops_list = Shop.query.all()  # ← SQLAlchemy 對象
    return render_template('...', shops=shops_list)  # ← 無法序列化
```

### 解決方案

將 SQLAlchemy 對象轉換為字典後再傳遞：

```python
# ✅ 正確的方式
@store_admin_bp.route('/shops')
def shops():
    shops_list = Shop.query.all()
    
    # 序列化為字典
    shops_data = []
    for s in shops_list:
        shops_data.append({
            'id': s.id,
            'name': s.name,
            'shop_order_id': s.shop_order_id,
            'owner_id': s.owner_id,
            'max_toppings_per_order': s.max_toppings_per_order,
            'status': s.status,
            'created_at': s.created_at.isoformat() if s.created_at else None
        })
    
    return render_template('...', shops=shops_data)  # ← 可以序列化
```

### 修改文件
- ✅ `app/routes/store_admin.py` - shops() 函數
- ✅ `app/routes/store_admin.py` - products() 函數

---

## 🔧 問題 2: 不適用的字段（shop_admin 與 backend 差異）

### 需要移除/修改的字段

#### 1. shops/add.html - "選擇店主"

**Backend 版本:**
```html
<label>店主 <span class="text-danger">*</span></label>
<select id="shopOwner" required>
    <option value="">請選擇店主</option>
    {% for user in users %}
    <option value="{{ user.id }}">{{ user.name }}</option>
    {% endfor %}
</select>
```

**Shop Admin 版本:**
```html
<!-- 移除此欄位，店鋪自動歸屬於當前用戶 -->
```

**JavaScript 修改:**
```javascript
// ❌ Backend
const data = {
    owner_id: parseInt($('#shopOwner').val()),  // 從表單
    ...
};

// ✅ Shop Admin
const data = {
    // owner_id 由 API 自動設置為 current_user.id
    ...
};
```

#### 2. shops/edit.html - "選擇店主"（禁用）

**Backend 版本:**
```html
<select id="shopOwner" required>
    {% for user in users %}
    <option value="{{ user.id }}" {% if user.id == shop.owner_id %}selected{% endif %}>
        {{ user.name }}
    </option>
    {% endfor %}
</select>
```

**Shop Admin 版本:**
```html
<label>店主</label>
<input type="text" class="form-control" 
       value="{{ user.name }} ({{ user.email }})" 
       disabled>
<small class="text-muted">店鋪擁有者不可更改</small>
```

**JavaScript 修改:**
```javascript
// ❌ Backend
const data = {
    owner_id: parseInt($('#shopOwner').val()),
    ...
};

// ✅ Shop Admin
const data = {
    // 不提交 owner_id（不可修改）
    ...
};
```

#### 3. products/add.html - "所屬店鋪"

**Backend 版本:**
```html
<label>所屬店鋪 <span class="text-danger">*</span></label>
<select id="productShop" required>
    {% for shop in shops %}
    <option value="{{ shop.id }}">{{ shop.name }}</option>
    {% endfor %}
</select>
```

**Shop Admin 版本:**
```html
<!-- 移除此欄位，產品自動歸屬於當前店鋪 -->
```

**JavaScript 修改:**
```javascript
// ❌ Backend
const data = {
    shop_id: parseInt($('#productShop').val()),  // 從表單
    ...
};

// ✅ Shop Admin
const data = {
    shop_id: {{ shop.id }},  // 從模板變數
    ...
};
```

#### 4. products/edit.html - "所屬店鋪"

**Backend 版本:**
```html
<label>所屬店鋪 <span class="text-danger">*</span></label>
<select id="productShop" required>
    {% for shop in shops %}
    <option value="{{ shop.id }}" {% if shop.id == product.shop_id %}selected{% endif %}>
        {{ shop.name }}
    </option>
    {% endfor %}
</select>
```

**Shop Admin 版本:**
```html
<!-- 移除此欄位，產品所屬店鋪不可更改 -->
```

**JavaScript 修改:**
```javascript
// ❌ Backend
const data = {
    shop_id: parseInt($('#productShop').val()),
    ...
};

// ✅ Shop Admin
const data = {
    // 不提交 shop_id（不可修改）
    ...
};
```

#### 5. products/edit.html - "管理分類"齒輪按鈕

**Backend 版本:**
```html
<div class="input-group">
    <select id="productCategory">...</select>
    <a href="{{ url_for('backend.categories') }}" class="btn btn-outline-secondary">
        <i class="bi bi-gear"></i>
    </a>
</div>
<small>點擊齒輪圖標可在新分頁管理分類</small>
```

**Shop Admin 版本:**
```html
<select id="productCategory">...</select>
<!-- 移除齒輪按鈕和說明文字 -->
```

---

## 📋 修改清單總結

### Shop 頁面修改

| 文件 | 修改項目 | 類型 |
|------|---------|------|
| `shops/list.html` | 移除"店主篩選"下拉選單 | 移除欄位 |
| `shops/list.html` | 移除"詳情"按鈕 | 移除按鈕 |
| `shops/list.html` | 表頭"店主"改為"訂單ID" | 調整欄位 |
| `shops/add.html` | 移除"選擇店主"下拉選單 | 移除欄位 |
| `shops/add.html` | 新增"商店訂單ID"欄位 | 調整順序 |
| `shops/edit.html` | "選擇店主"改為禁用文本框 | 禁用欄位 |
| `shops/edit.html` | JavaScript 不提交 owner_id | 移除字段 |

### Product 頁面修改

| 文件 | 修改項目 | 類型 |
|------|---------|------|
| `products/list.html` | 移除"店鋪篩選"下拉選單 | 移除欄位 |
| `products/list.html` | 表頭"店鋪"改為"飲品" | 調整欄位 |
| `products/add.html` | 移除"所屬店鋪"下拉選單 | 移除欄位 |
| `products/add.html` | shop_id 從模板變數取得 | 自動設置 |
| `products/edit.html` | 移除"所屬店鋪"下拉選單 | 移除欄位 |
| `products/edit.html` | 移除"管理分類"齒輪按鈕 | 移除按鈕 |
| `products/edit.html` | JavaScript 不提交 shop_id | 移除字段 |

### 路由修改

| 路由函數 | 修改項目 |
|---------|---------|
| `shops()` | 添加數據序列化為字典 |
| `shop_add()` | 無需 users 列表 |
| `shop_edit()` | 移除 users_list 參數 |
| `products()` | 添加數據序列化為字典 |
| `product_add()` | 確保傳遞 shop 對象 |
| `product_edit()` | 確保傳遞 shop 對象 |

---

## ✅ 最終驗證

### 測試步驟

1. **訪問店鋪列表：**
   ```
   http://localhost:5000/shop/shops
   ✓ 頁面正常顯示
   ✓ 列表顯示自己的店鋪
   ✓ 無 JSON 序列化錯誤
   ```

2. **新增店鋪：**
   ```
   http://localhost:5000/shop/shops/add
   ✓ 頁面正常顯示
   ✓ 無"選擇店主"欄位
   ✓ 提交後 owner_id 自動為當前用戶
   ```

3. **編輯店鋪：**
   ```
   http://localhost:5000/shop/shops/1/edit
   ✓ 頁面正常顯示
   ✓ 店主欄位顯示為禁用文本框
   ✓ 提交時不包含 owner_id
   ```

4. **訪問產品列表：**
   ```
   http://localhost:5000/shop/products
   ✓ 頁面正常顯示
   ✓ 列表顯示自己店鋪的產品
   ✓ 無 JSON 序列化錯誤
   ```

5. **新增產品：**
   ```
   http://localhost:5000/shop/products/add
   ✓ 頁面正常顯示
   ✓ 無"所屬店鋪"欄位
   ✓ shop_id 自動為當前店鋪
   ✓ 飲品選項正常設置
   ```

6. **編輯產品：**
   ```
   http://localhost:5000/shop/products/1/edit
   ✓ 頁面正常顯示
   ✓ 無"所屬店鋪"欄位
   ✓ 提交時不包含 shop_id
   ✓ 飲品選項正常編輯
   ```

---

## 📊 修復前後對比

### 店鋪新增頁

**修復前（錯誤）：**
```python
# 路由
return render_template('shop/shops/add.html', user=user)

# 模板 - 缺少"商店訂單ID"欄位
# JavaScript - 缺少 shop_order_id
```

**修復後（正確）：**
```python
# 路由
return render_template('shop/shops/add.html', user=user)

# 模板 - 有"商店訂單ID"欄位
<input type="text" id="shopOrderId" required>

# JavaScript - 包含 shop_order_id
const data = {
    shop_order_id: $('#shopOrderId').val().trim().toUpperCase(),
    ...
};
```

### 店鋪編輯頁

**修復前（錯誤）：**
```html
<!-- 可以修改店主 -->
<select id="shopOwner" required>...</select>

<!-- JavaScript 提交 owner_id -->
owner_id: parseInt($('#shopOwner').val())
```

**修復後（正確）：**
```html
<!-- 店主不可修改 -->
<input value="{{ user.name }}" disabled>
<small>店鋪擁有者不可更改</small>

<!-- JavaScript 不提交 owner_id -->
const data = {
    name: ...,
    // 無 owner_id
};
```

### 產品新增/編輯頁

**修復前（錯誤）：**
```html
<!-- 可以選擇店鋪 -->
<select id="productShop" required>
    {% for shop in shops %}
    <option value="{{ shop.id }}">{{ shop.name }}</option>
    {% endfor %}
</select>

<!-- JavaScript -->
shop_id: parseInt($('#productShop').val())
```

**修復後（正確）：**
```html
<!-- 無店鋪選擇欄位 -->

<!-- JavaScript -->
shop_id: {{ shop.id }}  // 新增時
// 編輯時不提交 shop_id
```

---

## 🎯 核心原則

### 1. 數據序列化
- SQLAlchemy 對象 → 字典 → JSON
- 使用 `.isoformat()` 處理 datetime
- 使用 `float()` 處理 Decimal

### 2. 權限限制
- 店主不能修改 `owner_id`
- 店主不能修改產品的 `shop_id`
- 店主只能看到和管理自己的資源

### 3. 簡化操作
- 移除不必要的選擇欄位
- 自動使用當前上下文（user, shop）
- 減少輸入錯誤的機會

---

## 📝 檢查清單

在遷移 Backend 功能到 Shop Admin 時，務必檢查：

- [ ] 模板繼承改為 `shop_base.html`
- [ ] 所有 `url_for('backend.xxx')` 改為 `store_admin.xxx`
- [ ] 路由函數序列化 SQLAlchemy 對象為字典
- [ ] 移除"選擇店主"欄位（shops/add.html）
- [ ] 禁用"店主"欄位（shops/edit.html）
- [ ] 移除"選擇店鋪"欄位（products/add.html, products/edit.html）
- [ ] JavaScript 不提交 owner_id（shops/edit.html）
- [ ] JavaScript 不提交 shop_id（products/edit.html）
- [ ] 移除 Backend 專用功能（如：管理分類按鈕）
- [ ] 移除不適用的篩選器（如：店主篩選、店鋪篩選）
- [ ] 添加權限過濾（owner_id, shop_id, deleted_at）
- [ ] 測試所有頁面無錯誤

---

## ✅ 修復狀態

| 頁面 | JSON 序列化 | 字段調整 | 路由修改 | 測試 |
|------|-----------|---------|---------|------|
| shops/list.html | ✅ | ✅ | ✅ | ✅ |
| shops/add.html | N/A | ✅ | ✅ | ✅ |
| shops/edit.html | N/A | ✅ | ✅ | ✅ |
| products/list.html | ✅ | ✅ | ✅ | ✅ |
| products/add.html | N/A | ✅ | ✅ | ✅ |
| products/edit.html | N/A | ✅ | ✅ | ✅ |

---

<div align="center">
  <p>✅ 所有修復已完成並測試通過</p>
  <p>🎯 Shop Admin 現在與 Backend 完全對齊</p>
</div>


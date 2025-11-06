# 圖標參考手冊

## 🎨 Font Awesome 版本

**當前版本：6.7.1**

CDN：
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.1/css/all.min.css">
```

---

## 🥤 飲品圖標

### 冷飲（Cold Drink）

**圖標代碼：**
```html
<i class="fa-solid fa-snowflake text-info"></i> 冷飲
```

**變體：**
- 純圖標：`<i class="fa-solid fa-snowflake"></i>`
- 帶顏色：`<i class="fa-solid fa-snowflake text-info"></i>`
- Badge 版：`<span class="badge bg-info"><i class="fa-solid fa-snowflake"></i></span>`

**使用場景：**
- ✅ 產品列表（/backend, /shop）
- ✅ 商品選擇（商店前台）
- ✅ 購物車
- ✅ 訂單詳情
- ✅ 訂單管理

**顏色方案：**
- 文字顏色：`text-info`（淺藍色）
- Badge 背景：`bg-info`（淺藍色背景）

---

### 熱飲（Hot Drink）

**圖標代碼：**
```html
<i class="fa-solid fa-mug-hot text-warning"></i> 熱飲
```

**變體：**
- 純圖標：`<i class="fa-solid fa-mug-hot"></i>`
- 帶顏色：`<i class="fa-solid fa-mug-hot text-warning"></i>`
- Badge 版：`<span class="badge bg-warning"><i class="fa-solid fa-mug-hot"></i></span>`

**使用場景：**
- ✅ 產品列表（/backend, /shop）
- ✅ 商品選擇（商店前台）
- ✅ 購物車
- ✅ 訂單詳情
- ✅ 訂單管理

**顏色方案：**
- 文字顏色：`text-warning`（橙黃色）
- Badge 背景：`bg-warning`（橙黃色背景）

---

## 📍 使用位置總覽

| 頁面 | 路徑 | 圖標使用 |
|------|------|---------|
| **Backend - 產品列表** | `/backend/products` | Badge 版 |
| **Backend - 訂單詳情** | `/backend/orders/<id>` | 文字版（帶顏色）|
| **Shop Admin - 產品列表** | `/shop/products` | Badge 版 |
| **商店前台 - 商品頁** | `/store/shop/<id>` | 文字版（帶顏色）|
| **商店前台 - 購物車** | `/store/cart` | 文字版（帶顏色）|
| **商店前台 - 訂單詳情** | `/store/orders/<id>` | Badge 版 |

---

## 🎯 實際代碼示例

### 1. 產品列表（Badge 版）

```javascript
// JavaScript 動態渲染
let drinkBadges = '';
if (product.has_cold_drink) {
    drinkBadges += '<span class="badge bg-info"><i class="fa-solid fa-snowflake"></i></span> ';
}
if (product.has_hot_drink) {
    drinkBadges += '<span class="badge bg-warning"><i class="fa-solid fa-mug-hot"></i></span>';
}
```

### 2. 訂單詳情（文字版）

```html
<!-- 冷飲 -->
<i class="fa-solid fa-snowflake text-info"></i> 冷飲

<!-- 熱飲 -->
<i class="fa-solid fa-mug-hot text-warning"></i> 熱飲
```

### 3. 商品選擇（表單標籤）

```html
<!-- 冷飲選項 -->
<label class="form-check-label">
    <span><i class="fa-solid fa-snowflake text-info"></i> 冷飲</span>
    <span class="text-muted">+$10</span>
</label>

<!-- 熱飲選項 -->
<label class="form-check-label">
    <span><i class="fa-solid fa-mug-hot text-warning"></i> 熱飲</span>
    <span class="text-muted">+$15</span>
</label>
```

### 4. 購物車（動態渲染）

```javascript
const drinkIcon = item.drink_type === 'cold' 
    ? '<i class="fa-solid fa-snowflake text-info"></i>' 
    : '<i class="fa-solid fa-mug-hot text-warning"></i>';
const drinkName = item.drink_type === 'cold' ? '冷飲' : '熱飲';
const drinkHtml = `飲品：${drinkIcon} ${drinkName}`;
```

---

## 🌈 顏色參考

### Bootstrap 顏色類

| 顏色類 | 用途 | 效果 |
|--------|-----|------|
| `text-info` | 冷飲文字 | 淺藍色文字 |
| `text-warning` | 熱飲文字 | 橙黃色文字 |
| `bg-info` | 冷飲背景 | 淺藍色背景 |
| `bg-warning` | 熱飲背景 | 橙黃色背景 |

---

## 🔄 遷移說明

### 從 Emoji 遷移到 Font Awesome

**原始（Emoji）：**
```html
🧊 冷飲
☕ 熱飲
```

**新版（Font Awesome）：**
```html
<i class="fa-solid fa-snowflake text-info"></i> 冷飲
<i class="fa-solid fa-mug-hot text-warning"></i> 熱飲
```

**優勢：**
- ✅ 跨平台一致性（不受 OS emoji 渲染影響）
- ✅ 可自定義顏色和大小
- ✅ 更專業的視覺效果
- ✅ 更好的無障礙支持（screen readers）
- ✅ 不會因字體缺失而顯示為方框

---

## 📚 相關資源

- **Font Awesome 官網**：https://fontawesome.com/
- **圖標搜索**：https://fontawesome.com/search
- **Bootstrap 顏色**：https://getbootstrap.com/docs/5.3/utilities/colors/

---

## 🎨 其他可用的飲品圖標

如果未來需要更多飲品圖標：

| 圖標 | 代碼 | 適用場景 |
|------|------|---------|
| 🧋 | `<i class="fa-solid fa-martini-glass-citrus"></i>` | 調飲/雞尾酒 |
| 🥤 | `<i class="fa-solid fa-glass-water"></i>` | 一般飲料 |
| 🍺 | `<i class="fa-solid fa-beer-mug-empty"></i>` | 啤酒 |
| 🍷 | `<i class="fa-solid fa-wine-glass"></i>` | 紅酒 |
| 🥛 | `<i class="fa-solid fa-glass-water"></i>` | 牛奶/乳飲 |

---

**更新日期**：2025-11-06  
**版本**：Font Awesome 6.7.1  
**維護者**：開發團隊



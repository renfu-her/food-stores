# 更新日誌 (Changelog)

## 2025-11-04 (下午) - 產品管理與分類系統完善

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
- ✅ `public/templates/backend/categories.html` - 分類管理頁面
- ✅ `public/templates/backend/products/add.html` - 產品新增頁面（含快速分類管理）
- ✅ `public/templates/backend/products/edit.html` - 產品編輯頁面（含圖片和分類管理）
- ✅ `public/uploads/shops/.gitkeep` - 商店上傳目錄
- ✅ `public/uploads/products/.gitkeep` - 產品上傳目錄
- ✅ `public/uploads/.gitignore` - Git 忽略規則（shops + products）

### 🔄 修改文件
- ✅ `app/models.py` - 新增 ShopImage 和 ProductImage 模型、images 關係
- ✅ `app/__init__.py` - 註冊圖片 API、靜態文件路由
- ✅ `app/config.py` - 文件上傳配置
- ✅ `app/routes/backend.py` - 新增 categories 路由、修復 products 數據
- ✅ `public/templates/base/backend_base.html` - 新增分類管理菜單
- ✅ `public/templates/backend/shops/add.html` - 配料表單優化、繁體中文
- ✅ `public/templates/backend/shops/edit.html` - 圖片管理、配料優化
- ✅ `public/templates/backend/shops/list.html` - 修復 URL、語法錯誤
- ✅ `public/templates/backend/users/list.html` - 修復 URL
- ✅ `public/templates/backend/products/list.html` - 修復結構、URL
- ✅ `public/templates/backend/orders/list.html` - 修復 URL、價格顯示
- ✅ `public/templates/store/index.html` - 商店圖片顯示、繁體中文
- ✅ `public/templates/store/shop.html` - 產品圖片顯示、價格整數化
- ✅ `public/templates/store/product.html` - 產品主圖顯示、價格整數化
- ✅ 其他 10+ 個模板文件（價格、繁體中文調整）

### 📈 項目規模
```
當前統計：
├── HTML 模板：42 個
├── CSS 文件：4 個
├── JavaScript 文件：4 個
├── API 路由：10 個（users, shops, products, orders, toppings, categories, shop_images, product_images, auth, websocket）
├── 數據模型：10 個（User, Shop, ShopImage, Product, ProductImage, Category, Topping, Order, OrderItem, UpdateLog）
└── 後台管理頁面：9 個（儀表板、使用者、店鋪、產品、分類、訂單、系統 Log、詳情頁等）
```

### 🎯 圖片管理功能對比
```
商店圖片管理：
├── 上傳目錄：public/uploads/shops/
├── 文件命名：shop_{id}_{timestamp}.{ext}
├── 前台顯示：首頁店鋪列表
└── 管理位置：/backend/shops/:id/edit

產品圖片管理：
├── 上傳目錄：public/uploads/products/
├── 文件命名：product_{id}_{timestamp}.{ext}
├── 前台顯示：產品列表、產品詳情頁
└── 管理位置：/backend/products/:id/edit

共同特點：
├── 1:1 正方形顯示（padding-top: 100%）
├── 拖拽排序（SortableJS）
├── 主圖標記（第一張）
├── 無圖片顯示 icon（商店🏪、產品📦）
├── 關聯刪除（刪除記錄時刪除文件）
└── 更新日誌記錄
```

---

## 2025-11-04 (上午) - 重大更新

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

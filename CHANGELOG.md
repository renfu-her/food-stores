# 更新日誌 (CHANGELOG)

> 本檔案記錄所有重要的系統修改、新增功能、Bug 修復等。

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

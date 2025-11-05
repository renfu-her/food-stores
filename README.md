# 🍔 Food Stores - 多店鋪食品訂購平台

一個功能完整的多店鋪食品訂購管理系統，基於 Flask 開發，支援商品管理、訂單處理、即時通知、配料系統和飲品選項。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📑 目錄

- [功能特性](#功能特性)
- [系統架構](#系統架構)
- [技術棧](#技術棧)
- [安裝說明](#安裝說明)
- [使用指南](#使用指南)
- [權限管理](#權限管理)
- [操作手冊](#操作手冊)
- [API 文檔](#api-文檔)
- [常見問題](#常見問題)

---

## ✨ 功能特性

### 🎯 核心功能

#### **三個獨立管理介面**
- 🔧 **後台管理（Backend）** - 超級管理員控制台
- 🏪 **店鋪管理（Shop Admin）** - 店主管理介面
- 🛒 **商城前台（Customer）** - 顧客購物介面

#### **完整的電商功能**
- ✅ 使用者認證系統（支援 Laravel 相容的 bcrypt 密碼加密）
- ✅ 多店鋪管理（每個店主可管理多家店鋪）
- ✅ 產品管理（CRUD、分類、庫存、上下架）
- ✅ 訂單處理（購物車、結帳、訂單狀態追蹤）
- ✅ 配料系統（自訂配料、價格、數量限制）
- ✅ **飲品選項**（冷飲/熱飲、可自訂加價） ⭐ 新功能
- ✅ 即時通知（WebSocket 推送訂單更新）
- ✅ 訂單編號系統（自訂前綴 + 店鋪 ID + 日期 + 流水號）
- ✅ 首頁 Banner 管理（輪播圖、標題、副標題、連結）
- ✅ 關於我們 / 最新消息（Markdown 編輯器）
- ✅ 地址管理（整合 TWzipcode 台灣郵遞區號）
- ✅ 密碼強度驗證（Low/Middle/High）

#### **權限管理**
- 🔐 基於角色的存取控制（RBAC）
  - **Admin** - 完整系統管理權限
  - **Store Admin** - 店鋪和產品管理權限
  - **Customer** - 瀏覽和購買權限

#### **即時功能（WebSocket）**
- 🔔 新訂單即時通知（聲音 + 彈窗）
- 📦 訂單狀態即時更新
- 💰 產品價格/庫存即時同步
- 🛎️ 店主訂單通知（紅點提示 + 橫幅）

---

## 🏗️ 系統架構

### 使用者角色與權限

```
┌─────────────────────────────────────────────────┐
│                    系統架構                      │
├─────────────────────────────────────────────────┤
│                                                 │
│  🔧 Admin (超級管理員)                          │
│  ├── 管理所有店鋪                               │
│  ├── 管理所有產品                               │
│  ├── 查看所有訂單                               │
│  ├── 系統設定（訂單編號前綴、郵件設定）          │
│  ├── 用戶管理                                   │
│  └── 內容管理（Banner、關於我們、最新消息）      │
│                                                 │
│  🏪 Store Admin (店主)                          │
│  ├── 管理自己的店鋪                             │
│  ├── 新增/編輯/刪除產品                         │
│  ├── 管理配料（Toppings）                       │
│  ├── 處理訂單（接單、完成、取消）               │
│  ├── 查看營業數據                               │
│  └── 接收訂單通知                               │
│                                                 │
│  🛒 Customer (顧客)                             │
│  ├── 瀏覽店鋪和產品                             │
│  ├── 加入購物車                                 │
│  ├── 選擇配料和飲品                             │
│  ├── 下單結帳                                   │
│  ├── 查看訂單狀態                               │
│  └── 個人資料管理                               │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 資料模型關係

```
User (使用者)
  ├── has many: Shop (店鋪)
  └── has many: Order (訂單)

Shop (店鋪)
  ├── belongs to: User (擁有者)
  ├── has many: Product (產品)
  ├── has many: Topping (配料)
  └── has many: Order (訂單)

Product (產品)
  ├── belongs to: Shop (店鋪)
  ├── belongs to: Category (分類)
  ├── has many: ProductImage (圖片)
  ├── has many: Topping (配料) - many-to-many
  └── has fields: 冷飲/熱飲選項 ⭐

Order (訂單)
  ├── belongs to: User (使用者)
  ├── belongs to: Shop (店鋪)
  └── has many: OrderItem (訂單項目)

OrderItem (訂單項目)
  ├── belongs to: Order (訂單)
  ├── belongs to: Product (產品)
  ├── has many: Topping (配料) - many-to-many
  └── has fields: 飲品類型 & 價格 ⭐
```

---

## 🛠️ 技術棧

### 後端
- **Flask 2.3+** - Web 框架
- **SQLAlchemy** - ORM 資料庫操作
- **Flask-Migrate** - 資料庫遷移管理
- **Flask-SocketIO** - WebSocket 即時通訊
- **PyMySQL** - MySQL 資料庫驅動
- **python-dotenv** - 環境變數管理
- **bcrypt** - 密碼加密（Laravel 相容）

### 前端
- **Jinja2** - 模板引擎
- **Bootstrap 5** - UI 框架
- **jQuery** - JavaScript 庫
- **Socket.IO Client** - WebSocket 客戶端
- **DataTables** - 表格資料展示
- **SortableJS** - 拖曳排序
- **EasyMDE** - Markdown 編輯器
- **marked.js** - Markdown 渲染
- **TWzipcode** - 台灣郵遞區號

### 資料庫
- **MySQL 8.0+** - 主要資料庫

---

## 📦 安裝說明

### 1️⃣ 環境需求

- Python 3.8 或更高版本
- MySQL 8.0 或更高版本
- pip（Python 套件管理器）

### 2️⃣ 克隆專案

```bash
git clone <repository-url>
cd food-stores
```

### 3️⃣ 安裝依賴

```bash
pip install -r requirements.txt
```

### 4️⃣ 配置環境變數

複製環境變數範例文件：

```bash
cp env.example .env
```

編輯 `.env` 文件，設定您的配置：

```ini
# Flask 應用配置
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=False

# 數據庫配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_NAME=food-stores

# SQLAlchemy 配置
SQLALCHEMY_ECHO=False

# Session 配置
SESSION_LIFETIME_DAYS=7

# SocketIO 配置
SOCKETIO_ASYNC_MODE=threading
SOCKETIO_CORS_ALLOWED_ORIGINS=*

# 開發/生產環境
FLASK_ENV=development
```

⚠️ **安全提示：**
- `.env` 文件包含敏感資訊，已被 `.gitignore` 排除
- 請勿將 `.env` 提交到版本控制系統
- 生產環境請使用強密碼和安全的 SECRET_KEY

### 5️⃣ 創建資料庫

在 MySQL 中創建資料庫：

```sql
CREATE DATABASE food-stores CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6️⃣ 初始化資料庫

```bash
python init_db.py
```

這將：
- 建立所有資料表
- 建立預設管理員帳戶
- 建立範例分類資料

### 7️⃣ 運行應用

**開發模式：**
```bash
python app.py
```

**生產模式（使用 uWSGI）：**
```bash
uwsgi --ini uwsgi.ini
```

應用將運行在 `http://localhost:5000`

---

## 📖 使用指南

### 預設帳號

初始化後會自動創建以下帳號：

| 角色 | Email | 密碼 | 說明 |
|------|-------|------|------|
| **Admin** | admin@admin.com | admin123 | 超級管理員 |
| **Store Admin** | store1@store.com | Qq123456@ | 範例店主 |

⚠️ **首次登入後請立即修改密碼！**

### 訪問路徑

```
後台管理：   http://localhost:5000/backend
店鋪管理：   http://localhost:5000/shop
商城前台：   http://localhost:5000/
```

---

## 🔐 權限管理

### 核心原則

本系統採用**基於角色的存取控制（RBAC）**，確保不同角色只能存取和修改自己權限範圍內的資源。

### 三種角色的權限範圍

| 角色 | 權限範圍 | 關鍵過濾條件 |
|------|---------|-------------|
| **Admin<br/>（超級管理員）** | • 所有店鋪<br/>• 所有產品<br/>• 所有訂單<br/>• 系統設定<br/>• 內容管理 | `Shop.query.all()` |
| **Store Admin<br/>（店主）** | • 自己的店鋪<br/>• 自己店鋪的產品<br/>• 自己店鋪的訂單<br/>• 自己店鋪的配料 | `Shop.query.filter_by(owner_id=user.id)`<br/>`Product.query.filter_by(shop_id=shop.id)` |
| **Customer<br/>（顧客）** | • 瀏覽所有公開店鋪和產品<br/>• 自己的訂單<br/>• 個人資料 | `Order.query.filter_by(user_id=user.id)` |

### 權限實現方式

#### 1️⃣ **路由層級控制**

使用 `@role_required()` 裝飾器：

```python
@app.route('/shop/products')
@role_required('store_admin')
def products():
    user = get_current_user()
    # ✅ 只查詢當前用戶擁有的店鋪
    shop = Shop.query.filter_by(owner_id=user.id).first_or_404()
    # ✅ 只查詢該店鋪的產品
    products = Product.query.filter_by(shop_id=shop.id).all()
    return render_template('shop/products.html', products=products)
```

#### 2️⃣ **API 層級控制**

在修改操作前檢查 `owner_id`：

```python
@app.route('/api/shops/<int:shop_id>', methods=['PUT'])
@login_required
def update_shop(shop_id):
    user = get_current_user()
    shop = Shop.query.get_or_404(shop_id)
    
    # ✅ 權限檢查
    if user.role != 'admin' and shop.owner_id != user.id:
        return jsonify({'error': 'forbidden'}), 403
    
    # 執行更新...
```

#### 3️⃣ **查詢過濾**

**店主（Store Admin）** 只能看到自己的資源：

```python
# 查詢店鋪
my_shops = Shop.query.filter_by(owner_id=user.id).all()

# 查詢產品
my_products = Product.query.filter_by(shop_id=shop.id).all()

# 查詢訂單
my_orders = Order.query.filter_by(shop_id=shop.id).all()
```

**管理員（Admin）** 可以查詢所有資源：

```python
all_shops = Shop.query.all()
all_products = Product.query.all()
all_orders = Order.query.all()
```

### 權限檢查流程圖

```
用戶請求
  ↓
檢查登入狀態 (@login_required)
  ↓
檢查角色權限 (@role_required)
  ↓
根據角色過濾資源
  ├─ Admin → 查詢所有資源
  ├─ Store Admin → filter_by(owner_id=user.id)
  └─ Customer → filter_by(user_id=user.id)
  ↓
返回結果
```

### 安全特性

✅ **資料隔離** - 店主之間無法互相訪問資料  
✅ **權限驗證** - 所有修改操作都需要驗證 `owner_id`  
✅ **智能重定向** - 未登入時根據路由自動重定向到對應登入頁  
✅ **錯誤處理** - 返回清晰的 403 Forbidden 或 404 Not Found  

### 📖 詳細文檔

| 文檔 | 說明 |
|------|------|
| **[docs/PERMISSIONS.md](docs/PERMISSIONS.md)** | 權限管理架構（1000+ 行） |
| **[docs/SHOP_ADMIN_GUIDE.md](docs/SHOP_ADMIN_GUIDE.md)** | 店主操作指南（完整流程） |
| **[docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** | 快速參考卡片（對比表格） |

**權限架構文檔包括：**
- 三種角色的詳細權限說明
- 路由和 API 的實現範例
- 裝飾器使用說明
- 權限檢查檢查清單
- 測試場景和測試方法
- 安全建議和最佳實踐

---

## 📚 操作手冊

### 🔧 後台管理（Admin）

#### 1. 登入後台

1. 訪問 `http://localhost:5000/backend`
2. 輸入管理員帳號密碼
3. 進入後台儀表板

#### 2. 系統設定

**訂單編號設定：**
- 導航至：`系統設定` → `訂單設定`
- 設定訂單前綴（如：ORDER、ORD、FD）
- 格式：`前綴 + 商店ID + 日期 + 流水號`
- 範例：`ORDER-A001-20251106-00001`

**郵件設定（預留）：**
- SMTP 伺服器設定
- 寄件人資訊
- 測試郵件發送

#### 3. 首頁 Banner 管理

1. 導航至：`首頁管理` → `Banner 管理`
2. 點擊「新增 Banner」
3. 填寫：
   - Banner 名稱（內部識別用）
   - 標題（顯示在首頁）
   - 副標題（顯示在首頁）
   - 連結（點擊跳轉位置）
   - 上傳圖片（建議尺寸：1920x480）
   - 顯示順序（拖曳排序）
   - 啟用/停用
4. 儲存

**拖曳排序：**
- 在列表頁面直接拖曳調整順序
- 自動儲存

#### 4. 關於我們 / 最新消息

**關於我們：**
1. 導航至：`內容管理` → `關於我們`
2. 點擊「新增」
3. 使用 Markdown 編輯器撰寫內容
4. 支援：標題、內容、啟用狀態、顯示順序

**最新消息：**
1. 導航至：`內容管理` → `最新消息`
2. 點擊「新增消息」
3. 填寫：標題、內容（Markdown）、上傳圖片、發布日期
4. 前台以卡片式呈現（Flickr 風格）

#### 5. 商店管理

**查看所有商店：**
- 導航至：`商店管理`
- 可查看、編輯、停用商店
- 設定商店訂單 ID（用於訂單編號）

**商店訂單 ID：**
- 每個商店必須有唯一的訂單 ID
- 只能使用大寫字母和數字（如：A001, SHOP01）
- 長度：2-20 個字符
- 用於生成訂單編號：`ORDER-A001-20251106-00001`

---

### 🏪 店鋪管理（Store Admin）

#### 1. 登入店鋪後台

1. 訪問 `http://localhost:5000/shop`
2. 輸入店主帳號密碼
3. 進入店鋪儀表板

#### 2. 商品管理

**新增商品：**

1. 導航至：`產品管理` → `新增產品`
2. 填寫基本資訊：
   - 產品名稱 *（必填）
   - 產品描述
   - 分類 *（必填）
   - 單價 *（必填）
   - 折扣價（選填）
   - 庫存數量

3. **配料設定**（選填）：
   - 從店鋪配料列表勾選
   - 可設定每個配料的價格（覆蓋預設）
   - 店鋪可設定配料數量上限（如：最多 5 個）

4. **飲品選項**（選填） ⭐ **新功能**：
   ```
   ☑️ 提供冷飲
      └─ 冷飲加價：$ 10  (可為 0)
   
   ☑️ 提供熱飲
      └─ 熱飲加價：$ 5   (可為 0)
   ```
   - 勾選「提供冷飲」並設定加價
   - 勾選「提供熱飲」並設定加價
   - 加價可設為 0（免費）
   - 不勾選則不提供飲品選項
   - 顧客下單時可選擇：冷飲/熱飲/不需要

5. 上傳產品圖片
6. 設定是否立即上架
7. 儲存

**編輯商品：**
- 點擊商品列表的「編輯」按鈕
- 修改任何欄位（包括飲品選項）
- 儲存變更

**商品狀態：**
- 上架：顧客可見並可購買
- 下架：顧客不可見

#### 3. 配料管理

**新增配料：**
1. 導航至：`配料管理` → `新增配料`
2. 填寫：
   - 配料名稱（如：珍珠、椰果、布丁）
   - 預設價格（可為 0）
   - 啟用/停用
3. 儲存

**配料價格覆蓋：**
- 在產品中可覆蓋配料的預設價格
- 範例：珍珠在 A 產品 +$10，在 B 產品 +$5

**配料數量限制：**
- 在「店鋪設定」中設定每筆訂單最多幾個配料
- 前台會自動檢查並限制

#### 4. 訂單管理

**接收新訂單：**
- 🔔 **即時通知**：收到新訂單時會：
  - 鈴鐺圖標顯示紅點
  - 播放提示音
  - 頂部顯示綠色橫幅通知
  - 顯示：訂單編號、金額、時間

**處理訂單：**
1. 點擊通知或導航至「訂單管理」
2. 查看訂單詳情：
   - 訂單編號（如：ORDER-A001-20251106-00001）
   - 顧客資訊（姓名、電話、地址）
   - 商品列表（名稱、數量、單價）
   - **配料**（如果有選擇）
   - **飲品**（🧊 冷飲 或 ☕ 熱飲，如果有選擇）⭐
   - 總金額
   - 配送備註

3. 更新訂單狀態：
   - **待處理（Pending）** - 新訂單
   - **處理中（Processing）** - 準備中
   - **已完成（Completed）** - 已交付
   - **已取消（Cancelled）** - 取消訂單

**訂單編號說明：**
```
ORDER-A001-20251106-00001
  │     │      │       │
  │     │      │       └─ 流水號（5位）
  │     │      └───────── 日期（YYYYMMDD）
  │     └──────────────── 商店訂單ID
  └────────────────────── 訂單前綴（後台設定）
```

---

### 🛒 商城前台（Customer）

#### 1. 註冊 / 登入

**註冊新帳號：**
1. 點擊「註冊」
2. 填寫：姓名、Email、密碼
3. **密碼強度要求**：
   - 至少 8 個字符
   - 必須達到「中等」強度
   - 包含大小寫字母、數字、特殊符號
   - 即時顯示強度指示器（低/中/高）
4. 送出註冊

**登入：**
- 使用 Email 和密碼登入
- 登入後可查看「個人資料」、「我的訂單」

#### 2. 瀏覽商店和商品

**首頁：**
- 輪播 Banner（可點擊跳轉）
- 商店列表（卡片式，4列顯示）
- 商店圖片固定高度 200px

**商店頁面：**
- 查看商店資訊和 Banner
- 瀏覽商品列表
- 按分類篩選
- 商品卡片顯示：
  - 圖片（可點擊查看詳情）
  - 名稱（可點擊查看詳情）
  - 價格（含折扣價）
  - 庫存狀態
  - 「查看詳情」按鈕

#### 3. 查看商品詳情 ⭐ 重點

點擊商品後，會打開詳情模態框：

**1. 基本資訊：**
- 商品名稱
- 詳細描述
- 價格（含折扣）
- 庫存狀態
- 商品圖片輪播

**2. 配料選擇**（如果商品有提供）：
```
☑️ 珍珠  +$10
☑️ 椰果  +$5
☐  布丁  FREE
☐  仙草  +$8

已選 2 個配料（最多 5 個）
```
- 可複選（Checkbox）
- 顯示價格或 FREE
- 達到上限時自動禁用其他選項

**3. 飲品選擇**（如果商品有提供） ⭐ **新功能**：
```
◉ 🧊 冷飲  +$10
◯ ☕ 熱飲  +$5
◯ 不需要
```
- 單選（Radio）
- 預設選擇「不需要」
- 顯示加價（如果有）
- 選擇後自動更新總價

**4. 數量選擇：**
- 輸入數量（受庫存限制）

**5. 總價計算：**
```
總價 = (商品價格 + 配料總價 + 飲品價格) × 數量

範例：
  商品：奶茶 $50
  配料：珍珠 +$10, 椰果 +$5
  飲品：冷飲 +$10
  數量：2 杯
  ─────────────────────
  總價 = (50 + 10 + 5 + 10) × 2 = $150
```

**6. 動作按鈕：**
- 「加入購物車」- 加入後繼續購物
- 「直接結帳」- 加入購物車並跳轉到結帳頁

#### 4. 購物車

查看購物車內容：
- 商品名稱
- 單價（已含配料和飲品）
- 配料列表（如：珍珠 +$10、椰果 +$5）
- **飲品選項**（如：🧊 冷飲 +$10）⭐
- 數量（可調整）
- 小計
- 移除按鈕

調整數量或刪除商品後，自動更新總金額。

#### 5. 結帳

**填寫收貨資訊：**
1. 收貨人姓名 *
2. 收貨人電話 *
3. 收貨地址 *（整合 TWzipcode）
   - 縣市（下拉選單）
   - 區域（下拉選單）
   - 郵遞區號（自動帶入）
   - 詳細地址（街道、樓層）
4. 配送備註（選填）
5. 付款方式
   - 貨到付款（COD）

**自動帶入：**
- 首次下單後，收貨資訊會自動儲存
- 下次結帳時自動帶入，可修改

**送出訂單：**
- 確認資訊無誤後，點擊「確認訂單」
- 系統會為每個店鋪分別生成訂單
- 生成訂單編號
- 扣除庫存
- 發送通知給店主

#### 6. 查看訂單

**我的訂單：**
1. 點擊右上角頭像 → 「我的訂單」
2. 查看訂單列表：
   - 訂單編號
   - 店鋪名稱
   - 訂單狀態
   - 總金額
   - 下單時間

3. 點擊訂單查看詳情：
   - 訂單資訊
   - 收貨資訊
   - 商品列表（含配料和飲品） ⭐
   - 總金額

---

## 🔧 進階功能

### 飲品選項詳細說明 ⭐

**商品設定（店主）：**
```yaml
商品: 珍珠奶茶
  基本價格: $50
  
  飲品選項:
    冷飲:
      啟用: ✓
      加價: $10
    熱飲:
      啟用: ✓
      加價: $5
```

**前台顯示（顧客）：**
```
商品詳情
├── 珍珠奶茶 $50
│
├── 配料選擇
│   ☑️ 珍珠 +$10
│   ☐  椰果 +$5
│
└── 飲品選擇  ⭐ 新功能
    ◯ 🧊 冷飲 +$10
    ◯ ☕ 熱飲 +$5
    ◉ 不需要（預設）

總價：$60（50 + 10 + 0）
```

**訂單記錄：**
```json
{
  "product": "珍珠奶茶",
  "quantity": 2,
  "unit_price": 60,
  "toppings": [
    {"name": "珍珠", "price": 10}
  ],
  "drink_type": "cold",      // 'cold' | 'hot' | null
  "drink_price": 10,
  "total": 120
}
```

**訂單詳情顯示：**
```
訂單項目
┌─────────────┬────┬────┬────────┬─────┬──────┐
│ 商品名稱    │單價│數量│ 配料   │飲品 │ 小計 │
├─────────────┼────┼────┼────────┼─────┼──────┤
│ 珍珠奶茶    │$60 │ 2  │ 珍珠   │🧊冷飲│ $120 │
└─────────────┴────┴────┴────────┴─────┴──────┘
                                   總計：$120
```

---

## 📡 API 文檔

### 認證 API

#### 註冊
```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "張三",
  "email": "user@example.com",
  "password": "Secure123@"
}
```

#### 登入
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "Secure123@"
}
```

#### 登出
```http
POST /api/auth/logout
```

#### 獲取當前使用者
```http
GET /api/auth/me
```

---

### 商品 API

#### 獲取商品列表
```http
GET /api/products?shop_id=1&category_id=2&is_active=true
```

**回應範例：**
```json
{
  "products": [
    {
      "id": 1,
      "name": "珍珠奶茶",
      "description": "經典珍珠奶茶",
      "unit_price": 50,
      "discounted_price": null,
      "stock_quantity": 100,
      "is_active": true,
      "has_cold_drink": true,
      "cold_drink_price": 10,
      "has_hot_drink": true,
      "hot_drink_price": 5,
      "toppings": [
        {"id": 1, "name": "珍珠", "price": 10},
        {"id": 2, "name": "椰果", "price": 5}
      ],
      "images": [
        {"id": 1, "image_path": "/uploads/products/tea.jpg"}
      ]
    }
  ],
  "total": 1
}
```

#### 獲取商品詳情
```http
GET /api/products/1
```

#### 創建商品（店主/管理員）
```http
POST /api/products
Content-Type: application/json

{
  "shop_id": 1,
  "name": "珍珠奶茶",
  "description": "經典珍珠奶茶",
  "category_id": 2,
  "unit_price": 50,
  "stock_quantity": 100,
  "is_active": true,
  "has_cold_drink": true,
  "cold_drink_price": 10,
  "has_hot_drink": true,
  "hot_drink_price": 5
}
```

#### 更新商品
```http
PUT /api/products/1
Content-Type: application/json

{
  "name": "經典珍珠奶茶",
  "unit_price": 55,
  "has_cold_drink": true,
  "cold_drink_price": 15
}
```

---

### 購物車 API

#### 加入購物車
```http
POST /api/cart/add
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 2,
  "toppings": [
    {"id": 1, "name": "珍珠", "price": 10}
  ],
  "drink_type": "cold",
  "drink_price": 10
}
```

#### 獲取購物車
```http
GET /api/cart
```

#### 更新購物車項目數量
```http
PUT /api/cart/update
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 3
}
```

#### 移除購物車項目
```http
DELETE /api/cart/remove
Content-Type: application/json

{
  "product_id": 1
}
```

#### 清空購物車
```http
DELETE /api/cart/clear
```

---

### 訂單 API

#### 創建訂單
```http
POST /api/orders
Content-Type: application/json

{
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "toppings": [
        {"id": 1, "price": 10}
      ],
      "drink_type": "cold",
      "drink_price": 10
    }
  ],
  "recipient_name": "張三",
  "recipient_phone": "0912345678",
  "county": "台北市",
  "district": "信義區",
  "zipcode": "110",
  "address": "信義路五段7號",
  "delivery_note": "請放管理室",
  "payment_method": "cod"
}
```

**回應範例：**
```json
{
  "message": "成功建立 1 個訂單",
  "orders": [
    {
      "order_id": 1,
      "order_number": "ORDER-A001-20251106-00001",
      "shop_id": 1,
      "total_price": 120
    }
  ]
}
```

#### 獲取訂單列表
```http
GET /api/orders?status=pending&shop_id=1
```

#### 獲取訂單詳情
```http
GET /api/orders/1
```

**回應範例：**
```json
{
  "id": 1,
  "order_number": "ORDER-A001-20251106-00001",
  "user_id": 1,
  "shop_id": 1,
  "total_price": 120,
  "status": "pending",
  "recipient_name": "張三",
  "recipient_phone": "0912345678",
  "recipient_address": "110 台北市信義區信義路五段7號",
  "items": [
    {
      "product": {"id": 1, "name": "珍珠奶茶"},
      "quantity": 2,
      "unit_price": 60,
      "drink_type": "cold",
      "drink_price": 10,
      "toppings": [
        {"name": "珍珠", "price": 10}
      ]
    }
  ]
}
```

#### 更新訂單狀態
```http
PUT /api/orders/1/status
Content-Type: application/json

{
  "status": "processing"
}
```

---

## 🔌 WebSocket 事件

### 客戶端監聽事件

```javascript
// 連接 WebSocket
const socket = io();

// 加入店鋪頻道（店主）
socket.emit('join', {room: '/shop/1'});

// 監聽新訂單
socket.on('new_order', function(data) {
  console.log('新訂單:', data);
  // data.order_id
  // data.order_number
  // data.shop_id
  // data.total_price
});

// 監聽訂單更新
socket.on('order_updated', function(data) {
  console.log('訂單更新:', data);
  // data.order_id
  // data.status
});

// 監聽產品更新
socket.on('product_updated', function(data) {
  console.log('產品更新:', data);
  // data.product_id
  // data.unit_price
  // data.stock_quantity
});
```

---

## 📁 專案結構

```
food-stores/
├── app/                          # 應用主目錄
│   ├── __init__.py              # Flask 應用初始化
│   ├── models.py                # 資料模型（User, Shop, Product, Order 等）
│   ├── config.py                # 配置檔案
│   │
│   ├── routes/                   # 路由定義
│   │   ├── api/                 # API 路由
│   │   │   ├── auth.py         # 認證 API
│   │   │   ├── products.py     # 產品 API
│   │   │   ├── orders.py       # 訂單 API
│   │   │   ├── cart.py         # 購物車 API
│   │   │   ├── shops.py        # 店鋪 API
│   │   │   └── ...
│   │   ├── backend.py           # 後台管理路由
│   │   ├── store_admin.py       # 店鋪管理路由
│   │   └── customer.py          # 商城前台路由
│   │
│   └── utils/                    # 工具函數
│       ├── decorators.py        # 裝飾器（role_required 等）
│       ├── validators.py        # 驗證器
│       ├── password_strength.py # 密碼強度檢查
│       ├── order_number.py      # 訂單編號生成
│       └── update_logger.py     # 更新日誌
│
├── public/                       # 前端資源
│   ├── templates/               # Jinja2 模板
│   │   ├── base/               # 基礎模板
│   │   │   ├── base.html      # 主模板
│   │   │   ├── backend_base.html
│   │   │   ├── shop_base.html
│   │   │   └── store_base.html
│   │   ├── backend/            # 後台模板
│   │   ├── shop/               # 店鋪管理模板
│   │   └── store/              # 商城前台模板
│   │
│   ├── static/                  # 靜態檔案
│   │   ├── css/                # 樣式表
│   │   ├── js/                 # JavaScript
│   │   └── images/             # 圖片
│   │
│   └── uploads/                 # 上傳檔案
│       ├── shops/              # 店鋪圖片
│       ├── products/           # 產品圖片
│       ├── banners/            # Banner 圖片
│       └── news/               # 最新消息圖片
│
├── migrations/                  # 資料庫遷移檔案
│   └── versions/               # 遷移版本
│
├── app.py                       # 應用入口（開發模式）
├── wsgi.py                      # uWSGI 入口（生產模式）
├── init_db.py                   # 資料庫初始化腳本
├── requirements.txt             # Python 依賴套件
├── .env                         # 環境變數（不納入版本控制）
├── env.example                  # 環境變數範例
├── CHANGELOG.md                 # 更新日誌
└── README.md                    # 專案說明（本檔案）
```

---

## ❓ 常見問題

### Q1: 忘記管理員密碼怎麼辦？

**A:** 可以通過以下步驟重置密碼：

```python
# reset_admin_password.py
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    admin = User.query.filter_by(email='admin@admin.com').first()
    if admin:
        admin.password_hash = generate_password_hash('新密碼')
        db.session.commit()
        print("密碼已重置")
```

```bash
python reset_admin_password.py
```

### Q2: 如何修改訂單編號格式？

**A:** 
1. 登入後台（Admin）
2. 導航至「系統設定」→「訂單設定」
3. 修改「訂單前綴」（如：ORDER、ORD、FD）
4. 商店訂單 ID 在「商店管理」中為每個商店單獨設定

### Q3: 商品沒有顯示飲品選項？

**A:** 請確認：
1. 在商品編輯頁面，確認「飲品選項」區塊
2. 至少勾選「提供冷飲」或「提供熱飲」
3. 設定加價（可為 0）
4. 儲存商品

### Q4: 如何設定配料數量上限？

**A:**
1. 登入店鋪管理
2. 導航至「店鋪設定」
3. 設定「每筆訂單最多配料數」（如：5 個）
4. 前台會自動限制

### Q5: 訂單通知沒有聲音？

**A:** 請確認：
1. 瀏覽器允許播放聲音（檢查瀏覽器設定）
2. 音量沒有靜音
3. WebSocket 連接正常（檢查瀏覽器 Console）

### Q6: 如何備份資料庫？

**A:**
```bash
# 備份
mysqldump -u root -p food-stores > backup_$(date +%Y%m%d).sql

# 還原
mysql -u root -p food-stores < backup_20251106.sql
```

### Q7: 如何更新資料庫結構？

**A:**
```bash
# 1. 修改 models.py
# 2. 生成遷移文件
flask db migrate -m "描述變更內容"

# 3. 檢查遷移文件
# 4. 應用遷移
flask db upgrade
```

### Q8: 生產環境部署建議？

**A:**
1. **Web Server**: Nginx + uWSGI
2. **Database**: MySQL 8.0+（配置主從複寫）
3. **Redis**: 用於 Session 和快取
4. **SSL**: 使用 Let's Encrypt 免費憑證
5. **備份**: 每日自動備份資料庫
6. **監控**: 使用 Sentry 或 ELK Stack
7. **CDN**: 靜態資源使用 CDN 加速

---

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

### 開發流程

1. Fork 本專案
2. 創建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

### 代碼規範

- 遵循 PEP 8 Python 代碼風格
- 函數和類別添加 Docstring
- 提交前執行測試
- 更新 CHANGELOG.md

---

## 📄 授權

本專案採用 MIT License - 詳見 [LICENSE](LICENSE) 文件

---

## 📧 聯絡方式

如有任何問題或建議，歡迎聯絡：

- Email: your-email@example.com
- GitHub Issues: [提交 Issue](https://github.com/your-repo/issues)

---

## 🙏 致謝

感謝以下開源專案：

- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Bootstrap](https://getbootstrap.com/)
- [Socket.IO](https://socket.io/)
- [DataTables](https://datatables.net/)
- [EasyMDE](https://github.com/Ionaru/easy-markdown-editor)
- [TWzipcode](https://github.com/essoduke/jQuery-TWzipcode)

---

<div align="center">
  <p>用 ❤️ 打造</p>
  <p>© 2025 Food Stores. All Rights Reserved.</p>
</div>

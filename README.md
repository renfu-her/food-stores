# Food Stores Flask Application

一個基於Flask的食品商店管理系統，支援多店鋪、產品管理、訂單處理和即時更新功能。

## 功能特性

- 三個獨立的管理介面（Backend後台、商店管理者、商城使用者）
- 使用者認證系統（Laravel相容的密碼雜湊）
- 店鋪和產品管理（CRUD操作）
- 訂單處理（pending/process/success狀態）
- 即時更新（Flask-SocketIO）- 訂單狀態、庫存/價格更新
- Toppings管理（支援價格覆蓋，price=0顯示為FREE）
- 權限控制（基於角色的存取控制）

## 技術棧

- Python Flask
- SQLAlchemy ORM
- Flask-Migrate（資料庫遷移）
- Flask-SocketIO（即時通訊）
- MySQL資料庫
- Laravel相容的密碼雜湊（bcrypt）

## 安裝和運行

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 配置環境變數

複製環境變數範例文件並配置：

```bash
# 複製範例文件
cp env.example .env

# 編輯 .env 文件，設定您的配置
```

**`.env` 文件配置項：**

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

⚠️ **重要提示：**
- `.env` 文件包含敏感資訊，已被 `.gitignore` 排除
- 請勿將 `.env` 提交到版本控制系統
- 使用 `env.example` 作為參考模板

### 3. 配置資料庫

確保MySQL資料庫已建立：
- 資料庫名：在 `.env` 中設定（預設：food-stores）
- 使用者名稱：在 `.env` 中設定（預設：root）
- 密碼：在 `.env` 中設定

### 4. 初始化資料庫

```bash
python init_db.py
```

這將建立所有資料表並建立預設管理員帳戶：
- Email: admin@admin.com
- Password: admin123

### 5. 運行應用

開發模式：
```bash
python app.py
```

生產模式（使用uWSGI）：
```bash
uwsgi --ini uwsgi.ini
```

或使用wsgi.py：
```bash
uwsgi --http :5000 --wsgi-file wsgi.py --callable application
```

## 專案結構

```
food-stores/
├── app/                    # 應用主目錄
│   ├── __init__.py        # Flask應用初始化
│   ├── models.py          # 資料模型
│   ├── config.py          # 配置檔案
│   ├── routes/            # 路由定義
│   └── utils/             # 工具函數
├── public/                 # 前端資源
│   ├── templates/         # 模板檔案
│   └── static/            # 靜態檔案
├── migrations/            # 資料庫遷移檔案
├── app.py                # 應用入口
├── wsgi.py               # uWSGI入口
└── requirements.txt      # Python依賴
```

## API端點

### 認證
- POST /api/auth/register - 使用者註冊
- POST /api/auth/login - 使用者登入
- POST /api/auth/logout - 使用者登出
- GET /api/auth/me - 獲取當前使用者資訊

### 店鋪
- GET /api/shops - 獲取店鋪列表
- GET /api/shops/:id - 獲取店鋪詳情
- POST /api/shops - 建立店鋪
- PUT /api/shops/:id - 更新店鋪
- DELETE /api/shops/:id - 刪除店鋪
- GET /api/shops/:id/toppings - 獲取店鋪toppings
- POST /api/shops/:id/toppings - 添加topping

### 產品
- GET /api/products - 獲取產品列表
- GET /api/products/:id - 獲取產品詳情
- POST /api/shops/:shop_id/products - 建立產品
- PUT /api/products/:id - 更新產品
- DELETE /api/products/:id - 刪除產品
- PUT /api/products/:id/stock - 更新庫存
- PUT /api/products/:id/status - 更新產品狀態

### 訂單
- GET /api/orders - 獲取訂單列表
- GET /api/orders/:id - 獲取訂單詳情
- POST /api/orders - 建立訂單
- PUT /api/orders/:id/status - 更新訂單狀態

### Toppings
- PUT /api/toppings/:id - 更新topping
- DELETE /api/toppings/:id - 刪除topping

## SocketIO事件

### 客戶端監聽的事件
- `order_updated` - 訂單狀態更新
- `product_updated` - 產品價格/庫存更新
- `product_status_changed` - 產品上架/下架
- `new_order` - 新訂單通知

### 客戶端發送的事件
- `join_shop` - 加入店鋪頻道
- `leave_shop` - 離開店鋪頻道

## 預設管理員帳戶

- Name: admin
- Email: admin@admin.com
- Password: admin123
- Role: admin

## 許可證

MIT License


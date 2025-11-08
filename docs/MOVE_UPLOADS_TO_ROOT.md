# 將 uploads 移動到專案根目錄 - 完整指南

## 🎯 目標

將上傳文件從 `public/uploads` 移動到專案根目錄的 `uploads`，與 `static` 的做法一致，簡化 Nginx 配置。

**移動前：**
```
quick-foods/
├── public/
│   └── uploads/
│       ├── shops/
│       ├── products/
│       ├── banners/
│       └── qrcodes/
└── app/
```

**移動後：**
```
quick-foods/
├── uploads/          ← 新位置
│   ├── shops/
│   ├── products/
│   ├── banners/
│   └── qrcodes/
├── public/
└── app/
```

---

## ✅ 已更新的程式碼

### 1. Flask 配置

**`app/config.py`** - 自動檢測 uploads 目錄：
```python
# 優先使用根目錄的 uploads，否則使用 public/uploads（向後兼容）
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
uploads_dir = os.path.join(BASE_DIR, 'uploads')
uploads_dir_public = os.path.join(BASE_DIR, 'public', 'uploads')
UPLOAD_FOLDER = uploads_dir if os.path.exists(uploads_dir) else uploads_dir_public
```

**`app/__init__.py`** - `/uploads/` 路由自動檢測：
```python
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    # 優先使用根目錄的 uploads，否則使用 public/uploads（向後兼容）
    uploads_dir = os.path.join(BASE_DIR, 'uploads')
    uploads_dir_public = os.path.join(BASE_DIR, 'public', 'uploads')
    upload_folder = uploads_dir if os.path.exists(uploads_dir) else uploads_dir_public
    return send_from_directory(upload_folder, filename)
```

### 2. 新增輔助函數

**`app/utils/upload_path.py`** - 統一處理上傳路徑：
- `get_upload_folder()` - 獲取上傳目錄路徑
- `get_upload_file_path()` - 根據相對路徑獲取絕對路徑

### 3. 更新的 API 路由

所有使用 `public/uploads` 路徑的 API 都已更新：

- ✅ `app/routes/api/shop_images.py` - 店鋪圖片
- ✅ `app/routes/api/product_images.py` - 產品圖片
- ✅ `app/routes/api/home_banners.py` - 首頁 Banner
- ✅ `app/routes/api/news.py` - 最新消息
- ✅ `app/routes/api/shop_banner.py` - 店鋪 Banner
- ✅ `app/routes/api/tables.py` - QRCode 生成和刪除
- ✅ `cleanup_old_images.py` - 清理腳本

**所有路徑現在都使用：**
```python
from app.utils.upload_path import get_upload_file_path, get_upload_folder

# 獲取文件路徑
file_path = get_upload_file_path(image_path, current_app.root_path)

# 獲取上傳目錄
upload_folder = get_upload_folder(current_app.root_path)
```

---

## 📋 遷移步驟

### 步驟 1: 執行遷移腳本

```bash
cd /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com

# 執行遷移腳本
python move_uploads_to_root.py
```

**或手動移動：**
```bash
# 複製文件
cp -r public/uploads uploads

# 確認文件
ls -la uploads/shops/
ls -la uploads/products/
ls -la uploads/banners/
ls -la uploads/qrcodes/
```

### 步驟 2: 更新 Nginx 配置

編輯 Nginx 配置文件，修改 `/uploads` location：

```nginx
# 修改前
location /uploads {
    alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/uploads;  # ❌
    expires 7d;
}

# 修改後
location /uploads {
    alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/uploads;  # ✅ 簡化了！
    expires 7d;
    add_header Cache-Control "public";
}
```

### 步驟 3: 重新載入服務

```bash
# 測試 Nginx 配置
sudo nginx -t

# 重新載入 Nginx
sudo systemctl reload nginx

# 重啟 Flask 應用
sudo systemctl restart quick-foods
# 或
sudo systemctl restart uwsgi
```

### 步驟 4: 驗證

```bash
# 檢查文件是否存在
ls -la /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/uploads/shops/

# 測試訪問
curl -I https://quick-foods.ai-tracks.com/uploads/shops/test.jpg

# 應該返回 200 OK
```

### 步驟 5: 清理舊文件（可選）

**備份後刪除：**
```bash
# 備份舊目錄
mv public/uploads public/uploads.backup

# 測試一段時間後，如果沒問題再刪除
# rm -rf public/uploads.backup
```

---

## 🔧 完整 Nginx 配置（移動後）

```nginx
server {
    listen 80;
    listen [::]:80;
    listen 443 ssl http2;
    listen [::]:443 ssl http2;

    server_name quick-foods.ai-tracks.com;

    {{ssl_certificate_key}}
    {{ssl_certificate}}

    if ($scheme != "https") {
        return 301 https://$host$request_uri;
    }

    {{root}}
    {{nginx_access_log}}
    {{nginx_error_log}}
    include /etc/nginx/global_settings;

    index index.html;

    location ~ /.well-known {
        auth_basic off;
        allow all;
    }

    # 靜態文件（簡化路徑，不需要 public/）
    location /static {
        alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/static;  # ✅
        expires 30d;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }

    # 上傳文件（簡化路徑，不需要 public/）
    location /uploads {
        alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/uploads;  # ✅
        expires 7d;
        add_header Cache-Control "public";
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:8093/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }

    location / {
        proxy_pass http://127.0.0.1:8093/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 900;
    }
}
```

---

## ✅ 優點

1. **簡化 Nginx 配置** - 不需要 `public/` 前綴
2. **與 static 一致** - 目錄結構更統一
3. **減少錯誤** - 路徑更簡單
4. **向後兼容** - 如果 `uploads` 不存在，自動使用 `public/uploads`

---

## 📊 路徑對照表

| 用途 | URL 路徑 | 實際文件路徑（移動後） | 實際文件路徑（移動前） |
|------|---------|---------------------|---------------------|
| **店鋪圖片** | `/uploads/shops/xxx.jpg` | `uploads/shops/xxx.jpg` | `public/uploads/shops/xxx.jpg` |
| **產品圖片** | `/uploads/products/xxx.jpg` | `uploads/products/xxx.jpg` | `public/uploads/products/xxx.jpg` |
| **Banner** | `/uploads/banners/xxx.jpg` | `uploads/banners/xxx.jpg` | `public/uploads/banners/xxx.jpg` |
| **QRCode** | `/uploads/qrcodes/...` | `uploads/qrcodes/...` | `public/uploads/qrcodes/...` |

---

## 🧪 驗證清單

- [ ] 文件已移動到 `uploads/` 目錄
- [ ] Flask 配置已更新（自動檢測）
- [ ] Nginx 配置已更新（`alias .../uploads`）
- [ ] Nginx 配置測試通過（`sudo nginx -t`）
- [ ] Nginx 已重新載入
- [ ] Flask 應用已重啟
- [ ] 上傳文件可以正常訪問（`curl` 測試）
- [ ] 圖片上傳功能正常
- [ ] 圖片刪除功能正常

---

## 🆘 如果出現問題

### 回滾步驟

```bash
# 1. 恢復舊目錄
mv public/uploads.backup public/uploads

# 2. 恢復 Nginx 配置
# 編輯 Nginx 配置，改回 alias .../public/uploads

# 3. 重新載入
sudo systemctl reload nginx
sudo systemctl restart quick-foods
```

---

**最後更新：** 2025-11-07  
**維護者：** 快點訂 開發團隊


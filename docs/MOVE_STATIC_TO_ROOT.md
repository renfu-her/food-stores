# 將靜態文件移動到專案根目錄指南

## 🎯 目標

將靜態文件從 `public/static` 移動到專案根目錄的 `static`，簡化 Nginx 配置。

**移動前：**
```
quick-foods/
├── public/
│   └── static/
│       ├── css/
│       └── js/
└── app/
```

**移動後：**
```
quick-foods/
├── static/          ← 新位置
│   ├── css/
│   └── js/
├── public/
└── app/
```

---

## 📋 遷移步驟

### 步驟 1: 執行遷移腳本

```bash
cd /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com

# 執行遷移腳本
python move_static_to_root.py
```

**或手動移動：**
```bash
# 複製文件
cp -r public/static static

# 確認文件
ls -la static/css/
ls -la static/js/
```

### 步驟 2: 更新 Flask 配置

編輯 `app/__init__.py`：

```python
# 修改前
app = Flask(__name__, 
            template_folder='../public/templates',
            static_folder='../public/static')  # ❌ 舊路徑

# 修改後
app = Flask(__name__, 
            template_folder='../public/templates',
            static_folder='static')  # ✅ 新路徑（相對於專案根目錄）
```

**或使用絕對路徑：**
```python
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'public', 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
```

### 步驟 3: 更新 Nginx 配置

編輯 Nginx 配置文件：

```nginx
# 修改前
location /static {
    alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static;  # ❌
    expires 30d;
    add_header Cache-Control "public, immutable";
    try_files $uri =404;
}

# 修改後
location /static {
    alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/static;  # ✅ 簡化了
    expires 30d;
    add_header Cache-Control "public, immutable";
    try_files $uri =404;
}
```

### 步驟 4: 重新載入服務

```bash
# 測試 Nginx 配置
sudo nginx -t

# 重新載入 Nginx
sudo systemctl reload nginx

# 重啟 Flask 應用（如果使用 Systemd）
sudo systemctl restart quick-foods
# 或
sudo systemctl restart gunicorn
```

### 步驟 5: 驗證

```bash
# 檢查文件是否存在
ls -la /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/static/css/style.css

# 測試訪問
curl -I https://quick-foods.ai-tracks.com/static/css/style.css

# 應該返回 200 OK
```

### 步驟 6: 清理舊文件（可選）

**備份後刪除：**
```bash
# 備份舊目錄
mv public/static public/static.backup

# 測試一段時間後，如果沒問題再刪除
# rm -rf public/static.backup
```

---

## 🔧 完整配置更新

### Flask 配置（app/__init__.py）

```python
from flask import Flask
import os

# 獲取專案根目錄
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder=os.path.join(BASE_DIR, 'public', 'templates'),
                static_folder=os.path.join(BASE_DIR, 'static'))  # ✅ 新路徑
    # ... 其他配置
```

### Nginx 配置

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

    # 靜態文件（簡化路徑）
    location /static {
        alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/static;  # ✅
        expires 30d;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
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
2. **更符合慣例** - 許多 Flask 專案將 `static` 放在根目錄
3. **減少錯誤** - 路徑更簡單，不容易出錯
4. **易於維護** - 結構更清晰

---

## ⚠️ 注意事項

1. **備份** - 移動前先備份
2. **測試** - 移動後充分測試
3. **更新配置** - 確保 Flask 和 Nginx 配置都已更新
4. **重啟服務** - 配置更新後必須重啟

---

## 🧪 驗證清單

- [ ] 文件已移動到 `static/` 目錄
- [ ] Flask 配置已更新（`static_folder='static'`）
- [ ] Nginx 配置已更新（`alias .../static`）
- [ ] Nginx 配置測試通過（`sudo nginx -t`）
- [ ] Nginx 已重新載入
- [ ] Flask 應用已重啟
- [ ] 靜態文件可以正常訪問（`curl` 測試）
- [ ] 瀏覽器清除快取後測試通過

---

## 🆘 如果出現問題

### 回滾步驟

```bash
# 1. 恢復舊目錄
mv public/static.backup public/static

# 2. 恢復 Flask 配置
# 編輯 app/__init__.py，改回 static_folder='../public/static'

# 3. 恢復 Nginx 配置
# 編輯 Nginx 配置，改回 alias .../public/static

# 4. 重新載入
sudo systemctl reload nginx
sudo systemctl restart quick-foods
```

---

**最後更新：** 2025-11-07  
**維護者：** Quick Foods 開發團隊


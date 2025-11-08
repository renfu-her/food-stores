# Nginx 配置診斷 - 配置正確但仍 404

## ✅ 您的配置看起來正確！

您的 Nginx 配置中 `/static` location 已經正確設置了 `public/static`：

```nginx
location /static {
    alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static;
    expires 30d;
    add_header Cache-Control "public, immutable";
    try_files $uri =404;
}
```

但錯誤日誌顯示 Nginx 仍在尋找 `/static`（沒有 `public/`），這表示：

---

## 🔍 可能的原因

### 1. Nginx 配置未重新載入（最可能）

**解決方法：**
```bash
# 測試配置
sudo nginx -t

# 重新載入 Nginx
sudo systemctl reload nginx

# 或重啟 Nginx
sudo systemctl restart nginx
```

### 2. 文件不存在

**檢查文件是否存在：**
```bash
# 檢查文件
ls -la /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static/css/style.css
ls -la /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static/css/backend.css
ls -la /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static/js/socketio_client.js

# 檢查目錄
ls -la /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static/
```

**如果文件不存在：**
```bash
# 上傳文件到伺服器
# 或從本地複製
scp -r public/static user@server:/home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/
```

### 3. 文件權限問題

**檢查並設置權限：**
```bash
# 檢查權限
ls -la /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static/

# 設置正確權限
chmod -R 755 /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static
chmod -R 644 /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static/css/*.css
chmod -R 644 /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static/js/*.js

# 如果使用 www-data 用戶
sudo chown -R www-data:www-data /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static
```

### 4. 有其他配置文件覆蓋

**檢查是否有其他配置：**
```bash
# 查看所有相關配置
sudo nginx -T | grep -A 10 "location /static"

# 查看所有站點配置
ls -la /etc/nginx/sites-enabled/
ls -la /etc/nginx/conf.d/

# 檢查是否有默認配置覆蓋
sudo grep -r "location /static" /etc/nginx/
```

### 5. 配置順序問題

**注意：** 您的配置中有一個 `location ~* \.(css|js|...)` 規則在 `/static` 之後，這可能會影響。

**建議調整順序：**
```nginx
# 1. 先處理 /static（最具體）
location /static {
    alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static;
    expires 30d;
    add_header Cache-Control "public, immutable";
    try_files $uri =404;
}

# 2. 然後處理 SocketIO
location /socket.io {
    ...
}

# 3. 最後處理其他靜態文件（通用規則）
location ~* \.(css|js|jpg|jpeg|gif|png|ico|gz|svg|svgz|ttf|otf|woff|woff2|eot|mp4|ogg|ogv|webm|webp|zip|swf)$ {
    expires max;
    add_header Access-Control-Allow-Origin "*";
}

# 4. 最後處理所有其他請求
location / {
    proxy_pass http://127.0.0.1:8093/;
    ...
}
```

---

## 🧪 診斷步驟

### 步驟 1: 確認文件存在

```bash
cd /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com

# 檢查文件
find . -name "style.css" -type f
find . -name "backend.css" -type f
find . -name "socketio_client.js" -type f

# 應該找到：
# ./public/static/css/style.css
# ./public/static/css/backend.css
# ./public/static/js/socketio_client.js
```

### 步驟 2: 測試 Nginx 配置

```bash
# 測試配置語法
sudo nginx -t

# 查看完整配置（確認 /static location）
sudo nginx -T | grep -A 5 "location /static"
```

### 步驟 3: 重新載入 Nginx

```bash
# 重新載入（推薦）
sudo systemctl reload nginx

# 或重啟
sudo systemctl restart nginx

# 檢查狀態
sudo systemctl status nginx
```

### 步驟 4: 測試靜態文件訪問

```bash
# 測試直接訪問文件
curl -I http://localhost/static/css/style.css

# 測試通過域名訪問
curl -I https://quick-foods.ai-tracks.com/static/css/style.css

# 應該返回 200 OK
```

### 步驟 5: 檢查錯誤日誌

```bash
# 實時查看錯誤日誌
sudo tail -f /var/log/nginx/error.log

# 然後在瀏覽器中訪問頁面，觀察日誌
```

---

## 🔧 優化後的完整配置

基於您的配置，這裡是優化版本：

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

    # Let's Encrypt 驗證
    location ~ /.well-known {
        auth_basic off;
        allow all;
    }

    # 靜態文件（最優先，最具體的路徑）
    location /static {
        alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
        access_log off;  # 可選：減少日誌
    }

    # SocketIO（WebSocket）
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

    # 其他靜態文件（通用規則，在 /static 之後）
    location ~* \.(css|js|jpg|jpeg|gif|png|ico|gz|svg|svgz|ttf|otf|woff|woff2|eot|mp4|ogg|ogv|webm|webp|zip|swf)$ {
        expires max;
        add_header Access-Control-Allow-Origin "*";
        # 注意：這個規則不會匹配 /static/ 因為已經被上面的規則處理了
    }

    # Flask 應用（最後處理）
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

## ⚡ 快速修復命令

```bash
# 1. 確認文件存在
ls -la /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static/css/

# 2. 設置權限
chmod -R 755 /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static

# 3. 測試 Nginx 配置
sudo nginx -t

# 4. 重新載入 Nginx
sudo systemctl reload nginx

# 5. 測試訪問
curl -I https://quick-foods.ai-tracks.com/static/css/style.css

# 6. 查看錯誤日誌（如果還有問題）
sudo tail -20 /var/log/nginx/error.log
```

---

## 🆘 如果仍然無法解決

### 方案 A: 讓 Flask 處理靜態文件

如果 Nginx 配置有問題，可以暫時讓 Flask 處理：

```nginx
# 註釋掉或刪除 /static location
# location /static {
#     ...
# }

# 讓 Flask 處理所有請求（包括靜態文件）
location / {
    proxy_pass http://127.0.0.1:8093/;
    ...
}
```

### 方案 B: 使用符號連結

```bash
# 創建符號連結（臨時解決）
sudo ln -sf /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static \
            /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/static
```

---

## 📋 檢查清單

- [ ] 文件存在於 `public/static/` 目錄
- [ ] 文件權限正確（755 目錄，644 文件）
- [ ] Nginx 配置語法正確（`sudo nginx -t`）
- [ ] Nginx 已重新載入（`sudo systemctl reload nginx`）
- [ ] 沒有其他配置覆蓋 `/static` location
- [ ] `curl` 測試返回 200 OK
- [ ] 瀏覽器清除快取後重新載入

---

**最後更新：** 2025-11-07  
**維護者：** 快點訂 開發團隊


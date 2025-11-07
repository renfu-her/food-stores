# Nginx 靜態文件路徑修復 - 快速指南

## 🚨 問題確認

**錯誤路徑：**
```
/home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/static/css/style.css
```

**正確路徑：**
```
/home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static/css/style.css
```

**問題：** Nginx 配置中的 `alias` 缺少 `public/` 前綴

---

## ✅ 立即修復步驟

### 步驟 1: 找到 Nginx 配置文件

```bash
# 方法 1: 查找配置文件
sudo find /etc/nginx -name "*quick-foods*" -o -name "*quick*"

# 方法 2: 查看所有站點配置
ls -la /etc/nginx/sites-available/
ls -la /etc/nginx/conf.d/

# 方法 3: 查看當前使用的配置
sudo nginx -T | grep -B 5 "quick-foods.ai-tracks.com"
```

**常見位置：**
- `/etc/nginx/sites-available/quick-foods`
- `/etc/nginx/sites-available/default`
- `/etc/nginx/conf.d/quick-foods.conf`
- `/etc/nginx/conf.d/default.conf`

### 步驟 2: 編輯配置文件

```bash
# 使用您找到的配置文件路徑
sudo nano /etc/nginx/sites-available/quick-foods
# 或
sudo nano /etc/nginx/conf.d/quick-foods.conf
```

### 步驟 3: 找到並修改 `/static` location

找到類似這樣的配置：

```nginx
location /static {
    alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/static;  # ❌ 錯誤
    expires 30d;
    try_files $uri =404;
}
```

**修改為：**

```nginx
location /static {
    alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static;  # ✅ 正確
    expires 30d;
    add_header Cache-Control "public, immutable";
    try_files $uri =404;
}
```

**關鍵修改：**
- 在路徑中添加 `public/`
- 從：`.../quick-foods.ai-tracks.com/static`
- 改為：`.../quick-foods.ai-tracks.com/public/static`

### 步驟 4: 同樣修改 `/uploads` location（如果有的話）

```nginx
location /uploads {
    alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/uploads;  # ✅ 確保有 public/
    expires 7d;
}
```

### 步驟 5: 測試並重新載入

```bash
# 測試配置語法
sudo nginx -t

# 如果測試通過，重新載入 Nginx
sudo systemctl reload nginx

# 或重啟 Nginx
sudo systemctl restart nginx
```

---

## 🔍 完整配置範例

**完整的 Nginx 配置應該是這樣：**

```nginx
server {
    listen 80;
    server_name quick-foods.ai-tracks.com;
    
    client_max_body_size 16M;
    
    # 靜態文件（修正：添加 public/）
    location /static {
        alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }
    
    # 上傳文件（確保有 public/）
    location /uploads {
        alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/uploads;
        expires 7d;
    }
    
    # SocketIO
    location /socket.io {
        proxy_pass http://127.0.0.1:8093/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
    
    # Flask 應用
    location / {
        proxy_pass http://127.0.0.1:8093;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**注意：** 我看到您的 Flask 運行在 `8093` 端口，確保配置中的 `proxy_pass` 也是 `8093`。

---

## ⚠️ 額外問題：Flask 應用未運行

日誌中還有一個錯誤：
```
connect() failed (111: Connection refused) while connecting to upstream, 
upstream: "http://127.0.0.1:8093/backend/"
```

這表示 Flask 應用沒有在 8093 端口運行。

**檢查 Flask 是否運行：**
```bash
# 檢查端口
netstat -tulpn | grep 8093
# 或
ss -tulpn | grep 8093

# 檢查進程
ps aux | grep gunicorn
ps aux | grep flask
```

**啟動 Flask：**
```bash
cd /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com

# 使用 Gunicorn
gunicorn -c gunicorn_config.py wsgi:application --bind 127.0.0.1:8093

# 或使用 Systemd（如果配置了）
sudo systemctl start quick-foods
sudo systemctl status quick-foods
```

---

## 🧪 驗證修復

### 1. 確認文件存在

```bash
ls -la /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static/css/style.css
ls -la /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static/css/backend.css
ls -la /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static/js/socketio_client.js
```

### 2. 測試靜態文件訪問

```bash
# 測試 Nginx 靜態文件路由
curl -I http://quick-foods.ai-tracks.com/static/css/style.css

# 應該返回：
# HTTP/2 200
# Content-Type: text/css
```

### 3. 清除瀏覽器快取

在瀏覽器中按 `Ctrl+Shift+R` 強制重新載入。

---

## 📋 快速修復命令（一鍵執行）

```bash
# 1. 找到配置文件
CONFIG_FILE=$(sudo find /etc/nginx -type f -name "*quick*" | head -1)
echo "配置文件: $CONFIG_FILE"

# 2. 備份配置
sudo cp "$CONFIG_FILE" "$CONFIG_FILE.backup"

# 3. 顯示當前配置
sudo grep -A 5 "location /static" "$CONFIG_FILE"

# 4. 編輯配置（手動修改，添加 public/）
sudo nano "$CONFIG_FILE"

# 5. 測試配置
sudo nginx -t

# 6. 重新載入
sudo systemctl reload nginx

# 7. 測試訪問
curl -I http://quick-foods.ai-tracks.com/static/css/style.css
```

---

## 🆘 如果仍然無法解決

### 方案 A: 讓 Flask 處理靜態文件（最簡單）

如果不想配置 Nginx，可以刪除 `/static` location，讓 Flask 處理：

```nginx
server {
    listen 80;
    server_name quick-foods.ai-tracks.com;
    
    # 不配置 /static location
    
    # 所有請求轉發給 Flask
    location / {
        proxy_pass http://127.0.0.1:8093;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 方案 B: 使用符號連結（臨時解決）

```bash
# 創建符號連結
sudo ln -s /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static \
          /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/static
```

---

## 📝 檢查清單

修復後確認：

- [ ] Nginx 配置中的 `alias` 路徑包含 `public/`
- [ ] `sudo nginx -t` 測試通過
- [ ] Nginx 已重新載入
- [ ] 靜態文件存在於正確路徑
- [ ] Flask 應用在 8093 端口運行
- [ ] `curl` 測試返回 200 OK
- [ ] 瀏覽器清除快取後重新載入

---

**最後更新：** 2025-11-07  
**維護者：** Quick Foods 開發團隊


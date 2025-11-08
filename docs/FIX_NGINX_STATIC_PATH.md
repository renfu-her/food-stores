# Nginx 配置修復指南 - 靜態文件路徑錯誤

## 🚨 問題診斷

**錯誤日誌顯示：**
```
openat() "/home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/static/css/style.css" 
failed (2: No such file or directory)
```

**問題原因：**
Nginx 配置中的 `alias` 路徑不正確，缺少 `public/` 前綴。

**實際文件路徑：**
```
/home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static/css/style.css
```

---

## ✅ 解決方案

### 方案 1: 修正 Nginx 配置（推薦）

編輯 Nginx 配置文件：

```bash
sudo nano /etc/nginx/sites-available/quick-foods
# 或
sudo nano /etc/nginx/conf.d/quick-foods.conf
```

**修改 `/static` location：**

```nginx
server {
    listen 80;
    server_name quick-foods.ai-tracks.com;
    
    # 修正：添加 public/ 前綴
    location /static {
        alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }
    
    # 其他配置...
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**關鍵修改：**
```nginx
# 錯誤（缺少 public/）
alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/static;

# 正確（包含 public/）
alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static;
```

**重新載入 Nginx：**
```bash
sudo nginx -t  # 測試配置
sudo systemctl reload nginx  # 重新載入
```

---

### 方案 2: 讓 Flask 處理靜態文件（更簡單）

如果不想配置 Nginx，可以讓 Flask 處理所有靜態文件：

**修改 Nginx 配置：**

```nginx
server {
    listen 80;
    server_name quick-foods.ai-tracks.com;
    
    # 不配置 /static location，讓所有請求都轉發給 Flask
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # SocketIO 支援
    location /socket.io {
        proxy_pass http://127.0.0.1:8000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

**這樣做：**
- ✅ 不需要配置靜態文件路徑
- ✅ Flask 會自動處理 `/static/` 請求
- ✅ 配置更簡單

**重新載入：**
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔍 驗證修復

### 步驟 1: 確認文件存在

```bash
# 檢查文件是否存在
ls -la /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static/css/style.css
ls -la /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static/css/backend.css
ls -la /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static/js/socketio_client.js
```

### 步驟 2: 測試訪問

```bash
# 測試 Nginx 靜態文件（如果使用方案 1）
curl -I http://quick-foods.ai-tracks.com/static/css/style.css

# 應該返回 200 OK

# 測試 Flask 靜態文件（如果使用方案 2）
curl -I http://localhost:8000/static/css/style.css
```

### 步驟 3: 清除瀏覽器快取

在瀏覽器中按 `Ctrl+Shift+R` 強制重新載入。

---

## 📋 完整 Nginx 配置範例

### 方案 1: Nginx 處理靜態文件（效能更好）

```nginx
server {
    listen 80;
    server_name quick-foods.ai-tracks.com;
    
    client_max_body_size 16M;
    
    # 靜態文件（修正路徑）
    location /static {
        alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }
    
    # 上傳文件
    location /uploads {
        alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/uploads;
        expires 7d;
    }
    
    # SocketIO
    location /socket.io {
        proxy_pass http://127.0.0.1:8000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
    
    # Flask 應用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 方案 2: Flask 處理靜態文件（配置更簡單）

```nginx
server {
    listen 80;
    server_name quick-foods.ai-tracks.com;
    
    client_max_body_size 16M;
    
    # 不配置 /static，讓 Flask 處理
    
    # SocketIO
    location /socket.io {
        proxy_pass http://127.0.0.1:8000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
    
    # 所有請求轉發給 Flask（包括靜態文件）
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🎯 推薦方案

**如果您的應用訪問量不大：**
- 使用**方案 2**（讓 Flask 處理靜態文件）
- 配置簡單，不需要擔心路徑問題

**如果您的應用訪問量較大：**
- 使用**方案 1**（Nginx 處理靜態文件）
- 效能更好，但需要確保路徑正確

---

## ⚡ 快速修復命令

```bash
# 1. 編輯 Nginx 配置
sudo nano /etc/nginx/sites-available/quick-foods

# 2. 修改 alias 路徑，添加 public/
# 從：alias /home/.../quick-foods.ai-tracks.com/static;
# 改為：alias /home/.../quick-foods.ai-tracks.com/public/static;

# 3. 測試配置
sudo nginx -t

# 4. 重新載入
sudo systemctl reload nginx

# 5. 測試訪問
curl -I http://quick-foods.ai-tracks.com/static/css/style.css
```

---

## 🆘 如果仍然無法解決

1. **確認文件路徑：**
```bash
find /home/ai-tracks-quick-foods -name "style.css"
```

2. **檢查 Nginx 配置：**
```bash
sudo nginx -T | grep -A 10 "location /static"
```

3. **查看詳細錯誤：**
```bash
sudo tail -f /var/log/nginx/error.log
```

---

**最後更新：** 2025-11-07  
**維護者：** 快點訂 開發團隊


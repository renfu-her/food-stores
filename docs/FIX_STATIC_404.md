# 靜態文件 404 錯誤解決方案

## 🚨 問題：靜態文件返回 404 錯誤

**錯誤文件：**
- `style.css` - 404
- `backend.css` - 404
- `socketio_client.js` - 404
- `favicon.ico` - 404

---

## ✅ 解決方案

### 方案 1: 檢查文件是否存在（推薦先執行）

```bash
# 執行檢查腳本
python check_static_files.py

# 或手動檢查
ls -la public/static/css/
ls -la public/static/js/
```

**應該看到：**
```
public/static/css/style.css
public/static/css/backend.css
public/static/js/socketio_client.js
```

---

### 方案 2: 確保文件已上傳

如果文件不存在，請上傳以下文件到正式主機：

```
public/
└── static/
    ├── css/
    │   ├── style.css
    │   └── backend.css
    └── js/
        └── socketio_client.js
```

**上傳命令（使用 SCP）：**
```bash
# 從本地到伺服器
scp -r public/static user@your-server:/path/to/quick-foods/public/
```

---

### 方案 3: 設置正確的文件權限

```bash
# 設置靜態文件權限
chmod -R 755 public/static
chmod -R 644 public/static/css/*.css
chmod -R 644 public/static/js/*.js

# 如果使用 www-data 用戶
sudo chown -R www-data:www-data public/static
```

---

### 方案 4: 配置 Nginx（推薦）

**問題原因：** Nginx 可能沒有正確處理 Flask 的靜態文件路由。

**解決方法：** 在 Nginx 配置中添加靜態文件處理：

```nginx
server {
    listen 80;
    server_name quick-foods.ai-tracks.com;
    
    # 靜態文件直接由 Nginx 處理（提高效能）
    location /static {
        alias /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com/public/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
        
        # 確保文件存在
        try_files $uri =404;
    }
    
    # 其他請求轉發給 Flask
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

**重新載入 Nginx：**
```bash
sudo nginx -t  # 測試配置
sudo systemctl reload nginx  # 重新載入
```

---

### 方案 5: 檢查 Flask 靜態文件配置

確認 `app/__init__.py` 中的配置：

```python
app = Flask(__name__, 
            template_folder='../public/templates',
            static_folder='../public/static')  # 確認這個路徑正確
```

**測試靜態文件路由：**
```bash
# 啟動 Flask
python app.py

# 在瀏覽器訪問
http://localhost:5000/static/css/style.css
http://localhost:5000/static/css/backend.css
http://localhost:5000/static/js/socketio_client.js
```

如果這些 URL 可以訪問，說明 Flask 配置正確，問題在 Nginx。

---

### 方案 6: 創建缺失的文件（臨時解決）

如果文件確實不存在，可以創建空文件作為臨時解決方案：

```bash
# 創建目錄
mkdir -p public/static/css
mkdir -p public/static/js

# 創建空文件（之後需要從本地複製真實內容）
touch public/static/css/style.css
touch public/static/css/backend.css
touch public/static/js/socketio_client.js
```

**然後從本地複製真實文件內容。**

---

## 🔍 診斷步驟

### 步驟 1: 檢查文件

```bash
python check_static_files.py
```

### 步驟 2: 檢查 Nginx 配置

```bash
# 查看當前 Nginx 配置
sudo cat /etc/nginx/sites-available/quick-foods

# 或
sudo cat /etc/nginx/conf.d/quick-foods.conf
```

### 步驟 3: 測試靜態文件訪問

```bash
# 直接訪問文件（繞過 Nginx）
curl http://localhost:5000/static/css/style.css

# 通過 Nginx 訪問
curl http://quick-foods.ai-tracks.com/static/css/style.css
```

### 步驟 4: 查看 Nginx 錯誤日誌

```bash
sudo tail -f /var/log/nginx/error.log
```

---

## 📋 完整檢查清單

- [ ] 文件已上傳到 `public/static/` 目錄
- [ ] 文件權限正確（755 目錄，644 文件）
- [ ] Nginx 配置了 `/static` 路由
- [ ] Nginx 配置已重新載入
- [ ] Flask 應用可以訪問靜態文件
- [ ] 瀏覽器可以訪問靜態文件 URL

---

## 🎯 快速修復命令

```bash
# 1. 檢查文件
python check_static_files.py

# 2. 設置權限
chmod -R 755 public/static

# 3. 測試 Flask 靜態路由
python app.py
# 訪問 http://localhost:5000/static/css/style.css

# 4. 檢查 Nginx 配置
sudo nginx -t
sudo systemctl reload nginx

# 5. 清除瀏覽器快取
# 在瀏覽器中按 Ctrl+Shift+R 強制重新載入
```

---

## 💡 關於 favicon.ico

如果缺少 favicon，可以：

1. **創建一個簡單的 favicon：**
```bash
# 創建 favicon 目錄
mkdir -p public/static

# 從網上下載或創建 favicon.ico
# 或暫時忽略（不影響功能）
```

2. **在模板中添加：**
```html
<link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}">
```

---

## 🆘 仍然無法解決？

1. **提供以下信息：**
   - `python check_static_files.py` 的輸出
   - Nginx 配置文件的內容
   - `ls -la public/static/` 的輸出
   - Nginx 錯誤日誌

2. **檢查文件路徑：**
   - 確認 Flask 的 `static_folder` 路徑
   - 確認 Nginx 的 `alias` 路徑是否一致

---

**最後更新：** 2025-11-07  
**維護者：** 快點訂 開發團隊


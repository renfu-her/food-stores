# Quick Foods 部署指南

## 🚀 正式環境部署步驟

### 1. 環境需求

- Python 3.8+
- MySQL 5.7+ / MariaDB 10.3+
- Nginx / Apache (Web 伺服器)
- Gunicorn / uWSGI (WSGI 伺服器)

### 2. 安裝依賴

```bash
# 安裝 Python 依賴
pip install -r requirements.txt
```

### 3. 環境變數配置

在專案根目錄創建 `.env` 檔案：

```env
# Flask 配置
SECRET_KEY=your-secret-key-here-change-this
DEBUG=False

# 資料庫配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=food-stores

# Session 配置
SESSION_LIFETIME_DAYS=7

# SocketIO 配置
SOCKETIO_ASYNC_MODE=threading
SOCKETIO_CORS_ALLOWED_ORIGINS=*

# 文件上傳配置
MAX_UPLOAD_SIZE_MB=16

# SQLAlchemy 配置
SQLALCHEMY_ECHO=False
```

### 4. 資料庫設置

```bash
# 創建資料庫
mysql -u root -p

CREATE DATABASE `food-stores` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# 執行資料庫遷移
flask db upgrade

# 初始化支付方式
python init_payment_methods.py
```

### 5. 檢查部署狀態

```bash
# 執行部署檢查工具
python check_deployment.py
```

### 6. Gunicorn 配置

創建 `gunicorn_config.py`：

```python
# gunicorn_config.py
bind = "127.0.0.1:8000"
workers = 4
worker_class = "eventlet"  # 支援 SocketIO
timeout = 120
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"
```

啟動命令：

```bash
gunicorn -c gunicorn_config.py wsgi:application
```

### 7. Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 16M;

    # 靜態文件
    location /static {
        alias /path/to/food-stores/public/static;
        expires 30d;
    }

    location /uploads {
        alias /path/to/food-stores/public/uploads;
        expires 7d;
    }

    # 代理到 Gunicorn
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
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 8. Systemd 服務配置

創建 `/etc/systemd/system/quick-foods.service`：

```ini
[Unit]
Description=Quick Foods Web Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/food-stores
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -c gunicorn_config.py wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

啟動服務：

```bash
sudo systemctl daemon-reload
sudo systemctl start quick-foods
sudo systemctl enable quick-foods
sudo systemctl status quick-foods
```

## 🔍 常見 500 錯誤排查

### 1. 資料庫連接失敗

**症狀：** 500 錯誤，日誌顯示 `Can't connect to MySQL server`

**解決方法：**
```bash
# 檢查 MySQL 是否運行
sudo systemctl status mysql

# 檢查資料庫是否存在
mysql -u your_user -p -e "SHOW DATABASES;"

# 檢查資料庫權限
mysql -u your_user -p -e "SHOW GRANTS;"
```

### 2. 缺少資料表

**症狀：** 500 錯誤，日誌顯示 `Table doesn't exist`

**解決方法：**
```bash
# 執行資料庫遷移
flask db upgrade

# 如果遷移失敗，檢查遷移狀態
flask db current
flask db history
```

### 3. 權限問題

**症狀：** 500 錯誤，日誌顯示 `Permission denied`

**解決方法：**
```bash
# 設置正確的目錄權限
sudo chown -R www-data:www-data /path/to/food-stores
sudo chmod -R 755 /path/to/food-stores
sudo chmod -R 775 /path/to/food-stores/public/uploads
sudo chmod -R 775 /path/to/food-stores/logs
```

### 4. 缺少環境變數

**症狀：** 500 錯誤，應用無法啟動

**解決方法：**
```bash
# 檢查 .env 檔案是否存在
ls -la .env

# 檢查環境變數
python check_deployment.py
```

### 5. Python 依賴未安裝

**症狀：** 500 錯誤，日誌顯示 `ModuleNotFoundError`

**解決方法：**
```bash
# 重新安裝依賴
pip install -r requirements.txt

# 檢查依賴
pip list
```

## 📋 部署檢查清單

在正式主機上執行以下命令進行檢查：

```bash
# 1. 檢查 Python 版本
python --version  # 應該是 3.8+

# 2. 檢查虛擬環境（如果使用）
which python
which pip

# 3. 檢查依賴
pip list | grep -E "Flask|SQLAlchemy|PyMySQL"

# 4. 檢查環境變數
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('DB_HOST:', os.getenv('DB_HOST')); print('DB_NAME:', os.getenv('DB_NAME'))"

# 5. 檢查資料庫連接
python check_deployment.py

# 6. 檢查資料庫遷移
flask db current

# 7. 檢查檔案權限
ls -la public/uploads
ls -la logs

# 8. 測試應用啟動
python wsgi.py
# 按 Ctrl+C 停止

# 9. 檢查日誌
tail -f logs/gunicorn_error.log
```

## 🔐 安全建議

### 1. 設置強密碼

```bash
# 生成隨機 SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. 限制資料庫權限

```sql
-- 創建專用資料庫用戶
CREATE USER 'foodstores_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON `food-stores`.* TO 'foodstores_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. 使用 HTTPS

```bash
# 安裝 Certbot（Let's Encrypt）
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 4. 防火牆設置

```bash
# 只開放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

## 📊 監控與日誌

### 查看日誌

```bash
# Gunicorn 日誌
tail -f logs/gunicorn_error.log
tail -f logs/gunicorn_access.log

# Nginx 日誌
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Systemd 日誌
sudo journalctl -u quick-foods -f
```

### 常用管理命令

```bash
# 重啟服務
sudo systemctl restart quick-foods
sudo systemctl restart nginx

# 查看服務狀態
sudo systemctl status quick-foods

# 重新載入 Nginx 配置
sudo nginx -t
sudo systemctl reload nginx
```

## 🆘 獲取幫助

如果您在部署過程中遇到問題：

1. **執行檢查工具：** `python check_deployment.py`
2. **查看錯誤日誌：** 檢查 Gunicorn 和 Nginx 日誌
3. **檢查資料庫：** 確保資料庫連接正常
4. **檢查權限：** 確保檔案和目錄權限正確

---

**最後更新：** 2025-11-07
**維護者：** Quick Foods 開發團隊


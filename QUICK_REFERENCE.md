# 快點訂 快速參考指令卡

## 🚨 遇到 500 錯誤立即執行

```bash
# 1. 快速診斷（首選）
python quick_diagnose.py

# 2. 查看日誌
tail -f logs/gunicorn_error.log

# 3. 查看完整文檔
cat docs/TROUBLESHOOTING_500.md
```

---

## 🔧 診斷工具

| 工具 | 命令 | 用途 |
|------|------|------|
| **快速診斷** | `python quick_diagnose.py` | 快速檢查常見問題 |
| **完整檢查** | `python check_deployment.py` | 詳細部署環境檢查 |
| **應用測試** | `python test_app.py` | 測試應用初始化 |
| **一鍵診斷** | `./diagnose.sh` | Linux/Mac 快速診斷 |

---

## 📦 安裝與初始化

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 配置環境變數
cp env.example .env
nano .env  # 編輯配置

# 3. 創建資料庫
mysql -u root -p
CREATE DATABASE `food-stores` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# 4. 執行遷移
flask db upgrade

# 5. 初始化支付方式
python init_payment_methods.py

# 6. 診斷檢查
python quick_diagnose.py
```

---

## 🚀 啟動應用

### 開發模式

```bash
python app.py
```

### 生產模式（Gunicorn）

```bash
# 前台運行
gunicorn -c gunicorn_config.py wsgi:application

# 後台運行
gunicorn -c gunicorn_config.py wsgi:application -D

# 使用 Systemd
sudo systemctl start quick-foods
sudo systemctl enable quick-foods
```

---

## 🗄️ 資料庫操作

```bash
# 創建遷移
flask db migrate -m "description"

# 執行遷移
flask db upgrade

# 回滾遷移
flask db downgrade

# 查看當前版本
flask db current

# 查看歷史
flask db history
```

---

## 📊 日誌查看

```bash
# Gunicorn 錯誤日誌
tail -f logs/gunicorn_error.log

# Gunicorn 訪問日誌
tail -f logs/gunicorn_access.log

# Nginx 錯誤日誌
sudo tail -f /var/log/nginx/error.log

# Systemd 服務日誌
sudo journalctl -u quick-foods -f
```

---

## 🔄 服務管理

```bash
# 啟動服務
sudo systemctl start quick-foods

# 停止服務
sudo systemctl stop quick-foods

# 重啟服務
sudo systemctl restart quick-foods

# 查看狀態
sudo systemctl status quick-foods

# 查看日誌
sudo journalctl -u quick-foods -n 100
```

---

## 🔐 權限設置

```bash
# 設置目錄擁有者
sudo chown -R www-data:www-data /var/www/quick-foods

# 設置目錄權限
sudo chmod -R 755 /var/www/quick-foods

# 設置上傳目錄權限
sudo chmod -R 775 /var/www/quick-foods/public/uploads

# 設置日誌目錄權限
sudo chmod -R 775 /var/www/quick-foods/logs
```

---

## 🧪 測試與驗證

```bash
# 測試資料庫連接
mysql -u your_user -p -h localhost food-stores

# 測試 Python 導入
python -c "from app import create_app; from app.config import Config; app = create_app(Config); print('✓ OK')"

# 測試 Gunicorn 配置
gunicorn -c gunicorn_config.py wsgi:application --check-config

# 測試 Nginx 配置
sudo nginx -t

# 重新載入 Nginx
sudo systemctl reload nginx
```

---

## ⚠️ 常見問題修復

### 問題：`.env` 文件不存在

```bash
cp env.example .env
nano .env
```

### 問題：資料庫連接失敗

```bash
# 檢查 MySQL
sudo systemctl status mysql
sudo systemctl start mysql

# 測試連接
mysql -u your_user -p -h localhost
```

### 問題：資料表不存在

```bash
flask db upgrade
python init_payment_methods.py
```

### 問題：Python 依賴缺失

```bash
pip install -r requirements.txt
```

### 問題：權限錯誤

```bash
sudo chown -R www-data:www-data /var/www/quick-foods
sudo chmod -R 775 public/uploads logs
```

### 問題：端口被佔用

```bash
# 查看端口使用
sudo netstat -tulpn | grep :8000

# 殺掉進程
sudo kill -9 <PID>
```

---

## 🔑 生成密鑰

```bash
# 生成 SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# 生成隨機密碼
python -c "import secrets; import string; chars = string.ascii_letters + string.digits + string.punctuation; print(''.join(secrets.choice(chars) for _ in range(16)))"
```

---

## 📚 文檔索引

| 文檔 | 路徑 | 說明 |
|------|------|------|
| **快速部署** | `docs/QUICK_START_PRODUCTION.md` | 5 分鐘快速部署 |
| **完整部署** | `docs/DEPLOYMENT_GUIDE.md` | 詳細部署指南 |
| **故障排除** | `docs/TROUBLESHOOTING_500.md` | 500 錯誤排查 |
| **支付設置** | `docs/PAYMENT_METHODS_SETUP.md` | 支付方式配置 |
| **文檔中心** | `docs/README.md` | 所有文檔索引 |
| **主文檔** | `README.md` | 專案說明 |

---

## 🌐 訪問路徑

| 界面 | URL | 說明 |
|------|-----|------|
| **前台商城** | `http://localhost:5000/` | 客戶購物 |
| **店家管理** | `http://localhost:5000/store_admin/dashboard` | 店主管理 |
| **後台管理** | `http://localhost:5000/backend/dashboard` | 系統管理 |
| **訪客點餐** | `http://localhost:5000/guest/shop/{id}/table/{num}` | 掃碼點餐 |

---

## 📞 獲取幫助

1. **執行診斷：** `python quick_diagnose.py`
2. **查看文檔：** `docs/` 目錄
3. **查看日誌：** `tail -f logs/gunicorn_error.log`
4. **GitHub Issues：** 報告問題

---

**最後更新：** 2025-11-07  
**版本：** 1.0  
**維護者：** 快點訂 開發團隊


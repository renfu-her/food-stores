# 正式主機快速安裝指南

## 🚨 遇到 "ModuleNotFoundError: No module named 'dotenv'" 錯誤？

### 立即執行以下命令

```bash
# 1. 進入專案目錄
cd /home/ai-tracks-quick-foods/htdocs/quick-foods.ai-tracks.com

# 2. 安裝 Python 依賴（最重要！）
pip install -r requirements.txt

# 或使用 pip3
pip3 install -r requirements.txt

# 如果使用虛擬環境
source venv/bin/activate  # 啟動虛擬環境
pip install -r requirements.txt
```

### 如果沒有 pip

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip

# CentOS/RHEL
sudo yum install python3-pip
```

---

## 📋 完整安裝步驟

### 第一步：基礎檢查（不需要任何依賴）

```bash
python basic_check.py
# 或
python3 basic_check.py
```

這個工具會檢查：
- ✅ Python 版本
- ✅ 文件結構
- ✅ .env 配置
- ✅ 已安裝的套件

### 第二步：安裝依賴

```bash
pip install -r requirements.txt
```

**需要安裝的套件：**
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-SocketIO
- PyMySQL
- python-dotenv
- bcrypt
- Werkzeug
- Pillow
- qrcode
- gunicorn (生產環境)
- eventlet (支援 SocketIO)

### 第三步：配置環境變數

```bash
# 複製範例配置
cp env.example .env

# 編輯配置
nano .env
# 或
vi .env
```

**必須設定：**
```env
SECRET_KEY=生成一個隨機密鑰
DB_HOST=localhost
DB_USER=您的資料庫用戶名
DB_PASSWORD=您的資料庫密碼
DB_NAME=food-stores
DEBUG=False
```

**生成 SECRET_KEY：**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 第四步：創建資料庫

```bash
# 登入 MySQL
mysql -u root -p

# 創建資料庫
CREATE DATABASE `food-stores` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 創建專用用戶（推薦）
CREATE USER 'quickfoods'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON `food-stores`.* TO 'quickfoods'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 第五步：執行資料庫遷移

```bash
# 執行遷移
flask db upgrade

# 初始化支付方式
python init_payment_methods.py
```

### 第六步：設置權限

```bash
# 創建必要目錄
mkdir -p public/uploads logs

# 設置權限
chmod -R 775 public/uploads
chmod -R 775 logs

# 如果使用 www-data 用戶
sudo chown -R www-data:www-data /path/to/quick-foods
```

### 第七步：完整診斷

```bash
# 現在可以執行完整診斷了
python quick_diagnose.py

# 或完整檢查
python check_deployment.py

# 測試應用
python test_app.py
```

---

## 🚀 啟動應用

### 開發測試

```bash
python app.py
```

### 生產環境（Gunicorn）

```bash
# 前台運行（測試）
gunicorn -c gunicorn_config.py wsgi:application

# 使用 Systemd
sudo systemctl start quick-foods
```

---

## ✅ 檢查清單

安裝完成後，確認：

- [ ] Python 3.8+ 已安裝
- [ ] 所有依賴已安裝 (`pip list`)
- [ ] `.env` 文件已創建並配置
- [ ] MySQL 資料庫已創建
- [ ] 資料庫遷移已執行
- [ ] 目錄權限正確
- [ ] `python basic_check.py` 全部通過
- [ ] `python test_app.py` 測試通過

---

## 🔍 診斷工具使用順序

```bash
# 1. 基礎檢查（無需依賴）
python basic_check.py

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 快速診斷
python quick_diagnose.py

# 4. 完整檢查
python check_deployment.py

# 5. 應用測試
python test_app.py
```

---

## 🆘 常見錯誤

### 1. ModuleNotFoundError: No module named 'xxx'

**解決：**
```bash
pip install -r requirements.txt
```

### 2. Can't connect to MySQL server

**解決：**
```bash
# 檢查 MySQL
sudo systemctl status mysql
sudo systemctl start mysql

# 檢查 .env 配置
cat .env | grep DB_
```

### 3. Permission denied

**解決：**
```bash
chmod -R 775 public/uploads logs
sudo chown -R www-data:www-data /path/to/quick-foods
```

### 4. Table doesn't exist

**解決：**
```bash
flask db upgrade
python init_payment_methods.py
```

---

## 📞 需要幫助？

1. 執行基礎檢查：`python basic_check.py`
2. 查看文檔：`docs/TROUBLESHOOTING_500.md`
3. 提供錯誤日誌和診斷輸出

---

**最後更新：** 2025-11-07  
**維護者：** Quick Foods 開發團隊


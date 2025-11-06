# Quick Foods 正式環境快速部署

## 🚀 快速開始（5 分鐘部署）

### 1. 上傳代碼到伺服器

```bash
# 使用 Git
git clone https://your-repo-url.git /var/www/quick-foods
cd /var/www/quick-foods

# 或使用 SCP/SFTP 上傳代碼
```

### 2. 配置環境變數

```bash
# 複製環境變數範例
cp env.example .env

# 編輯 .env 文件
nano .env
```

**最小配置（必填）：**
```env
SECRET_KEY=請執行下面的命令生成
DB_HOST=localhost
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=food-stores
DEBUG=False
```

**生成 SECRET_KEY：**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. 安裝依賴

```bash
# 建議使用虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt

# 安裝 Gunicorn（生產環境）
pip install gunicorn eventlet
```

### 4. 設置資料庫

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

```bash
# 執行資料庫遷移
flask db upgrade

# 初始化支付方式
python init_payment_methods.py
```

### 5. 快速診斷

```bash
# 方式 1: 快速診斷（推薦）
./diagnose.sh

# 方式 2: Python 診斷
python quick_diagnose.py

# 方式 3: 完整檢查
python check_deployment.py

# 方式 4: 測試應用
python test_app.py
```

### 6. 啟動應用

#### 開發/測試模式

```bash
# 使用 Flask 內建伺服器（僅測試用）
python app.py
```

#### 生產模式（Gunicorn）

```bash
# 前台運行（測試）
gunicorn -c gunicorn_config.py wsgi:application

# 後台運行
gunicorn -c gunicorn_config.py wsgi:application -D

# 使用 Systemd（推薦）
sudo systemctl start quick-foods
sudo systemctl enable quick-foods
```

## ⚡ 遇到 500 錯誤？

### 立即執行診斷

```bash
# 一鍵診斷
python quick_diagnose.py
```

### 常見問題快速修復

#### ❌ `.env` 文件不存在

```bash
cp env.example .env
nano .env  # 填入正確配置
```

#### ❌ 資料庫連接失敗

```bash
# 檢查 MySQL
sudo systemctl status mysql

# 測試連接
mysql -u your_user -p -h localhost food-stores
```

#### ❌ 資料表不存在

```bash
flask db upgrade
python init_payment_methods.py
```

#### ❌ Python 依賴缺失

```bash
pip install -r requirements.txt
```

#### ❌ 權限問題

```bash
sudo chown -R www-data:www-data /var/www/quick-foods
sudo chmod -R 755 /var/www/quick-foods
sudo chmod -R 775 /var/www/quick-foods/public/uploads
sudo chmod -R 775 /var/www/quick-foods/logs
```

### 查看詳細錯誤

```bash
# Gunicorn 錯誤日誌
tail -f logs/gunicorn_error.log

# Nginx 錯誤日誌
sudo tail -f /var/log/nginx/error.log

# Systemd 日誌
sudo journalctl -u quick-foods -f
```

## 📚 完整文檔

- **部署指南：** [docs/DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **故障排除：** [docs/TROUBLESHOOTING_500.md](TROUBLESHOOTING_500.md)
- **支付設置：** [docs/PAYMENT_METHODS_SETUP.md](PAYMENT_METHODS_SETUP.md)

## 🔍 診斷工具說明

### 1. `diagnose.sh` - 一鍵診斷（推薦）

**用途：** 快速檢查系統狀態  
**適用：** Linux/Mac  
**特點：** 彩色輸出，一目了然

```bash
./diagnose.sh
```

**檢查內容：**
- ✅ 系統信息
- ✅ `.env` 配置
- ✅ 目錄結構
- ✅ Python 套件
- ✅ 服務狀態
- ✅ 日誌摘要

### 2. `quick_diagnose.py` - 快速診斷

**用途：** Python 版本的快速診斷  
**適用：** 所有平台  
**特點：** 跨平台，詳細輸出

```bash
python quick_diagnose.py
```

**檢查內容：**
- ✅ `.env` 文件
- ✅ 關鍵目錄
- ✅ Python 依賴
- ✅ 環境變數
- ✅ 資料庫連接
- ✅ 應用初始化

### 3. `check_deployment.py` - 完整檢查

**用途：** 詳細的部署環境檢查  
**適用：** 部署前完整驗證  
**特點：** 最全面的檢查

```bash
python check_deployment.py
```

**檢查內容：**
- ✅ 環境變數詳細檢查
- ✅ 資料庫連接和資料表
- ✅ 所有 Python 依賴
- ✅ 目錄權限詳細檢查
- ✅ 應用完整初始化測試

### 4. `test_app.py` - 應用測試

**用途：** 測試應用是否能正常運行  
**適用：** 開發和部署後測試  
**特點：** 模擬實際運行

```bash
python test_app.py
```

**測試內容：**
- ✅ 模組導入
- ✅ 應用創建
- ✅ 資料庫連接
- ✅ 模型測試
- ✅ 資料表檢查
- ✅ 路由註冊
- ✅ 配置驗證

## 🔐 安全檢查清單

在正式環境中，確保：

- [ ] `DEBUG=False`
- [ ] 使用強 `SECRET_KEY`
- [ ] 資料庫使用專用用戶（非 root）
- [ ] 啟用 HTTPS（使用 Let's Encrypt）
- [ ] 設置防火牆（只開放 80, 443, 22）
- [ ] 定期更新系統和依賴
- [ ] 設置日誌輪替
- [ ] 配置自動備份

## 📊 監控建議

### 應用監控

```bash
# 查看進程
ps aux | grep gunicorn

# 查看端口
netstat -tulpn | grep :8000

# 查看日誌
tail -f logs/gunicorn_error.log
```

### 資源監控

```bash
# CPU 和記憶體
top
htop

# 磁碟空間
df -h

# 磁碟 I/O
iostat
```

### 日誌監控

```bash
# 實時監控錯誤
tail -f logs/gunicorn_error.log | grep ERROR

# 統計錯誤數量
grep ERROR logs/gunicorn_error.log | wc -l

# 最近 100 個錯誤
grep ERROR logs/gunicorn_error.log | tail -100
```

## 🆘 需要幫助？

### 自助診斷流程

1. **執行快速診斷**
   ```bash
   python quick_diagnose.py
   ```

2. **根據提示修復問題**

3. **查看錯誤日誌**
   ```bash
   tail -f logs/gunicorn_error.log
   ```

4. **參考文檔**
   - [TROUBLESHOOTING_500.md](TROUBLESHOOTING_500.md)

### 報告問題時請提供

1. `python quick_diagnose.py` 的完整輸出
2. 最近的錯誤日誌（Gunicorn/Nginx）
3. 伺服器環境信息
4. 重現步驟

## 📞 聯絡資訊

- **文檔：** `docs/` 目錄
- **問題追蹤：** GitHub Issues
- **Email：** support@quickfoods.com

---

**最後更新：** 2025-11-07  
**維護者：** Quick Foods 開發團隊  
**版本：** 1.0


# 500 錯誤排查指南

## 🚨 出現 500 錯誤時的快速診斷步驟

### 第一步：快速診斷

在正式主機上執行快速診斷工具：

```bash
cd /path/to/food-stores
python quick_diagnose.py
```

這個工具會自動檢查：
- ✅ `.env` 配置文件
- ✅ 必要目錄（uploads, logs）
- ✅ Python 依賴套件
- ✅ 環境變數設定
- ✅ 資料庫連接
- ✅ 應用初始化

### 第二步：根據診斷結果修復

#### 問題 1: `.env` 文件不存在

```bash
# 複製範例配置
cp env.example .env

# 編輯 .env 文件
nano .env
# 或
vi .env
```

**必須設定的參數：**
```env
SECRET_KEY=請生成一個隨機密鑰
DB_HOST=您的資料庫主機
DB_USER=資料庫用戶名
DB_PASSWORD=資料庫密碼
DB_NAME=food-stores
```

**生成 SECRET_KEY：**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### 問題 2: 資料庫連接失敗

**可能原因：**

1. **MySQL 服務未啟動**
```bash
# 檢查 MySQL 狀態
sudo systemctl status mysql
# 或
sudo systemctl status mariadb

# 啟動 MySQL
sudo systemctl start mysql
```

2. **資料庫不存在**
```bash
# 登入 MySQL
mysql -u root -p

# 創建資料庫
CREATE DATABASE `food-stores` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 授權用戶
GRANT ALL PRIVILEGES ON `food-stores`.* TO 'your_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

3. **資料庫密碼錯誤**
```bash
# 測試連接
mysql -u your_user -p -h localhost food-stores
```

#### 問題 3: 資料表不存在

```bash
# 執行資料庫遷移
flask db upgrade

# 初始化支付方式
python init_payment_methods.py
```

**如果遷移失敗：**
```bash
# 查看當前遷移狀態
flask db current

# 查看遷移歷史
flask db history

# 如果需要，標記為已遷移
flask db stamp head
```

#### 問題 4: Python 依賴未安裝

```bash
# 安裝所有依賴
pip install -r requirements.txt

# 如果使用 Gunicorn
pip install gunicorn eventlet

# 驗證安裝
pip list | grep -E "Flask|SQLAlchemy|PyMySQL"
```

#### 問題 5: 目錄權限問題

```bash
# 創建必要目錄
mkdir -p public/uploads logs

# 設定權限（根據您的 Web 伺服器用戶）
sudo chown -R www-data:www-data /path/to/food-stores
sudo chmod -R 755 /path/to/food-stores
sudo chmod -R 775 /path/to/food-stores/public/uploads
sudo chmod -R 775 /path/to/food-stores/logs
```

### 第三步：查看詳細日誌

#### 1. Gunicorn 日誌

```bash
# 查看錯誤日誌
tail -f logs/gunicorn_error.log

# 查看訪問日誌
tail -f logs/gunicorn_access.log
```

#### 2. Nginx 日誌

```bash
# Nginx 錯誤日誌
sudo tail -f /var/log/nginx/error.log

# Nginx 訪問日誌
sudo tail -f /var/log/nginx/access.log
```

#### 3. Systemd 日誌

```bash
# 查看服務日誌
sudo journalctl -u quick-foods -f

# 查看最近 100 行
sudo journalctl -u quick-foods -n 100
```

#### 4. Flask 應用日誌

如果設定了應用日誌：
```bash
tail -f logs/app.log
```

## 🔍 常見 500 錯誤類型

### 錯誤 1: `Can't connect to MySQL server`

**原因：** 資料庫連接失敗

**解決：**
1. 檢查 MySQL 是否運行
2. 檢查 `.env` 中的資料庫配置
3. 檢查防火牆設置
4. 檢查資料庫用戶權限

### 錯誤 2: `Table 'food-stores.users' doesn't exist`

**原因：** 資料表不存在

**解決：**
```bash
flask db upgrade
python init_payment_methods.py
```

### 錯誤 3: `ModuleNotFoundError: No module named 'xxx'`

**原因：** Python 依賴未安裝

**解決：**
```bash
pip install -r requirements.txt
```

### 錯誤 4: `Permission denied: '/path/to/uploads'`

**原因：** 檔案權限問題

**解決：**
```bash
sudo chmod -R 775 public/uploads
sudo chown -R www-data:www-data public/uploads
```

### 錯誤 5: `KeyError: 'SECRET_KEY'`

**原因：** 環境變數未設定

**解決：**
1. 確保 `.env` 文件存在
2. 檢查 `.env` 中是否設定了 `SECRET_KEY`
3. 重啟應用

## 📋 完整檢查清單

在正式主機上按順序執行：

```bash
# 1. 進入專案目錄
cd /path/to/food-stores

# 2. 檢查 Python 版本（需要 3.8+）
python --version

# 3. 檢查虛擬環境
which python
which pip

# 4. 檢查 .env 文件
ls -la .env
cat .env  # 檢查配置

# 5. 快速診斷
python quick_diagnose.py

# 6. 完整檢查
python check_deployment.py

# 7. 測試資料庫連接
mysql -u your_user -p -h localhost food-stores

# 8. 檢查資料表
mysql -u your_user -p food-stores -e "SHOW TABLES;"

# 9. 檢查依賴
pip list

# 10. 測試應用啟動
python wsgi.py
# 按 Ctrl+C 停止

# 11. 檢查目錄權限
ls -la public/uploads
ls -la logs

# 12. 如果使用 Gunicorn，測試啟動
gunicorn -c gunicorn_config.py wsgi:application --check-config

# 13. 查看服務狀態
sudo systemctl status quick-foods

# 14. 查看日誌
sudo journalctl -u quick-foods -n 50
```

## 🔧 手動測試應用

創建測試腳本 `test_app.py`：

```python
from app import create_app
from app.config import Config

try:
    print("正在創建應用...")
    app = create_app(Config)
    print("✓ 應用創建成功")
    
    with app.app_context():
        from app import db
        print("✓ 資料庫對象創建成功")
        
        # 測試資料庫連接
        db.session.execute('SELECT 1')
        print("✓ 資料庫連接成功")
        
        # 檢查資料表
        from app.models import User, Shop, Product
        print("✓ 模型導入成功")
        
    print("\n所有測試通過！應用應該可以正常運行。")
    
except Exception as e:
    print(f"\n✗ 錯誤: {e}")
    import traceback
    traceback.print_exc()
```

執行測試：
```bash
python test_app.py
```

## 🆘 仍然無法解決？

1. **收集詳細錯誤信息：**
```bash
# 完整的錯誤日誌
sudo journalctl -u quick-foods -n 500 > error_log.txt

# Gunicorn 日誌
tail -n 200 logs/gunicorn_error.log >> error_log.txt

# Nginx 日誌
sudo tail -n 200 /var/log/nginx/error.log >> error_log.txt

# 診斷結果
python quick_diagnose.py >> error_log.txt
python check_deployment.py >> error_log.txt
```

2. **檢查系統資源：**
```bash
# 磁碟空間
df -h

# 記憶體使用
free -h

# CPU 使用
top -bn1 | head -20
```

3. **重啟所有服務：**
```bash
# 重啟應用
sudo systemctl restart quick-foods

# 重啟 Nginx
sudo systemctl restart nginx

# 重啟 MySQL
sudo systemctl restart mysql
```

## 📞 技術支援

如果您完成了所有步驟仍然遇到問題，請提供：

1. `python quick_diagnose.py` 的輸出
2. `python check_deployment.py` 的輸出
3. 最近的錯誤日誌（Gunicorn/Nginx/Systemd）
4. 伺服器環境信息（OS、Python 版本、MySQL 版本）

---

**最後更新：** 2025-11-07  
**維護者：** 快點訂 開發團隊


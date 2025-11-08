# 快點訂 文檔中心

歡迎使用 快點訂！本目錄包含所有相關的技術文檔和指南。

## 📚 文檔目錄

### 🚀 部署相關

#### [QUICK_START_PRODUCTION.md](QUICK_START_PRODUCTION.md)
**5 分鐘快速部署指南**

適合：首次部署、快速上線

內容：
- ⚡ 最小配置要求
- 📋 快速部署步驟
- 🔧 常見問題快速修復
- 🔍 診斷工具說明

#### [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
**完整部署指南**

適合：正式環境完整部署

內容：
- 📦 環境需求詳細說明
- ⚙️ Gunicorn 配置
- 🌐 Nginx 反向代理設置
- 🔄 Systemd 服務配置
- 🔐 安全建議
- 📊 監控與日誌管理

### 🔧 故障排除

#### [TROUBLESHOOTING_500.md](TROUBLESHOOTING_500.md)
**500 錯誤完整排查指南**

適合：遇到 500 錯誤時

內容：
- 🚨 快速診斷步驟
- 🔍 常見錯誤類型和解決方法
- 📋 完整檢查清單
- 🔧 手動測試方法
- 📞 獲取技術支援

### 💳 功能設置

#### [PAYMENT_METHODS_SETUP.md](PAYMENT_METHODS_SETUP.md)
**支付方式設置指南**

適合：配置支付功能

內容：
- 💰 支付方式管理
- 🏪 店鋪支付設置
- 🔒 現金支付保護
- 📝 初始化腳本使用

## 🛠️ 診斷工具

快點訂 提供了多種診斷工具來幫助您快速定位和解決問題：

### 1. 快速診斷（推薦）

```bash
# Linux/Mac
./diagnose.sh

# Windows/所有平台
python quick_diagnose.py
```

**用途：** 快速檢查系統狀態，適合日常使用

### 2. 完整檢查

```bash
python check_deployment.py
```

**用途：** 詳細的部署環境檢查，適合部署前驗證

### 3. 應用測試

```bash
python test_app.py
```

**用途：** 測試應用是否能正常初始化和運行

## 📖 快速參考

### 部署前檢查清單

- [ ] Python 3.8+ 已安裝
- [ ] MySQL 5.7+ 已安裝並運行
- [ ] 創建了 `.env` 文件並配置正確
- [ ] 安裝了所有 Python 依賴 (`pip install -r requirements.txt`)
- [ ] 創建了資料庫
- [ ] 執行了資料庫遷移 (`flask db upgrade`)
- [ ] 初始化了支付方式 (`python init_payment_methods.py`)
- [ ] 目錄權限設置正確
- [ ] 執行診斷工具確認無誤

### 常用命令

```bash
# 開發模式
python app.py

# 生產模式（Gunicorn）
gunicorn -c gunicorn_config.py wsgi:application

# 資料庫遷移
flask db upgrade

# 診斷問題
python quick_diagnose.py

# 查看日誌
tail -f logs/gunicorn_error.log

# 重啟服務
sudo systemctl restart quick-foods
```

### 環境變數配置

最小必需配置：

```env
SECRET_KEY=your-secret-key
DB_HOST=localhost
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=food-stores
DEBUG=False
```

生成 SECRET_KEY：
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 🚨 遇到問題？

### 500 錯誤

1. 執行快速診斷：
   ```bash
   python quick_diagnose.py
   ```

2. 查看錯誤日誌：
   ```bash
   tail -f logs/gunicorn_error.log
   ```

3. 參考文檔：
   - [TROUBLESHOOTING_500.md](TROUBLESHOOTING_500.md)

### 資料庫問題

```bash
# 檢查 MySQL
sudo systemctl status mysql

# 測試連接
mysql -u your_user -p -h localhost food-stores

# 執行遷移
flask db upgrade
```

### 權限問題

```bash
# 設置正確權限
sudo chown -R www-data:www-data /path/to/quick-foods
sudo chmod -R 755 /path/to/quick-foods
sudo chmod -R 775 /path/to/quick-foods/public/uploads
sudo chmod -R 775 /path/to/quick-foods/logs
```

## 📂 項目結構

```
quick-foods/
├── app/                    # 應用主目錄
│   ├── models.py          # 資料模型
│   ├── routes/            # 路由
│   └── utils/             # 工具函數
├── public/                # 前端資源
│   ├── static/            # 靜態文件
│   ├── templates/         # 模板
│   └── uploads/           # 上傳文件
├── migrations/            # 資料庫遷移
├── logs/                  # 日誌文件
├── docs/                  # 文檔（本目錄）
├── app.py                 # 開發模式啟動
├── wsgi.py                # 生產模式入口
├── gunicorn_config.py     # Gunicorn 配置
├── check_deployment.py    # 部署檢查工具
├── quick_diagnose.py      # 快速診斷工具
├── test_app.py            # 應用測試工具
├── diagnose.sh            # 一鍵診斷腳本
├── env.example            # 環境變數範例
└── requirements.txt       # Python 依賴
```

## 🔐 安全建議

在正式環境中：

1. **永遠不要** 使用 `DEBUG=True`
2. **必須** 使用強隨機的 `SECRET_KEY`
3. **建議** 使用專用資料庫用戶（非 root）
4. **必須** 啟用 HTTPS
5. **建議** 設置防火牆
6. **必須** 定期更新系統和依賴
7. **建議** 配置日誌輪替
8. **必須** 設置定期備份

## 📊 監控建議

### 應用層面

- 使用 Supervisor 或 Systemd 管理進程
- 配置日誌輪替（logrotate）
- 監控磁碟空間
- 監控應用響應時間

### 系統層面

- 監控 CPU 和記憶體使用
- 監控資料庫性能
- 設置告警通知
- 定期備份資料庫

## 🆘 獲取幫助

### 自助資源

1. 查閱相關文檔
2. 執行診斷工具
3. 查看錯誤日誌
4. 參考常見問題

### 報告問題

報告問題時請提供：

1. `python quick_diagnose.py` 的完整輸出
2. 錯誤日誌（Gunicorn/Nginx/Systemd）
3. 伺服器環境信息（OS、Python 版本、MySQL 版本）
4. 問題重現步驟
5. 已嘗試的解決方法

### 聯絡方式

- **GitHub Issues：** [項目 Issues 頁面]
- **Email：** support@quickfoods.com
- **文檔：** 本目錄的其他文件

## 📝 文檔更新

- **最後更新：** 2025-11-07
- **維護者：** 快點訂 開發團隊
- **版本：** 1.0

## 🙏 貢獻

歡迎改進文檔！如果您發現：

- 文檔錯誤或過時
- 可以補充的內容
- 更好的解決方案

請提交 Pull Request 或 Issue。

---

**感謝使用 快點訂！** 🍔🍕🍜


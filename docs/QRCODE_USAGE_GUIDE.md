# QRCode 掃碼點餐使用說明

## 📋 目錄

1. [功能概述](#功能概述)
2. [啟用 QRCode 功能](#啟用-qrcode-功能)
3. [生成和管理 QRCode](#生成和管理-qrcode)
4. [訪客使用流程（無需登入）](#訪客使用流程無需登入)
5. [技術實現細節](#技術實現細節)
6. [API 接口說明](#api-接口說明)
7. [常見問題](#常見問題)

---

## 功能概述

QRCode 掃碼點餐功能允許顧客**無需登入**即可通過掃描桌上的 QRCode 進行點餐。這是一個完整的訪客點餐系統，包含以下特點：

### ✨ 主要特點

- ✅ **無需登入**：顧客掃描 QRCode 即可點餐，無需註冊或登入帳號
- ✅ **自動生成**：創建桌號時自動生成對應的 QRCode 圖片
- ✅ **桌號追蹤**：掃描 QRCode 後自動更新桌號狀態（available → occupied）
- ✅ **完整流程**：包含點餐、購物車、結帳等完整功能
- ✅ **批量管理**：支援批量創建桌號和批量打印 QRCode

### 🎯 使用場景

- 餐廳內用點餐：顧客坐在桌邊掃描 QRCode 點餐
- 快速點餐：無需下載 APP 或註冊帳號
- 桌號管理：店家可以追蹤每桌的使用狀態

---

## 啟用 QRCode 功能

### 步驟 1: 在店鋪設置中啟用

1. 登入後台管理系統
2. 進入「店鋪管理」→「編輯店鋪」
3. 找到「桌號掃碼點餐」選項
4. 勾選「啟用桌號掃碼點餐」
5. 保存設置

**設置位置：**
```
後台管理 → 店鋪管理 → 編輯店鋪 → 桌號掃碼點餐
```

**API 設置：**
```json
PUT /api/shops/:id
{
  "qrcode_enabled": true
}
```

### 步驟 2: 確認店鋪狀態

啟用後，店鋪的 `qrcode_enabled` 欄位會設為 `true`，這是訪客點餐功能的前置條件。

---

## 生成和管理 QRCode

### 創建桌號（自動生成 QRCode）

#### 方法 1: 單個創建

**後台操作：**
1. 進入「店鋪管理」→「桌號管理」
2. 點擊「新增桌號」
3. 輸入桌號（如：A1、B2、01、02）
4. 點擊「創建」
5. 系統自動生成 QRCode 圖片

**API 調用：**
```bash
POST /api/shops/:shop_id/tables
Content-Type: application/json
Authorization: Bearer {token}

{
  "table_number": "A1"
}
```

**回應：**
```json
{
  "message": "桌號創建成功",
  "table": {
    "id": 1,
    "table_number": "A1",
    "status": "available",
    "qrcode_path": "qrcodes/shop_1/table_A1.png",
    "qrcode_url": "/store/1/table/A1"
  }
}
```

#### 方法 2: 批量創建

**後台操作：**
1. 進入「店鋪管理」→「桌號管理」
2. 點擊「批量創建」
3. 設置參數：
   - **數量**：要創建的桌號數量（1-100）
   - **前綴**（可選）：如 A、B、VIP
   - **起始編號**：從哪個數字開始
4. 點擊「批量創建」
5. 系統自動為每個桌號生成 QRCode

**範例：**
- 數量：10，前綴：A，起始編號：1
- 結果：A1, A2, A3, ..., A10（每個都有對應的 QRCode）

**API 調用：**
```bash
POST /api/shops/:shop_id/tables/batch
Content-Type: application/json
Authorization: Bearer {token}

{
  "count": 10,
  "prefix": "A",
  "start_number": 1
}
```

**回應：**
```json
{
  "message": "成功創建 10 個桌號",
  "created": ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10"],
  "skipped": [],
  "total_created": 10
}
```

### 查看 QRCode

**後台查看：**
1. 進入「店鋪管理」→「桌號管理」
2. 在桌號列表中，點擊「查看」按鈕
3. QRCode 圖片會在新視窗中打開

**直接訪問：**
```
GET /api/tables/:table_id/qrcode
```

**文件路徑：**
```
/uploads/qrcodes/shop_{shop_id}/table_{table_number}.png
```

### 打印 QRCode

**批量打印：**
1. 進入「店鋪管理」→「桌號管理」
2. 點擊「打印所有 QRCode」按鈕
3. 系統會生成打印友好頁面
4. 每頁顯示 4 個 QRCode（2x2 網格）
5. 每個 QRCode 顯示：店名 + 桌號 + 掃碼說明

**打印頁面路由：**
```
/store_admin/shops/:shop_id/tables/print
```

### 更新桌號（重新生成 QRCode）

當更新桌號編號時，系統會：
1. 刪除舊的 QRCode 文件
2. 自動生成新的 QRCode 文件

**API 調用：**
```bash
PUT /api/shops/:shop_id/tables/:table_id
Content-Type: application/json
Authorization: Bearer {token}

{
  "table_number": "B1"
}
```

### 刪除桌號（同時刪除 QRCode）

刪除桌號時，系統會自動刪除對應的 QRCode 文件。

**API 調用：**
```bash
DELETE /api/shops/:shop_id/tables/:table_id
Authorization: Bearer {token}
```

---

## 訪客使用流程（無需登入）

### 完整流程圖

```
掃描 QRCode
    ↓
進入點餐頁面（自動識別桌號）
    ↓
瀏覽商品、加入購物車
    ↓
查看購物車
    ↓
結帳（選擇支付方式）
    ↓
提交訂單
    ↓
訂單成功頁面
```

### 步驟 1: 掃描 QRCode

顧客使用手機掃描桌上的 QRCode，會自動跳轉到點餐頁面。

**QRCode 包含的 URL：**
```
https://your-domain.com/guest/shop/{shop_id}/table/{table_number}
```

**範例：**
```
https://quick-foods.ai-tracks.com/guest/shop/1/table/A1
```

### 步驟 2: 自動檢查和狀態更新

當顧客掃描 QRCode 進入頁面時，系統會：

1. **檢查店鋪是否啟用 QRCode 功能**
   - 如果未啟用，顯示錯誤訊息：「此店鋪未啟用桌號掃碼點餐」

2. **檢查桌號是否存在**
   - 如果不存在，顯示錯誤訊息：「桌號不存在」

3. **自動更新桌號狀態**
   - 如果桌號狀態為 `available`，自動改為 `occupied`
   - 方便店家追蹤桌號使用情況

### 步驟 3: 點餐頁面

**路由：**
```
/guest/shop/:shop_id/table/:table_number
```

**頁面功能：**
- ✅ 顯示店鋪名稱和桌號
- ✅ 顯示所有可用商品（按分類）
- ✅ 商品篩選（按分類）
- ✅ 加入購物車（使用 localStorage，無需登入）
- ✅ 查看購物車按鈕

**頁面特點：**
- 不顯示登入/註冊按鈕
- 頁面頂部顯示桌號信息
- 使用 localStorage 儲存購物車數據

### 步驟 4: 購物車頁面

**路由：**
```
/guest/shop/:shop_id/table/:table_number/cart
```

**頁面功能：**
- ✅ 顯示購物車中的所有商品
- ✅ 修改數量、刪除商品
- ✅ 顯示總金額
- ✅ 前往結帳按鈕

**數據儲存：**
- 使用瀏覽器的 localStorage
- 鍵名格式：`guest_cart_{shop_id}_{table_number}`
- 數據結構：
```json
{
  "items": [
    {
      "product_id": 1,
      "name": "商品名稱",
      "quantity": 2,
      "unit_price": 100.00,
      "toppings": []
    }
  ],
  "total": 200.00
}
```

### 步驟 5: 結帳頁面

**路由：**
```
/guest/shop/:shop_id/table/:table_number/checkout
```

**頁面功能：**
- ✅ 顯示訂單摘要
- ✅ 選擇支付方式（店鋪啟用的支付方式）
- ✅ 填寫收件人信息（外送時）
- ✅ 提交訂單

**API 調用：**
```bash
POST /api/orders/guest
Content-Type: application/json

{
  "shop_id": 1,
  "table_number": "A1",
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "toppings": []
    }
  ],
  "payment_method_id": 1,
  "recipient_info": {
    "name": "張三",
    "phone": "0912345678"
  }
}
```

### 步驟 6: 訂單成功頁面

**路由：**
```
/guest/shop/:shop_id/table/:table_number/order-success
```

**頁面功能：**
- ✅ 顯示訂單成功訊息
- ✅ 顯示訂單編號
- ✅ 顯示預計送達時間（外送時）
- ✅ 返回點餐頁面按鈕

---

## 技術實現細節

### QRCode 生成

**使用的庫：**
```python
qrcode==7.4.2
```

**生成函數：**
```python
def generate_table_qrcode(shop_id, table_number):
    """生成桌號 QRCode"""
    # 生成訪客點餐 URL
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    qr_url = f"{base_url}/guest/shop/{shop_id}/table/{table_number}"
    
    # 創建 QRCode
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 保存文件
    qrcode_dir = f"uploads/qrcodes/shop_{shop_id}"
    filename = f"table_{table_number}.png"
    filepath = os.path.join(qrcode_dir, filename)
    img.save(filepath)
    
    # 返回相對路徑
    return f"qrcodes/shop_{shop_id}/{filename}"
```

**文件儲存位置：**
```
public/uploads/qrcodes/shop_{shop_id}/table_{table_number}.png
```

### 數據模型

**Shop 模型：**
```python
qrcode_enabled = db.Column(db.Boolean, default=False, nullable=False)
```

**Table 模型：**
```python
table_number = db.Column(db.String(20), nullable=False)
status = db.Column(db.String(20), default='available')  # available/occupied/cleaning
qrcode_path = db.Column(db.String(255), nullable=True)
```

### 路由結構

**訪客路由（無需登入）：**
- `/guest/shop/:shop_id/table/:table_number` - 點餐頁面
- `/guest/shop/:shop_id/table/:table_number/cart` - 購物車
- `/guest/shop/:shop_id/table/:table_number/checkout` - 結帳
- `/guest/shop/:shop_id/table/:table_number/order-success` - 訂單成功

**後台管理路由（需登入）：**
- `/store_admin/shops/:shop_id/tables` - 桌號管理
- `/store_admin/shops/:shop_id/tables/print` - 打印 QRCode

---

## API 接口說明

### 桌號管理 API

#### 1. 獲取店鋪所有桌號

```bash
GET /api/shops/:shop_id/tables
Authorization: Bearer {token}
```

**回應：**
```json
{
  "tables": [
    {
      "id": 1,
      "table_number": "A1",
      "status": "available",
      "qrcode_path": "qrcodes/shop_1/table_A1.png",
      "qrcode_url": "/store/1/table/A1",
      "created_at": "2025-01-27 14:00:00"
    }
  ],
  "total": 1
}
```

#### 2. 創建單個桌號

```bash
POST /api/shops/:shop_id/tables
Authorization: Bearer {token}
Content-Type: application/json

{
  "table_number": "A1"
}
```

#### 3. 批量創建桌號

```bash
POST /api/shops/:shop_id/tables/batch
Authorization: Bearer {token}
Content-Type: application/json

{
  "count": 10,
  "prefix": "A",
  "start_number": 1
}
```

#### 4. 更新桌號

```bash
PUT /api/shops/:shop_id/tables/:table_id
Authorization: Bearer {token}
Content-Type: application/json

{
  "table_number": "B1",
  "status": "occupied"
}
```

#### 5. 刪除桌號

```bash
DELETE /api/shops/:shop_id/tables/:table_id
Authorization: Bearer {token}
```

#### 6. 獲取 QRCode 圖片（公開訪問）

```bash
GET /api/tables/:table_id/qrcode
```

**回應：** PNG 圖片文件

### 訪客訂單 API

#### 創建訪客訂單

```bash
POST /api/orders/guest
Content-Type: application/json

{
  "shop_id": 1,
  "table_number": "A1",
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "toppings": [
        {
          "topping_id": 1,
          "quantity": 1
        }
      ]
    }
  ],
  "payment_method_id": 1,
  "payment_splits": [],
  "recipient_info": {
    "name": "張三",
    "phone": "0912345678",
    "address": "台北市信義區..."
  }
}
```

**回應：**
```json
{
  "message": "訂單創建成功",
  "order": {
    "id": 123,
    "order_number": "ORD20250127001",
    "table_number": "A1",
    "total_amount": 200.00,
    "status": "pending"
  }
}
```

---

## 常見問題

### Q1: 如何啟用 QRCode 功能？

**A:** 在店鋪設置中勾選「啟用桌號掃碼點餐」選項，或通過 API 設置 `qrcode_enabled: true`。

### Q2: QRCode 圖片儲存在哪裡？

**A:** QRCode 圖片儲存在 `public/uploads/qrcodes/shop_{shop_id}/table_{table_number}.png`。

### Q3: 訪客需要登入嗎？

**A:** **不需要**。訪客掃描 QRCode 後可以直接點餐，無需註冊或登入帳號。

### Q4: 如何批量打印 QRCode？

**A:** 在桌號管理頁面點擊「打印所有 QRCode」按鈕，系統會生成打印友好頁面。

### Q5: 桌號狀態如何更新？

**A:** 當顧客掃描 QRCode 進入點餐頁面時，如果桌號狀態為 `available`，系統會自動更新為 `occupied`。

### Q6: 可以自定義 QRCode 的 URL 嗎？

**A:** QRCode URL 格式固定為：`{BASE_URL}/guest/shop/{shop_id}/table/{table_number}`。可以通過設置 `BASE_URL` 環境變數來配置基礎 URL。

### Q7: 刪除桌號時 QRCode 會一起刪除嗎？

**A:** 會的。刪除桌號時，系統會自動刪除對應的 QRCode 文件。

### Q8: 更新桌號編號時 QRCode 會重新生成嗎？

**A:** 會的。更新桌號編號時，系統會刪除舊的 QRCode 文件，並自動生成新的 QRCode。

### Q9: QRCode 生成失敗怎麼辦？

**A:** 檢查以下項目：
1. `qrcode` 庫是否已安裝：`pip list | grep qrcode`
2. 目錄權限是否正確：`chmod 755 public/uploads/qrcodes`
3. 磁碟空間是否足夠

### Q10: 訪客購物車數據儲存在哪裡？

**A:** 訪客購物車數據儲存在瀏覽器的 localStorage 中，鍵名格式為：`guest_cart_{shop_id}_{table_number}`。

### Q11: 如何設置 BASE_URL？

**A:** 在 `.env` 文件中設置：
```env
BASE_URL=https://your-domain.com
```

或在 `app/config.py` 中設置：
```python
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
```

### Q12: 訪客訂單如何追蹤？

**A:** 訪客訂單會包含桌號信息，店家可以在後台訂單管理中查看，並通過桌號篩選訂單。

---

## 使用範例

### 完整使用流程範例

**1. 店家啟用 QRCode 功能**
```bash
PUT /api/shops/1
{
  "qrcode_enabled": true
}
```

**2. 批量創建 20 個桌號**
```bash
POST /api/shops/1/tables/batch
{
  "count": 20,
  "prefix": "A",
  "start_number": 1
}
```

**3. 打印所有 QRCode**
- 訪問：`/store_admin/shops/1/tables/print`
- 打印頁面，貼在桌上

**4. 顧客掃描 QRCode**
- 掃描後自動跳轉到：`/guest/shop/1/table/A1`
- 開始點餐

**5. 顧客提交訂單**
```bash
POST /api/orders/guest
{
  "shop_id": 1,
  "table_number": "A1",
  "items": [...],
  "payment_method_id": 1
}
```

---

## 注意事項

1. **啟用前準備**
   - 確保店鋪已啟用 QRCode 功能
   - 確保有足夠的磁碟空間儲存 QRCode 圖片

2. **權限設置**
   - QRCode 圖片目錄需要有寫入權限
   - 建議設置：`chmod 755 public/uploads/qrcodes`

3. **BASE_URL 配置**
   - 生產環境必須設置正確的 `BASE_URL`
   - QRCode 中的 URL 必須可以公開訪問

4. **桌號管理**
   - 定期清理未使用的桌號
   - 更新桌號編號時會重新生成 QRCode

5. **訪客數據**
   - 訪客購物車數據儲存在 localStorage，清除瀏覽器數據會丟失
   - 建議在結帳前提醒顧客不要清除瀏覽器數據

---

**最後更新：** 2025-01-27 14:30:00 UTC+8  
**維護者：** 快點訂 開發團隊


# 圖片路徑說明 - public/uploads 保持不變

## 📋 當前配置

### 資料庫存儲格式

API 返回的 `image_path` 格式：
- `/uploads/shops/{filename}`
- `/uploads/products/{filename}`
- `/uploads/banners/{filename}`
- `/uploads/news/{filename}`
- `/uploads/qrcodes/shop_{id}/table_{number}.png`

### Flask 路由

```python
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    upload_folder = os.path.join(app.root_path, '..', 'public', 'uploads')
    return send_from_directory(upload_folder, filename)
```

**說明：**
- URL 路徑：`/uploads/shops/xxx.jpg`
- Flask 從：`public/uploads/shops/xxx.jpg` 提供文件
- 模板中使用：`{{ product.images[0].image_path }}` 或 `/uploads/{{ table.qrcode_path }}`

---

## ✅ 如果保持 public/uploads 不變

### 不需要更新程式碼！

**原因：**
1. ✅ API 返回的路徑格式正確：`/uploads/...`
2. ✅ Flask 路由正確：`/uploads/<path:filename>` → `public/uploads/...`
3. ✅ 模板使用正確：`{{ image_path }}` 或 `/uploads/{{ path }}`
4. ✅ Nginx 配置：`location /uploads` → `alias .../public/uploads`

**當前流程：**
```
瀏覽器請求: /uploads/shops/xxx.jpg
    ↓
Nginx: 轉發給 Flask 或直接提供（如果配置了）
    ↓
Flask: /uploads/<filename> 路由
    ↓
實際文件: public/uploads/shops/xxx.jpg
```

---

## 🔍 檢查清單

### 1. Flask 路由（已正確）

```python
# app/__init__.py
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    upload_folder = os.path.join(app.root_path, '..', 'public', 'uploads')
    return send_from_directory(upload_folder, filename)
```

### 2. API 返回路徑（已正確）

```python
# app/routes/api/shop_images.py
relative_path = f'/uploads/shops/{filename}'  # ✅ 正確

# app/routes/api/product_images.py
relative_path = f'/uploads/products/{filename}'  # ✅ 正確
```

### 3. 模板使用（已正確）

```html
<!-- 使用資料庫中的 image_path -->
<img src="{{ product.images[0].image_path }}" />

<!-- 或直接使用 /uploads/ -->
<img src="/uploads/{{ table.qrcode_path }}" />
```

### 4. Nginx 配置（需要確認）

```nginx
location /uploads {
    alias /home/.../quick-foods.ai-tracks.com/public/uploads;  # ✅ 確保路徑正確
    expires 7d;
}
```

---

## ⚠️ 如果模板中使用 `/public/uploads/`

如果您在模板中寫了 `/public/uploads/`，有兩種處理方式：

### 方式 1: 更新模板（推薦）

將模板中的 `/public/uploads/` 改為 `/uploads/`：

```html
<!-- 錯誤 -->
<img src="/public/uploads/{{ image_path }}" />

<!-- 正確 -->
<img src="/uploads/{{ image_path }}" />
```

### 方式 2: 添加 Flask 路由（不推薦）

如果必須使用 `/public/uploads/`，可以添加路由：

```python
# app/__init__.py
@app.route('/public/uploads/<path:filename>')
def public_uploaded_file(filename):
    upload_folder = os.path.join(app.root_path, '..', 'public', 'uploads')
    return send_from_directory(upload_folder, filename)
```

但這會讓 URL 變長，不推薦。

---

## 📊 路徑對照表

| 用途 | URL 路徑 | 實際文件路徑 | 說明 |
|------|---------|------------|------|
| **店鋪圖片** | `/uploads/shops/xxx.jpg` | `public/uploads/shops/xxx.jpg` | ✅ 正確 |
| **產品圖片** | `/uploads/products/xxx.jpg` | `public/uploads/products/xxx.jpg` | ✅ 正確 |
| **Banner** | `/uploads/banners/xxx.jpg` | `public/uploads/banners/xxx.jpg` | ✅ 正確 |
| **QRCode** | `/uploads/qrcodes/...` | `public/uploads/qrcodes/...` | ✅ 正確 |

---

## 🎯 總結

**如果保持 `public/uploads` 不變：**

✅ **不需要更新程式碼！**

**原因：**
- Flask 路由 `/uploads/<filename>` 已經正確映射到 `public/uploads/`
- API 返回的路徑格式 `/uploads/...` 已經正確
- 模板使用方式已經正確

**只需要確保：**
1. Nginx 配置正確（如果使用 Nginx 處理靜態文件）
2. 文件權限正確
3. Flask 路由正常工作

---

## 🔧 驗證方法

```bash
# 1. 檢查文件是否存在
ls -la public/uploads/shops/
ls -la public/uploads/products/

# 2. 測試 Flask 路由（如果 Flask 運行中）
curl http://localhost:5000/uploads/shops/test.jpg

# 3. 測試 Nginx（如果配置了）
curl http://your-domain.com/uploads/shops/test.jpg

# 4. 檢查資料庫中的路徑格式
# 應該看到：/uploads/shops/xxx.jpg（不是 /public/uploads/...）
```

---

**最後更新：** 2025-11-07  
**維護者：** 快點訂 開發團隊


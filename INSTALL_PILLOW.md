# 圖片處理依賴安裝指南

## 🎯 目的

本系統已實現所有圖片自動轉換為 WebP 格式，以節省空間和提升性能。

## 📦 需要安裝的依賴

```bash
pip install Pillow==10.1.0
```

或者安裝所有依賴：

```bash
pip install -r requirements.txt
```

## ✅ 驗證安裝

運行以下命令檢查是否安裝成功：

```bash
python -c "from PIL import Image; print('✅ Pillow 已正確安裝')"
```

## 🖼️ WebP 功能說明

### 支持的原始格式
- JPG / JPEG
- PNG (包含透明背景)
- GIF
- BMP
- WebP

### 轉換設定

| 圖片類型 | 質量 | 最大尺寸 |
|---------|------|---------|
| 產品圖片 | 85% | 1920x1920 |
| 店鋪圖片 | 85% | 1920x1920 |
| 店鋪 Banner | 90% | 2560x1440 |
| 首頁 Banner | 90% | 2560x1440 |
| 新聞圖片 | 85% | 1920x1920 |

### 功能特性
- ✅ 自動等比例縮放（超過最大尺寸時）
- ✅ RGBA/透明圖片自動轉為 RGB（白色背景）
- ✅ 使用 LANCZOS 高質量重採樣
- ✅ 自動添加 .webp 擴展名

## 📊 效益

- 📦 文件大小減少 **25-35%**（相比 JPEG）
- 📦 文件大小減少 **50-80%**（相比 PNG）
- 🚀 加載速度更快
- 💾 節省伺服器存儲空間
- 🌐 減少帶寬消耗

## 🔧 技術細節

圖片處理邏輯位於：`app/utils/image_processor.py`

核心函數：
```python
def convert_to_webp(file, output_path, quality=85, max_width=1920, max_height=1920)
```

所有圖片上傳 API 都會自動調用此函數進行轉換。

## 🚀 開始使用

安裝依賴後，無需任何配置，所有圖片上傳將自動轉換為 WebP 格式！


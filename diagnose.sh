#!/bin/bash
# Quick Foods 一鍵診斷腳本

echo "=========================================="
echo "Quick Foods 500 錯誤快速診斷"
echo "=========================================="
echo ""

# 顏色定義
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 檢查是否在正確的目錄
if [ ! -f "app.py" ] && [ ! -f "wsgi.py" ]; then
    echo -e "${RED}✗ 錯誤：請在專案根目錄執行此腳本${NC}"
    exit 1
fi

echo -e "${YELLOW}1. 系統信息${NC}"
echo "----------------------------------------"
echo "作業系統: $(uname -s)"
echo "Python 版本: $(python --version 2>&1)"
echo "當前目錄: $(pwd)"
echo ""

echo -e "${YELLOW}2. 檢查 .env 文件${NC}"
echo "----------------------------------------"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env 文件存在${NC}"
    echo "配置項："
    grep -E "^[^#]" .env | grep -E "DB_HOST|DB_NAME|DB_USER|SECRET_KEY" | sed 's/=.*/=***/'
else
    echo -e "${RED}✗ .env 文件不存在${NC}"
    echo "  → 請執行: cp env.example .env"
fi
echo ""

echo -e "${YELLOW}3. 檢查目錄結構${NC}"
echo "----------------------------------------"
for dir in "public/uploads" "logs" "migrations" "app"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $dir"
    else
        echo -e "${RED}✗${NC} $dir (不存在)"
    fi
done
echo ""

echo -e "${YELLOW}4. 檢查關鍵 Python 套件${NC}"
echo "----------------------------------------"
for package in "flask" "flask_sqlalchemy" "pymysql" "flask_migrate"; do
    if python -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $package"
    else
        echo -e "${RED}✗${NC} $package (未安裝)"
    fi
done
echo ""

echo -e "${YELLOW}5. 執行 Python 診斷工具${NC}"
echo "----------------------------------------"
if [ -f "quick_diagnose.py" ]; then
    python quick_diagnose.py
else
    echo -e "${RED}✗ quick_diagnose.py 不存在${NC}"
fi
echo ""

echo -e "${YELLOW}6. 檢查服務狀態${NC}"
echo "----------------------------------------"

# 檢查 MySQL
if command -v systemctl &> /dev/null; then
    if systemctl is-active --quiet mysql || systemctl is-active --quiet mariadb; then
        echo -e "${GREEN}✓${NC} MySQL/MariaDB 正在運行"
    else
        echo -e "${RED}✗${NC} MySQL/MariaDB 未運行"
    fi
    
    # 檢查應用服務
    if systemctl list-units --type=service | grep -q "quick-foods"; then
        if systemctl is-active --quiet quick-foods; then
            echo -e "${GREEN}✓${NC} Quick Foods 服務正在運行"
        else
            echo -e "${RED}✗${NC} Quick Foods 服務未運行"
        fi
    fi
else
    echo "  (無法檢查服務狀態，systemctl 不可用)"
fi
echo ""

echo -e "${YELLOW}7. 檢查日誌文件${NC}"
echo "----------------------------------------"
if [ -d "logs" ]; then
    if [ -f "logs/gunicorn_error.log" ]; then
        echo "最近的 Gunicorn 錯誤（最後 5 行）:"
        tail -n 5 logs/gunicorn_error.log
    else
        echo "  gunicorn_error.log 不存在"
    fi
else
    echo -e "${RED}✗ logs 目錄不存在${NC}"
fi
echo ""

echo "=========================================="
echo "診斷完成"
echo "=========================================="
echo ""
echo "建議的下一步操作："
echo "1. 執行完整檢查: python check_deployment.py"
echo "2. 查看詳細文檔: docs/TROUBLESHOOTING_500.md"
echo "3. 檢查詳細日誌: tail -f logs/gunicorn_error.log"
echo ""


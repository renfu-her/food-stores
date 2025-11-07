# 🚨 Internal Server Error 快速修复指南

## 立即执行的诊断步骤

### 第一步：快速诊断（推荐）

在服务器上执行：

```bash
cd /path/to/food-stores
python quick_diagnose.py
```

这个工具会自动检查：
- ✅ `.env` 配置文件
- ✅ 必要目录（uploads, logs）
- ✅ Python 依赖套件
- ✅ 环境变量设定
- ✅ 数据库连接
- ✅ 应用初始化

### 第二步：查看错误日志

**1. Gunicorn 错误日志（最重要）**

```bash
# 实时查看错误日志
tail -f logs/gunicorn_error.log

# 查看最近 50 行
tail -n 50 logs/gunicorn_error.log

# 搜索错误关键词
grep -i error logs/gunicorn_error.log | tail -20
```

**2. Nginx 错误日志**

```bash
# 实时查看
sudo tail -f /var/log/nginx/error.log

# 查看最近错误
sudo tail -n 50 /var/log/nginx/error.log
```

**3. Systemd 服务日志**

```bash
# 查看服务状态
sudo systemctl status quick-foods

# 查看服务日志
sudo journalctl -u quick-foods -n 100 --no-pager

# 实时监控
sudo journalctl -u quick-foods -f
```

### 第三步：常见问题快速修复

#### 问题 1: `.env` 文件缺失或配置错误

```bash
# 检查 .env 文件是否存在
ls -la .env

# 如果不存在，复制示例文件
cp env.example .env

# 编辑 .env 文件，确保以下配置正确：
# SECRET_KEY=你的密钥
# DB_HOST=数据库主机
# DB_USER=数据库用户名
# DB_PASSWORD=数据库密码
# DB_NAME=food-stores
```

**生成 SECRET_KEY：**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### 问题 2: 数据库连接失败

```bash
# 检查 MySQL 服务状态
sudo systemctl status mysql
# 或
sudo systemctl status mariadb

# 如果未启动，启动服务
sudo systemctl start mysql

# 测试数据库连接
mysql -u your_user -p -h localhost food-stores
```

**如果数据库不存在：**
```bash
mysql -u root -p
CREATE DATABASE `food-stores` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON `food-stores`.* TO 'your_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 问题 3: 数据库表不存在

```bash
# 执行数据库迁移
flask db upgrade

# 初始化支付方式
python init_payment_methods.py
```

#### 问题 4: Python 依赖未安装

```bash
# 安装所有依赖
pip install -r requirements.txt

# 验证关键依赖
pip list | grep -E "Flask|SQLAlchemy|PyMySQL|gunicorn"
```

#### 问题 5: 目录权限问题

```bash
# 创建必要目录
mkdir -p public/uploads logs

# 设置权限（根据实际 Web 服务器用户调整）
sudo chown -R www-data:www-data /path/to/food-stores
sudo chmod -R 755 /path/to/food-stores
sudo chmod -R 775 public/uploads logs
```

#### 问题 6: Gunicorn 服务未运行或配置错误

```bash
# 检查 Gunicorn 进程
ps aux | grep gunicorn

# 测试 Gunicorn 配置
gunicorn -c gunicorn_config.py wsgi:application --check-config

# 手动启动测试（前台运行）
gunicorn -c gunicorn_config.py wsgi:application

# 如果正常，重启服务
sudo systemctl restart quick-foods
```

### 第四步：完整检查

执行完整部署检查：

```bash
python check_deployment.py
```

这个工具会检查：
- ✅ 环境变量
- ✅ Python 依赖
- ✅ 数据库连接
- ✅ 必要目录
- ✅ 文件权限
- ✅ 应用初始化

### 第五步：手动测试应用

创建测试脚本 `test_app.py`：

```python
from app import create_app
from app.config import Config

try:
    print("正在创建应用...")
    app = create_app(Config)
    print("✓ 应用创建成功")
    
    with app.app_context():
        from app import db
        print("✓ 数据库对象创建成功")
        
        # 测试数据库连接
        db.session.execute('SELECT 1')
        print("✓ 数据库连接成功")
        
        # 检查数据表
        from app.models import User, Shop, Product
        print("✓ 模型导入成功")
        
    print("\n所有测试通过！应用应该可以正常运行。")
    
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
```

执行测试：
```bash
python test_app.py
```

## 🔍 根据错误日志定位问题

### 错误类型 1: `Can't connect to MySQL server`

**原因：** 数据库连接失败

**解决：**
1. 检查 MySQL 是否运行：`sudo systemctl status mysql`
2. 检查 `.env` 中的数据库配置
3. 检查防火墙设置
4. 检查数据库用户权限

### 错误类型 2: `Table 'food-stores.users' doesn't exist`

**原因：** 数据表不存在

**解决：**
```bash
flask db upgrade
python init_payment_methods.py
```

### 错误类型 3: `ModuleNotFoundError: No module named 'xxx'`

**原因：** Python 依赖未安装

**解决：**
```bash
pip install -r requirements.txt
```

### 错误类型 4: `Permission denied: '/path/to/uploads'`

**原因：** 文件权限问题

**解决：**
```bash
sudo chmod -R 775 public/uploads
sudo chown -R www-data:www-data public/uploads
```

### 错误类型 5: `KeyError: 'SECRET_KEY'`

**原因：** 环境变量未设定

**解决：**
1. 确保 `.env` 文件存在
2. 检查 `.env` 中是否设定了 `SECRET_KEY`
3. 重启应用

### 错误类型 6: `ImportError` 或 `AttributeError`

**原因：** 代码导入错误或配置问题

**解决：**
1. 查看完整错误堆栈（在日志中）
2. 检查相关模块是否存在
3. 检查 Python 版本（需要 3.8+）

## 📋 完整检查清单

按顺序执行以下命令：

```bash
# 1. 进入项目目录
cd /path/to/food-stores

# 2. 检查 Python 版本（需要 3.8+）
python --version

# 3. 检查虚拟环境
which python
which pip

# 4. 检查 .env 文件
ls -la .env
cat .env  # 检查配置（注意不要暴露密码）

# 5. 快速诊断
python quick_diagnose.py

# 6. 完整检查
python check_deployment.py

# 7. 测试数据库连接
mysql -u your_user -p -h localhost food-stores

# 8. 检查数据表
mysql -u your_user -p food-stores -e "SHOW TABLES;"

# 9. 检查依赖
pip list

# 10. 测试应用启动
python wsgi.py
# 按 Ctrl+C 停止

# 11. 检查目录权限
ls -la public/uploads
ls -la logs

# 12. 测试 Gunicorn 配置
gunicorn -c gunicorn_config.py wsgi:application --check-config

# 13. 查看服务状态
sudo systemctl status quick-foods

# 14. 查看日志
sudo journalctl -u quick-foods -n 50
tail -n 50 logs/gunicorn_error.log
```

## 🔄 重启服务

如果修复了配置问题，需要重启服务：

```bash
# 重启应用服务
sudo systemctl restart quick-foods

# 重启 Nginx（如果需要）
sudo systemctl restart nginx

# 重启 MySQL（如果需要）
sudo systemctl restart mysql

# 检查服务状态
sudo systemctl status quick-foods
sudo systemctl status nginx
```

## 🆘 仍然无法解决？

### 收集详细错误信息

```bash
# 创建错误报告文件
error_report.txt

# 完整的错误日志
sudo journalctl -u quick-foods -n 500 > error_report.txt

# Gunicorn 日志
tail -n 200 logs/gunicorn_error.log >> error_report.txt

# Nginx 日志
sudo tail -n 200 /var/log/nginx/error.log >> error_report.txt

# 诊断结果
python quick_diagnose.py >> error_report.txt
python check_deployment.py >> error_report.txt

# 系统信息
python --version >> error_report.txt
mysql --version >> error_report.txt
```

### 检查系统资源

```bash
# 磁盘空间
df -h

# 内存使用
free -h

# CPU 使用
top -bn1 | head -20
```

## 📞 需要帮助时提供的信息

如果问题仍未解决，请提供：

1. `python quick_diagnose.py` 的完整输出
2. `python check_deployment.py` 的完整输出
3. 最近的错误日志（Gunicorn/Nginx/Systemd）
4. 服务器环境信息（OS、Python 版本、MySQL 版本）
5. `.env` 文件配置（**注意：隐藏敏感信息**）

---

**最后更新：** 2025-01-27 14:30:00 UTC+8  
**维护者：** Quick Foods 开发团队


# uWSGI 分别 Reload 指南

## 📋 概述

当主机上有多个 uWSGI 应用时（如 `blog.uwsgi`、`chat-message.uwsgi`、`quick-foods.uwsgi`、`weather-forecast.uwsgi`），需要能够分别 reload 每个应用而不影响其他应用。

---

## ✅ 前置说明

### touch-reload 是否需要安装？

**不需要！** `touch-reload` 是 uWSGI 的内置功能，无需额外安装。只需要：

1. ✅ 确保已安装 uWSGI（通常系统已安装）
2. ✅ 在配置文件中添加 `touch-reload` 选项
3. ✅ 创建对应的 touch-reload 文件

**检查 uWSGI 是否安装：**
```bash
# 检查 uWSGI 版本
uwsgi --version

# 如果未安装，安装方法：
# Ubuntu/Debian
sudo apt-get install uwsgi

# CentOS/RHEL
sudo yum install uwsgi
```

---

## 🔍 方法 1: 使用 touch-reload 文件（推荐）

### 配置步骤

1. **在 uWSGI 配置文件中添加 touch-reload 选项**

   每个应用的配置文件（如 `/etc/uwsgi/apps-available/quick-foods.ini`）：
   
   ```ini
   [uwsgi]
   # ... 其他配置 ...
   
   # Touch-reload 文件路径（uWSGI 内置功能，无需安装）
   touch-reload = /run/uwsgi/app/quick-foods.uwsgi/touch-reload
   ```

2. **创建 touch-reload 文件**

   ```bash
   # 为每个应用创建 touch-reload 文件
   sudo touch /run/uwsgi/app/quick-foods.uwsgi/touch-reload
   sudo touch /run/uwsgi/app/blog.uwsgi/touch-reload
   sudo touch /run/uwsgi/app/chat-message.uwsgi/touch-reload
   sudo touch /run/uwsgi/app/weather-forecast.uwsgi/touch-reload
   
   # 设置权限（确保 uWSGI 进程可以读取）
   sudo chmod 666 /run/uwsgi/app/*/touch-reload
   ```

3. **重启 uWSGI 应用以加载新配置**

   ```bash
   # 如果使用 systemd
   sudo systemctl restart uwsgi
   
   # 或重启特定应用
   sudo systemctl restart quick-foods
   ```

4. **Reload 特定应用**

   ```bash
   # Reload quick-foods 应用（只需 touch 文件即可）
   sudo touch /run/uwsgi/app/quick-foods.uwsgi/touch-reload
   
   # Reload blog 应用
   sudo touch /run/uwsgi/app/blog.uwsgi/touch-reload
   
   # Reload chat-message 应用
   sudo touch /run/uwsgi/app/chat-message.uwsgi/touch-reload
   
   # Reload weather-forecast 应用
   sudo touch /run/uwsgi/app/weather-forecast.uwsgi/touch-reload
   ```

**工作原理：**
- uWSGI 会监控 `touch-reload` 文件的时间戳
- 当文件被 `touch` 时，时间戳改变
- uWSGI 检测到变化后自动 reload worker 进程
- 无需重启整个应用，实现零停机 reload

---

## 🔍 方法 2: 使用 uWSGI Master FIFO

### 配置步骤

1. **在 uWSGI 配置文件中添加 master-fifo 选项**

   ```ini
   [uwsgi]
   # ... 其他配置 ...
   
   # Master FIFO 路径
   master-fifo = /run/uwsgi/app/quick-foods.uwsgi/master-fifo
   ```

2. **创建 master-fifo 文件**

   ```bash
   # 为每个应用创建 master-fifo
   sudo mkfifo /run/uwsgi/app/quick-foods.uwsgi/master-fifo
   sudo mkfifo /run/uwsgi/app/blog.uwsgi/master-fifo
   sudo mkfifo /run/uwsgi/app/chat-message.uwsgi/master-fifo
   sudo mkfifo /run/uwsgi/app/weather-forecast.uwsgi/master-fifo
   
   # 设置权限
   sudo chmod 666 /run/uwsgi/app/*/master-fifo
   ```

3. **Reload 特定应用**

   ```bash
   # Reload quick-foods 应用
   echo r > /run/uwsgi/app/quick-foods.uwsgi/master-fifo
   
   # Reload blog 应用
   echo r > /run/uwsgi/app/blog.uwsgi/master-fifo
   
   # Reload chat-message 应用
   echo r > /run/uwsgi/app/chat-message.uwsgi/master-fifo
   
   # Reload weather-forecast 应用
   echo r > /run/uwsgi/app/weather-forecast.uwsgi/master-fifo
   ```

---

## 🔍 方法 3: 使用 systemd 服务（如果使用 systemd）

### 配置步骤

1. **为每个应用创建 systemd 服务**

   `/etc/systemd/system/quick-foods.service`:
   ```ini
   [Unit]
   Description=Quick Foods uWSGI Application
   After=network.target
   
   [Service]
   Type=notify
   User=www-data
   Group=www-data
   ExecStart=/usr/bin/uwsgi --ini /etc/uwsgi/apps-available/quick-foods.ini
   ExecReload=/bin/kill -HUP $MAINPID
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

2. **Reload 特定应用**

   ```bash
   # Reload quick-foods 应用
   sudo systemctl reload quick-foods
   
   # Reload blog 应用
   sudo systemctl reload blog
   
   # Reload chat-message 应用
   sudo systemctl reload chat-message
   
   # Reload weather-forecast 应用
   sudo systemctl reload weather-forecast
   ```

---

## 🔍 方法 4: 使用 uWSGI Emperor 模式（推荐用于多应用）

### 配置步骤

1. **创建 Emperor 配置文件**

   `/etc/uwsgi/emperor.ini`:
   ```ini
   [uwsgi]
   emperor = /etc/uwsgi/apps-enabled
   emperor-tyrant = true
   emperor-pidfile = /run/uwsgi/emperor.pid
   logto = /var/log/uwsgi/emperor.log
   ```

2. **为每个应用创建独立配置文件**

   `/etc/uwsgi/apps-available/quick-foods.ini`:
   ```ini
   [uwsgi]
   # 应用特定配置
   socket = /run/uwsgi/app/quick-foods.uwsgi/socket
   chmod-socket = 666
   touch-reload = /run/uwsgi/app/quick-foods.uwsgi/touch-reload
   pidfile = /run/uwsgi/app/quick-foods.uwsgi/pid
   # ... 其他配置 ...
   ```

3. **启用应用**

   ```bash
   # 创建符号链接
   sudo ln -s /etc/uwsgi/apps-available/quick-foods.ini /etc/uwsgi/apps-enabled/
   ```

4. **Reload 特定应用**

   ```bash
   # 使用 touch-reload
   sudo touch /run/uwsgi/app/quick-foods.uwsgi/touch-reload
   
   # 或使用 uwsgi 命令
   sudo uwsgi --reload /run/uwsgi/app/quick-foods.uwsgi/pid
   ```

---

## 🔍 方法 5: 直接使用 PID 文件 Reload

### 步骤

1. **查找应用的 PID 文件**

   ```bash
   # 查看每个应用的 PID 文件位置
   ls -la /run/uwsgi/app/*/pid
   ```

2. **Reload 特定应用**

   ```bash
   # Reload quick-foods（使用 PID 文件）
   sudo uwsgi --reload /run/uwsgi/app/quick-foods.uwsgi/pid
   
   # Reload blog
   sudo uwsgi --reload /run/uwsgi/app/blog.uwsgi/pid
   
   # Reload chat-message
   sudo uwsgi --reload /run/uwsgi/app/chat-message.uwsgi/pid
   
   # Reload weather-forecast
   sudo uwsgi --reload /run/uwsgi/app/weather-forecast.uwsgi/pid
   ```

---

## 🔍 方法 6: 使用信号 Reload

### 步骤

1. **查找应用的 Master PID**

   ```bash
   # 查看每个应用的 PID
   cat /run/uwsgi/app/quick-foods.uwsgi/pid
   cat /run/uwsgi/app/blog.uwsgi/pid
   cat /run/uwsgi/app/chat-message.uwsgi/pid
   cat /run/uwsgi/app/weather-forecast.uwsgi/pid
   ```

2. **发送 HUP 信号 Reload**

   ```bash
   # Reload quick-foods
   sudo kill -HUP $(cat /run/uwsgi/app/quick-foods.uwsgi/pid)
   
   # Reload blog
   sudo kill -HUP $(cat /run/uwsgi/app/blog.uwsgi/pid)
   
   # Reload chat-message
   sudo kill -HUP $(cat /run/uwsgi/app/chat-message.uwsgi/pid)
   
   # Reload weather-forecast
   sudo kill -HUP $(cat /run/uwsgi/app/weather-forecast.uwsgi/pid)
   ```

---

## 📝 便捷脚本

### 创建 Reload 脚本

创建 `/usr/local/bin/uwsgi-reload.sh`:

```bash
#!/bin/bash

# uWSGI 应用 Reload 脚本
# 用法: uwsgi-reload.sh <应用名称>

APP_NAME=$1
UWSGI_DIR="/run/uwsgi/app"

if [ -z "$APP_NAME" ]; then
    echo "用法: $0 <应用名称>"
    echo "可用应用:"
    ls -1 $UWSGI_DIR
    exit 1
fi

APP_PATH="$UWSGI_DIR/$APP_NAME.uwsgi"

if [ ! -d "$APP_PATH" ]; then
    echo "错误: 应用 $APP_NAME 不存在"
    exit 1
fi

# 方法 1: 尝试使用 touch-reload
if [ -f "$APP_PATH/touch-reload" ]; then
    echo "使用 touch-reload 方式 reload $APP_NAME..."
    sudo touch "$APP_PATH/touch-reload"
    echo "✓ $APP_NAME 已 reload"
    exit 0
fi

# 方法 2: 尝试使用 PID 文件
if [ -f "$APP_PATH/pid" ]; then
    PID=$(cat "$APP_PATH/pid")
    if [ -n "$PID" ] && kill -0 $PID 2>/dev/null; then
        echo "使用 PID 文件方式 reload $APP_NAME..."
        sudo kill -HUP $PID
        echo "✓ $APP_NAME 已 reload"
        exit 0
    fi
fi

# 方法 3: 尝试使用 uwsgi 命令
if command -v uwsgi &> /dev/null && [ -f "$APP_PATH/pid" ]; then
    echo "使用 uwsgi 命令 reload $APP_NAME..."
    sudo uwsgi --reload "$APP_PATH/pid"
    echo "✓ $APP_NAME 已 reload"
    exit 0
fi

echo "错误: 无法找到 reload 方法"
exit 1
```

设置权限：

```bash
sudo chmod +x /usr/local/bin/uwsgi-reload.sh
```

使用脚本：

```bash
# Reload quick-foods
sudo uwsgi-reload.sh quick-foods

# Reload blog
sudo uwsgi-reload.sh blog

# Reload chat-message
sudo uwsgi-reload.sh chat-message

# Reload weather-forecast
sudo uwsgi-reload.sh weather-forecast
```

---

## 🔍 检查应用状态

### 查看所有应用状态

```bash
# 查看所有 uWSGI 应用状态
sudo systemctl status uwsgi

# 或查看进程
ps aux | grep uwsgi

# 查看每个应用的 PID
for app in quick-foods blog chat-message weather-forecast; do
    echo "$app: $(cat /run/uwsgi/app/$app.uwsgi/pid 2>/dev/null || echo '未运行')"
done
```

---

## 🎯 推荐方案

### 对于多应用环境，推荐使用：

1. **uWSGI Emperor 模式** + **touch-reload**
   - 统一管理多个应用
   - 简单可靠的 reload 方式
   - 易于维护

2. **systemd 服务**（如果使用 systemd）
   - 系统级管理
   - 自动重启
   - 日志管理

---

## ⚠️ 注意事项

1. **权限问题**
   - 确保 touch-reload 文件有正确的权限
   - 确保 PID 文件可读

2. **应用配置**
   - 每个应用需要独立的配置文件
   - 确保 socket 文件路径不冲突

3. **日志检查**
   - Reload 后检查应用日志确认成功
   - 查看 `/var/log/uwsgi/` 目录下的日志

4. **测试 Reload**
   - 在生产环境使用前先测试
   - 确保 Reload 不会导致服务中断

---

## 📚 相关命令

```bash
# 查看 uWSGI 版本
uwsgi --version

# 查看所有 uWSGI 进程
ps aux | grep uwsgi

# 查看 uWSGI 配置
cat /etc/uwsgi/apps-available/quick-foods.ini

# 查看应用日志
tail -f /var/log/uwsgi/app/quick-foods.log

# 重启所有 uWSGI 应用
sudo systemctl restart uwsgi

# 重启特定应用（如果使用 systemd）
sudo systemctl restart quick-foods
```

---

*最后更新：2025-01-27*


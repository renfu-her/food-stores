# Gunicorn 配置文件
import os
import multiprocessing

# 基礎配置
bind = "127.0.0.1:8000"
backlog = 2048

# Worker 配置
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "eventlet"  # 支援 SocketIO，使用 eventlet
worker_connections = 1000
timeout = 120
keepalive = 5

# 最大請求數後重啟 worker（防止記憶體洩漏）
max_requests = 1000
max_requests_jitter = 50

# 日誌配置
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Daemon 模式（可選）
# daemon = False

# PID 文件
pidfile = "logs/gunicorn.pid"

# 用戶和群組（根據實際情況調整）
# user = "www-data"
# group = "www-data"

# 臨時目錄
# tmp_upload_dir = "/tmp"

# SSL 配置（如果需要）
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# 環境變數
raw_env = [
    "LANG=en_US.UTF-8",
]

# 創建日誌目錄
if not os.path.exists('logs'):
    os.makedirs('logs')

def post_fork(server, worker):
    """Worker 啟動後的回調"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    """Worker 啟動前的回調"""
    pass

def pre_exec(server):
    """重新執行前的回調"""
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    """伺服器準備好後的回調"""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """Worker 收到 INT 或 QUIT 信號"""
    worker.log.info("worker received INT or QUIT signal")

def worker_abort(worker):
    """Worker 收到 SIGABRT 信號"""
    worker.log.info("worker received SIGABRT signal")


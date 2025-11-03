"""
Flask-Migrate配置
"""
from flask_migrate import Migrate
from app import create_app, db
from app.config import Config

app = create_app(Config)
migrate = Migrate(app, db)

if __name__ == '__main__':
    # 可以通过命令行运行迁移命令
    # python -m flask db init
    # python -m flask db migrate -m "Initial migration"
    # python -m flask db upgrade
    pass


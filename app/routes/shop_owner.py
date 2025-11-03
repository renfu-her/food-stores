"""
商店管理者路由
"""
from flask import Blueprint

shop_owner_bp = Blueprint('shop_owner', __name__)

@shop_owner_bp.route('/')
def index():
    """Shop Owner首頁"""
    # TODO: 实现Shop Owner首頁
    pass


"""
WebSocket事件處理
"""
from flask import Blueprint, session
from flask_socketio import emit, join_room, leave_room
from app import socketio
from app.utils.decorators import get_current_user
from app.models import User

websocket_bp = Blueprint('websocket', __name__)

@socketio.on('connect')
def handle_connect():
    """客戶端連接事件"""
    try:
        # 獲取當前使用者（從session）
        user_id = session.get('user_id')
        if not user_id:
            emit('error', {'message': '未認證'})
            return False
        
        user = User.query.get(user_id)
        if not user or not user.is_active:
            emit('error', {'message': '使用者不存在或已被禁用'})
            return False
        
        # 根據使用者角色加入相應的房間
        if user.role == 'admin':
            join_room('/backend')
            emit('connected', {'message': '已連接到管理員頻道', 'user_id': user_id, 'role': user.role})
        
        if user.role == 'shop_owner':
            # 獲取使用者擁有的店鋪
            from app.models import Shop
            shops = Shop.query.filter_by(owner_id=user_id).all()
            for shop in shops:
                join_room(f'/shop/{shop.id}')
            emit('connected', {'message': '已連接到店鋪頻道', 'user_id': user_id, 'role': user.role})
        
        # 所有使用者都加入使用者個人頻道和公開頻道
        join_room(f'/user/{user_id}')
        join_room('/public')
        
        emit('connected', {'message': '連接成功', 'user_id': user_id, 'role': user.role})
        
    except Exception as e:
        emit('error', {'message': f'連接失敗: {str(e)}'})
        return False

@socketio.on('disconnect')
def handle_disconnect():
    """客戶端斷開連接事件"""
    try:
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                if user.role == 'shop_owner':
                    from app.models import Shop
                    shops = Shop.query.filter_by(owner_id=user_id).all()
                    for shop in shops:
                        leave_room(f'/shop/{shop.id}')
                
                leave_room(f'/user/{user_id}')
                leave_room('/public')
                
                if user.role == 'admin':
                    leave_room('/backend')
        
        emit('disconnected', {'message': '已断开连接'})
    except Exception as e:
        pass  # 忽略斷開連接時的錯誤

@socketio.on('join_shop')
def handle_join_shop(data):
    """加入店鋪頻道"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            emit('error', {'message': '未認證'})
            return
        
        shop_id = data.get('shop_id')
        if not shop_id:
            emit('error', {'message': '缺少shop_id參數'})
            return
        
        join_room(f'/shop/{shop_id}')
        emit('joined', {'message': f'已加入店铺 {shop_id} 频道', 'shop_id': shop_id})
    except Exception as e:
        emit('error', {'message': f'加入店鋪頻道失败: {str(e)}'})

@socketio.on('leave_shop')
def handle_leave_shop(data):
    """離開店鋪頻道"""
    try:
        shop_id = data.get('shop_id')
        if shop_id:
            leave_room(f'/shop/{shop_id}')
            emit('left', {'message': f'已离开店铺 {shop_id} 频道', 'shop_id': shop_id})
    except Exception as e:
        emit('error', {'message': f'離開店鋪頻道失败: {str(e)}'})

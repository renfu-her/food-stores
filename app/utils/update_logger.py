"""
系統更新日誌記錄工具
"""
import json
from flask import session, request
from app import db
from app.models import UpdateLog

def log_update(action, table_name, record_id=None, old_data=None, new_data=None, description=None):
    """
    記錄系統更新日誌
    
    Args:
        action: 操作類型 (create, update, delete)
        table_name: 表名
        record_id: 記錄ID
        old_data: 舊數據（字典）
        new_data: 新數據（字典）
        description: 操作描述
    """
    try:
        # 安全获取 session 和 request
        try:
            user_id = session.get('user_id') if session else None
        except:
            user_id = None
        
        try:
            ip_address = request.remote_addr if request else None
        except:
            ip_address = None
        
        # 將數據轉換為JSON字符串
        old_data_json = json.dumps(old_data, ensure_ascii=False) if old_data else None
        new_data_json = json.dumps(new_data, ensure_ascii=False) if new_data else None
        
        # 如果沒有描述，自動生成
        if not description:
            action_map = {
                'create': '新增',
                'update': '更新',
                'delete': '刪除'
            }
            table_map = {
                'user': '使用者',
                'shop': '店鋪',
                'product': '產品',
                'order': '訂單',
                'topping': 'Topping',
                'category': '分類'
            }
            action_text = action_map.get(action, action)
            table_text = table_map.get(table_name, table_name)
            description = f'{action_text}{table_text} #{record_id}' if record_id else f'{action_text}{table_text}'
        
        # 創建日誌記錄
        log = UpdateLog(
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_data=old_data_json,
            new_data=new_data_json,
            description=description,
            ip_address=ip_address
        )
        
        db.session.add(log)
        db.session.commit()
        
        return log
        
    except Exception as e:
        print(f"日誌記錄失敗: {str(e)}")
        db.session.rollback()
        return None

def get_logs(limit=100, table_name=None, action=None, user_id=None):
    """
    獲取更新日誌
    
    Args:
        limit: 返回記錄數量
        table_name: 過濾表名
        action: 過濾操作類型
        user_id: 過濾用戶ID
    """
    query = UpdateLog.query
    
    if table_name:
        query = query.filter_by(table_name=table_name)
    
    if action:
        query = query.filter_by(action=action)
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    return query.order_by(UpdateLog.created_at.desc()).limit(limit).all()

def get_record_history(table_name, record_id):
    """
    獲取特定記錄的歷史
    
    Args:
        table_name: 表名
        record_id: 記錄ID
    """
    return UpdateLog.query.filter_by(
        table_name=table_name,
        record_id=record_id
    ).order_by(UpdateLog.created_at.desc()).all()


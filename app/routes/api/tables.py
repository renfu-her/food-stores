"""
桌号管理 API
"""
from flask import Blueprint, request, jsonify, send_file, current_app
from app.models import Table, Shop
from app.utils.decorators import login_required, role_required, get_current_user
from app import db
import qrcode
from io import BytesIO
import os
from datetime import datetime

tables_api_bp = Blueprint('tables_api', __name__)

@tables_api_bp.route('/shops/<int:shop_id>/tables', methods=['GET'])
@role_required('admin', 'store_admin')
def get_shop_tables(shop_id):
    """获取店铺所有桌号"""
    user = get_current_user()
    
    # 获取店铺
    shop = Shop.query.get_or_404(shop_id)
    
    # 权限检查：store_admin只能管理自己的店铺
    if user.role == 'store_admin' and shop.owner_id != user.id:
        return jsonify({'error': '无权访问此店铺'}), 403
    
    # 获取所有桌号
    tables = Table.query.filter_by(shop_id=shop_id).order_by(Table.table_number).all()
    
    tables_data = []
    for table in tables:
        tables_data.append({
            'id': table.id,
            'table_number': table.table_number,
            'status': table.status,
            'qrcode_path': table.qrcode_path,
            'created_at': table.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'qrcode_url': f'/store/{shop_id}/table/{table.table_number}'
        })
    
    return jsonify({
        'tables': tables_data,
        'total': len(tables_data)
    }), 200

@tables_api_bp.route('/shops/<int:shop_id>/tables', methods=['POST'])
@role_required('admin', 'store_admin')
def create_table(shop_id):
    """创建单个桌号"""
    user = get_current_user()
    data = request.get_json()
    
    # 获取店铺
    shop = Shop.query.get_or_404(shop_id)
    
    # 权限检查
    if user.role == 'store_admin' and shop.owner_id != user.id:
        return jsonify({'error': '无权操作此店铺'}), 403
    
    table_number = data.get('table_number', '').strip()
    if not table_number:
        return jsonify({'error': '桌号不能为空'}), 400
    
    # 检查桌号是否已存在
    existing = Table.query.filter_by(shop_id=shop_id, table_number=table_number).first()
    if existing:
        return jsonify({'error': '桌号已存在'}), 400
    
    # 创建桌号
    table = Table(
        shop_id=shop_id,
        table_number=table_number,
        status='available'
    )
    
    # 生成 QRCode
    qrcode_path = generate_table_qrcode(shop_id, table_number)
    table.qrcode_path = qrcode_path
    
    db.session.add(table)
    db.session.commit()
    
    return jsonify({
        'message': '桌号创建成功',
        'table': {
            'id': table.id,
            'table_number': table.table_number,
            'status': table.status,
            'qrcode_path': table.qrcode_path,
            'qrcode_url': f'/store/{shop_id}/table/{table_number}'
        }
    }), 201

@tables_api_bp.route('/shops/<int:shop_id>/tables/batch', methods=['POST'])
@role_required('admin', 'store_admin')
def batch_create_tables(shop_id):
    """批量创建桌号"""
    user = get_current_user()
    data = request.get_json()
    
    # 获取店铺
    shop = Shop.query.get_or_404(shop_id)
    
    # 权限检查
    if user.role == 'store_admin' and shop.owner_id != user.id:
        return jsonify({'error': '无权操作此店铺'}), 403
    
    count = data.get('count', 0)
    prefix = data.get('prefix', '').strip()  # 前缀，如 A, B
    start_number = data.get('start_number', 1)  # 起始编号
    
    if count <= 0 or count > 100:
        return jsonify({'error': '数量必须在1-100之间'}), 400
    
    created_tables = []
    skipped_tables = []
    
    for i in range(count):
        number = start_number + i
        if prefix:
            table_number = f"{prefix}{number}"
        else:
            table_number = f"{number:02d}"  # 补齐两位数
        
        # 检查是否已存在
        existing = Table.query.filter_by(shop_id=shop_id, table_number=table_number).first()
        if existing:
            skipped_tables.append(table_number)
            continue
        
        # 创建桌号
        table = Table(
            shop_id=shop_id,
            table_number=table_number,
            status='available'
        )
        
        # 生成 QRCode
        qrcode_path = generate_table_qrcode(shop_id, table_number)
        table.qrcode_path = qrcode_path
        
        db.session.add(table)
        created_tables.append(table_number)
    
    db.session.commit()
    
    return jsonify({
        'message': f'成功创建 {len(created_tables)} 个桌号',
        'created': created_tables,
        'skipped': skipped_tables,
        'total_created': len(created_tables)
    }), 201

@tables_api_bp.route('/shops/<int:shop_id>/tables/<int:table_id>', methods=['PUT'])
@role_required('admin', 'store_admin')
def update_table(shop_id, table_id):
    """更新桌号"""
    user = get_current_user()
    data = request.get_json()
    
    # 获取店铺
    shop = Shop.query.get_or_404(shop_id)
    
    # 权限检查
    if user.role == 'store_admin' and shop.owner_id != user.id:
        return jsonify({'error': '无权操作此店铺'}), 403
    
    # 获取桌号
    table = Table.query.filter_by(id=table_id, shop_id=shop_id).first_or_404()
    
    # 更新桌号编号
    if 'table_number' in data:
        new_number = data['table_number'].strip()
        if new_number != table.table_number:
            # 检查新编号是否已存在
            existing = Table.query.filter_by(shop_id=shop_id, table_number=new_number).first()
            if existing:
                return jsonify({'error': '桌号已存在'}), 400
            
            # 删除旧 QRCode 文件
            if table.qrcode_path:
                old_path = os.path.join(current_app.root_path, '..', 'public', 'uploads', table.qrcode_path)
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            table.table_number = new_number
            # 重新生成 QRCode
            table.qrcode_path = generate_table_qrcode(shop_id, new_number)
    
    # 更新状态
    if 'status' in data:
        table.status = data['status']
    
    table.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': '桌号更新成功',
        'table': {
            'id': table.id,
            'table_number': table.table_number,
            'status': table.status,
            'qrcode_path': table.qrcode_path
        }
    }), 200

@tables_api_bp.route('/shops/<int:shop_id>/tables/<int:table_id>', methods=['DELETE'])
@role_required('admin', 'store_admin')
def delete_table(shop_id, table_id):
    """删除桌号"""
    user = get_current_user()
    
    # 获取店铺
    shop = Shop.query.get_or_404(shop_id)
    
    # 权限检查
    if user.role == 'store_admin' and shop.owner_id != user.id:
        return jsonify({'error': '无权操作此店铺'}), 403
    
    # 获取桌号
    table = Table.query.filter_by(id=table_id, shop_id=shop_id).first_or_404()
    
    # 删除 QRCode 文件
    if table.qrcode_path:
        qrcode_file = os.path.join(current_app.root_path, '..', 'public', 'uploads', table.qrcode_path)
        if os.path.exists(qrcode_file):
            os.remove(qrcode_file)
    
    db.session.delete(table)
    db.session.commit()
    
    return jsonify({'message': '桌号删除成功'}), 200

@tables_api_bp.route('/tables/<int:table_id>/qrcode', methods=['GET'])
def get_table_qrcode(table_id):
    """获取桌号 QRCode 图片（公开访问）"""
    table = Table.query.get_or_404(table_id)
    
    if not table.qrcode_path:
        return jsonify({'error': 'QRCode不存在'}), 404
    
    qrcode_file = os.path.join(current_app.root_path, '..', 'public', 'uploads', table.qrcode_path)
    
    if not os.path.exists(qrcode_file):
        return jsonify({'error': 'QRCode文件不存在'}), 404
    
    return send_file(qrcode_file, mimetype='image/png')

def generate_table_qrcode(shop_id, table_number):
    """
    生成桌号 QRCode
    
    Args:
        shop_id: 店铺ID
        table_number: 桌号
    
    Returns:
        QRCode文件相对路径
    """
    # 生成URL
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    qr_url = f"{base_url}/store/{shop_id}/table/{table_number}"
    
    # 创建 QRCode
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 确保目录存在
    qrcode_dir = os.path.join(current_app.root_path, '..', 'public', 'uploads', 'qrcodes', f'shop_{shop_id}')
    os.makedirs(qrcode_dir, exist_ok=True)
    
    # 保存文件
    filename = f"table_{table_number}.png"
    filepath = os.path.join(qrcode_dir, filename)
    img.save(filepath)
    
    # 返回相对路径
    return f"qrcodes/shop_{shop_id}/{filename}"


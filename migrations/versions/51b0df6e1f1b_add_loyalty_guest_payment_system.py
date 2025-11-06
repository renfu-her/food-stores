"""add_loyalty_guest_payment_system

Revision ID: 51b0df6e1f1b
Revises: bf3e210941aa
Create Date: 2025-11-06 10:56:35.191497

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51b0df6e1f1b'
down_revision = 'bf3e210941aa'
branch_labels = None
depends_on = None


def upgrade():
    # 1. 修改现有表 - user
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('points', sa.Integer(), nullable=True, server_default='0'))
    
    # 2. 修改现有表 - shop
    with op.batch_alter_table('shop', schema=None) as batch_op:
        batch_op.add_column(sa.Column('points_rate', sa.Integer(), nullable=True, server_default='30'))
        batch_op.add_column(sa.Column('max_tables', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('qrcode_enabled', sa.Boolean(), nullable=True, server_default='0'))
    
    # 3. 修改现有表 - order
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('table_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('is_guest_order', sa.Boolean(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('points_earned', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('points_used', sa.Integer(), nullable=True, server_default='0'))
    
    # 4. 创建 payment_methods 表
    op.create_table('payment_methods',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('icon', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('display_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # 5. 创建 tables 表
    op.create_table('tables',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('shop_id', sa.Integer(), nullable=False),
        sa.Column('table_number', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='available'),
        sa.Column('qrcode_path', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['shop_id'], ['shop.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 6. 创建 shop_payment_methods 表
    op.create_table('shop_payment_methods',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('shop_id', sa.Integer(), nullable=False),
        sa.Column('payment_method_id', sa.Integer(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['shop_id'], ['shop.id'], ),
        sa.ForeignKeyConstraint(['payment_method_id'], ['payment_methods.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 7. 创建 order_payments 表
    op.create_table('order_payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('payment_method_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='pending'),
        sa.Column('transaction_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
        sa.ForeignKeyConstraint(['payment_method_id'], ['payment_methods.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 8. 创建 point_transactions 表
    op.create_table('point_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('shop_id', sa.Integer(), nullable=True),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('balance', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
        sa.ForeignKeyConstraint(['shop_id'], ['shop.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 9. 插入默认支付方式数据
    op.execute("""
        INSERT INTO payment_methods (name, code, icon, is_active, display_order, created_at) VALUES
        ('LINE Pay', 'line_pay', 'fa-brands fa-line', 1, 1, NOW()),
        ('街口支付', 'jko_pay', 'fa-solid fa-wallet', 1, 2, NOW()),
        ('现金', 'cash', 'fa-solid fa-money-bill-1', 1, 99, NOW())
    """)


def downgrade():
    # 删除新增的表
    op.drop_table('point_transactions')
    op.drop_table('order_payments')
    op.drop_table('shop_payment_methods')
    op.drop_table('tables')
    op.drop_table('payment_methods')
    
    # 删除 order 表的新增字段
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_column('points_used')
        batch_op.drop_column('points_earned')
        batch_op.drop_column('is_guest_order')
        batch_op.drop_column('table_id')
    
    # 删除 shop 表的新增字段
    with op.batch_alter_table('shop', schema=None) as batch_op:
        batch_op.drop_column('qrcode_enabled')
        batch_op.drop_column('max_tables')
        batch_op.drop_column('points_rate')
    
    # 删除 user 表的新增字段
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('points')

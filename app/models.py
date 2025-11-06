"""
資料模型定義
"""
from datetime import datetime
from app import db
from sqlalchemy import Index
from decimal import Decimal

# 關聯表定義
product_topping = db.Table('product_topping',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('topping_id', db.Integer, db.ForeignKey('topping.id'), primary_key=True),
    db.Column('price', db.Numeric(10, 2), nullable=False, default=0)
)

order_item_topping = db.Table('order_item_topping',
    db.Column('order_item_id', db.Integer, db.ForeignKey('order_item.id'), primary_key=True),
    db.Column('topping_id', db.Integer, db.ForeignKey('topping.id'), primary_key=True),
    db.Column('price', db.Numeric(10, 2), nullable=False)
)

class User(db.Model):
    """使用者模型"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)  # 電話
    role = db.Column(db.String(20), nullable=False, default='customer')  # admin, store_admin, customer
    
    # 地址資訊
    county = db.Column(db.String(50), nullable=True)  # 縣市
    district = db.Column(db.String(50), nullable=True)  # 區域
    zipcode = db.Column(db.String(10), nullable=True)  # 郵遞區號
    address = db.Column(db.String(500), nullable=True)  # 詳細地址
    
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    points = db.Column(db.Integer, default=0, nullable=False)  # 回馈金点数
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 關係
    shops = db.relationship('Shop', backref='owner', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True)
    point_transactions = db.relationship('PointTransaction', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.name}>'

class Shop(db.Model):
    """店鋪模型"""
    __tablename__ = 'shop'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    shop_order_id = db.Column(db.String(20), unique=True, nullable=False, index=True)  # 商店訂單ID（用於訂單編號，必填）
    banner_image = db.Column(db.String(500), nullable=True)  # Banner 橫幅圖片
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    max_toppings_per_order = db.Column(db.Integer, default=5, nullable=False)
    points_rate = db.Column(db.Integer, default=30, nullable=False)  # 回馈比例（N元=1点）
    max_tables = db.Column(db.Integer, default=0, nullable=False)  # 最大桌号数量
    qrcode_enabled = db.Column(db.Boolean, default=False, nullable=False)  # 是否启用桌号扫码
    status = db.Column(db.String(20), default='active', nullable=False)  # active, inactive
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)  # 軟刪除時間戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 關係
    products = db.relationship('Product', backref='shop', lazy=True, cascade='all, delete-orphan')
    toppings = db.relationship('Topping', backref='shop', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='shop', lazy=True)
    images = db.relationship('ShopImage', backref='shop', lazy=True, cascade='all, delete-orphan', order_by='ShopImage.display_order')
    tables = db.relationship('Table', backref='shop', lazy=True, cascade='all, delete-orphan')
    shop_payment_methods = db.relationship('ShopPaymentMethod', backref='shop', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Shop {self.name}>'
    
    def get_primary_image(self):
        """獲取主要圖片（第一張）"""
        if self.images:
            return self.images[0].image_path
        return None

class Category(db.Model):
    """產品分類模型"""
    __tablename__ = 'category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 關係
    products = db.relationship('Product', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    """產品模型"""
    __tablename__ = 'product'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    discounted_price = db.Column(db.Numeric(10, 2), nullable=True)
    stock_quantity = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    
    # 飲品選項（可選）
    has_cold_drink = db.Column(db.Boolean, default=False, nullable=False)  # 是否提供冷飲
    cold_drink_price = db.Column(db.Numeric(10, 2), nullable=True)  # 冷飲加價
    has_hot_drink = db.Column(db.Boolean, default=False, nullable=False)  # 是否提供熱飲
    hot_drink_price = db.Column(db.Numeric(10, 2), nullable=True)  # 熱飲加價
    
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)  # 軟刪除時間戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 關係
    toppings = db.relationship('Topping', secondary=product_topping, lazy='subquery',
                               backref=db.backref('products', lazy=True))
    images = db.relationship('ProductImage', backref='product', lazy=True, cascade='all, delete-orphan', order_by='ProductImage.display_order')
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def get_primary_image(self):
        """獲取主要圖片（第一張）"""
        if self.images:
            return self.images[0].image_path
        return None

class Topping(db.Model):
    """配料模型"""
    __tablename__ = 'topping'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False, index=True)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Topping {self.name}>'
    
    def get_display_price(self):
        """获取显示價格，如果为0则返回FREE"""
        if self.price == 0:
            return "FREE"
        return f"${self.price:.2f}"

class Order(db.Model):
    """訂單模型"""
    __tablename__ = 'order'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)  # 訂單編號
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False, index=True)
    table_id = db.Column(db.Integer, db.ForeignKey('tables.id'), nullable=True)  # 桌号ID（访客订单）
    is_guest_order = db.Column(db.Boolean, default=False, nullable=False)  # 是否访客订单
    points_earned = db.Column(db.Integer, default=0, nullable=False)  # 本次赚取回馈金
    points_used = db.Column(db.Integer, default=0, nullable=False)  # 本次使用回馈金
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)  # pending, process, success
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    recipient_name = db.Column(db.String(100), nullable=True)  # 收货人姓名
    recipient_phone = db.Column(db.String(20), nullable=True)  # 收货人电话
    recipient_address = db.Column(db.String(500), nullable=True)  # 收货人地址
    delivery_note = db.Column(db.Text, nullable=True)  # 配送备注
    payment_method = db.Column(db.String(20), default='cod', nullable=False)  # 支付方式: cod(货到付款), online(在线支付)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 關係
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('OrderPayment', backref='order', lazy=True, cascade='all, delete-orphan')
    table = db.relationship('Table', backref='orders', foreign_keys=[table_id])
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

class OrderItem(db.Model):
    """訂單項模型"""
    __tablename__ = 'order_item'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # 飲品選項（如果有選擇）
    drink_type = db.Column(db.String(20), nullable=True)  # 'cold' or 'hot'
    drink_price = db.Column(db.Numeric(10, 2), nullable=True)  # 飲品加價
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 關係
    product = db.relationship('Product', backref='order_items')
    toppings = db.relationship('Topping', secondary=order_item_topping, lazy='subquery',
                               backref=db.backref('order_items', lazy=True))
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'

class ShopImage(db.Model):
    """店鋪圖片模型"""
    __tablename__ = 'shop_image'
    
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    image_path = db.Column(db.String(500), nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_shop_image_shop', 'shop_id'),
        Index('idx_shop_image_order', 'shop_id', 'display_order'),
    )
    
    def __repr__(self):
        return f'<ShopImage shop_id={self.shop_id} order={self.display_order}>'

class ProductImage(db.Model):
    """產品圖片模型"""
    __tablename__ = 'product_image'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    image_path = db.Column(db.String(500), nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_product_image_product', 'product_id'),
        Index('idx_product_image_order', 'product_id', 'display_order'),
    )
    
    def __repr__(self):
        return f'<ProductImage product_id={self.product_id} order={self.display_order}>'

class HomeBanner(db.Model):
    """首頁 Banner 模型"""
    __tablename__ = 'home_banner'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    image_path = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200), nullable=True)  # 標題（顯示在首頁）
    subtitle = db.Column(db.String(300), nullable=True)  # 副標題（顯示在首頁）
    link = db.Column(db.String(500), nullable=True)  # 連結（點擊跳轉）
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_home_banner_active', 'is_active'),
        Index('idx_home_banner_order', 'display_order'),
    )
    
    def __repr__(self):
        return f'<HomeBanner {self.name}>'

class About(db.Model):
    """關於我們模型"""
    __tablename__ = 'about'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)  # 標題
    content = db.Column(db.Text, nullable=False)  # Markdown 內容
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # 是否啟用
    display_order = db.Column(db.Integer, default=0, nullable=False)  # 顯示順序
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_about_active', 'is_active'),
        Index('idx_about_order', 'display_order'),
    )
    
    def __repr__(self):
        return f'<About {self.title}>'

class News(db.Model):
    """最新消息模型"""
    __tablename__ = 'news'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # 標題
    description = db.Column(db.Text, nullable=True)  # 描述/內容
    image_path = db.Column(db.String(500), nullable=True)  # 圖片路徑
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # 是否啟用
    publish_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # 發布日期
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_news_active', 'is_active'),
        Index('idx_news_publish_date', 'publish_date'),
    )
    
    def __repr__(self):
        return f'<News {self.name}>'

class SystemSetting(db.Model):
    """系統設定模型"""
    __tablename__ = 'system_setting'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False, index=True)  # 設定鍵
    setting_value = db.Column(db.Text, nullable=True)  # 設定值
    setting_type = db.Column(db.String(20), default='text', nullable=False)  # 類型: text, number, boolean, json
    description = db.Column(db.String(500), nullable=True)  # 描述
    category = db.Column(db.String(50), default='general', nullable=False)  # 分類: general, order, email, etc
    is_encrypted = db.Column(db.Boolean, default=False, nullable=False)  # 是否加密（如密碼）
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_setting_category', 'category'),
    )
    
    def __repr__(self):
        return f'<SystemSetting {self.setting_key}>'
    
    @staticmethod
    def get(key, default=None):
        """獲取設定值"""
        setting = SystemSetting.query.filter_by(setting_key=key).first()
        if not setting:
            return default
        
        # 根據類型轉換
        if setting.setting_type == 'boolean':
            return setting.setting_value.lower() in ['true', '1', 'yes']
        elif setting.setting_type == 'number':
            try:
                return int(setting.setting_value)
            except (ValueError, TypeError):
                return default
        elif setting.setting_type == 'json':
            try:
                import json
                return json.loads(setting.setting_value)
            except:
                return default
        else:
            return setting.setting_value
    
    @staticmethod
    def set(key, value, setting_type='text', description=None, category='general'):
        """設置設定值"""
        setting = SystemSetting.query.filter_by(setting_key=key).first()
        
        # 轉換值為字符串
        if isinstance(value, bool):
            str_value = 'true' if value else 'false'
            setting_type = 'boolean'
        elif isinstance(value, (dict, list)):
            import json
            str_value = json.dumps(value)
            setting_type = 'json'
        else:
            str_value = str(value)
        
        if setting:
            setting.setting_value = str_value
            setting.setting_type = setting_type
            if description:
                setting.description = description
            setting.category = category
        else:
            setting = SystemSetting(
                setting_key=key,
                setting_value=str_value,
                setting_type=setting_type,
                description=description,
                category=category
            )
            db.session.add(setting)
        
        db.session.commit()
        return setting

class UpdateLog(db.Model):
    """系統更新日誌模型"""
    __tablename__ = 'update_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # 執行操作的用戶
    action = db.Column(db.String(20), nullable=False)  # create, update, delete
    table_name = db.Column(db.String(50), nullable=False)  # 操作的表名
    record_id = db.Column(db.Integer, nullable=True)  # 記錄的ID
    old_data = db.Column(db.Text, nullable=True)  # 舊數據（JSON格式）
    new_data = db.Column(db.Text, nullable=True)  # 新數據（JSON格式）
    description = db.Column(db.Text, nullable=True)  # 操作描述
    ip_address = db.Column(db.String(50), nullable=True)  # IP地址
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 關係
    user = db.relationship('User', backref='update_logs', lazy=True)
    
    # 索引
    __table_args__ = (
        Index('idx_update_log_table_record', 'table_name', 'record_id'),
        Index('idx_update_log_user', 'user_id'),
        Index('idx_update_log_created', 'created_at'),
    )
    
    def __repr__(self):
        return f'<UpdateLog {self.action} {self.table_name} #{self.record_id}>'

class Table(db.Model):
    """桌号管理模型"""
    __tablename__ = 'tables'
    
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    table_number = db.Column(db.String(20), nullable=False)  # 桌号（如：A1, B2, 01, 02）
    status = db.Column(db.String(20), default='available', nullable=False)  # available/occupied/cleaning
    qrcode_path = db.Column(db.String(255), nullable=True)  # QRCode 图片路径
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Table {self.table_number} - Shop {self.shop_id}>'

class PaymentMethod(db.Model):
    """支付方式模型"""
    __tablename__ = 'payment_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # LINE Pay, 街口支付, 现金
    code = db.Column(db.String(20), unique=True, nullable=False)  # line_pay, jko_pay, cash
    icon = db.Column(db.String(100), nullable=True)  # Font Awesome icon class
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 關係
    shop_payment_methods = db.relationship('ShopPaymentMethod', backref='payment_method', lazy=True, cascade='all, delete-orphan')
    order_payments = db.relationship('OrderPayment', backref='payment_method', lazy=True)
    
    def __repr__(self):
        return f'<PaymentMethod {self.name}>'

class ShopPaymentMethod(db.Model):
    """店家启用的支付方式"""
    __tablename__ = 'shop_payment_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'), nullable=False)
    is_enabled = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<ShopPaymentMethod shop={self.shop_id} method={self.payment_method_id}>'

class OrderPayment(db.Model):
    """订单支付记录（支持组合支付）"""
    __tablename__ = 'order_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)  # 此支付方式的金额
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending/completed/failed
    transaction_id = db.Column(db.String(100), nullable=True)  # 第三方交易ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<OrderPayment order={self.order_id} amount={self.amount}>'

class PointTransaction(db.Model):
    """回馈金交易记录"""
    __tablename__ = 'point_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=True)
    type = db.Column(db.String(20), nullable=False)  # earn/use/expire
    points = db.Column(db.Integer, nullable=False)  # 正数=赚取，负数=使用
    balance = db.Column(db.Integer, nullable=False)  # 交易后余额
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<PointTransaction user={self.user_id} points={self.points}>'


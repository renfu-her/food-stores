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
    role = db.Column(db.String(20), nullable=False, default='customer')  # admin, store_admin, customer
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 關係
    shops = db.relationship('Shop', backref='owner', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.name}>'

class Shop(db.Model):
    """店鋪模型"""
    __tablename__ = 'shop'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    max_toppings_per_order = db.Column(db.Integer, default=5, nullable=False)
    status = db.Column(db.String(20), default='active', nullable=False)  # active, inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 關係
    products = db.relationship('Product', backref='shop', lazy=True, cascade='all, delete-orphan')
    toppings = db.relationship('Topping', backref='shop', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='shop', lazy=True)
    
    def __repr__(self):
        return f'<Shop {self.name}>'

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 關係
    toppings = db.relationship('Topping', secondary=product_topping, lazy='subquery',
                               backref=db.backref('products', lazy=True))
    
    def __repr__(self):
        return f'<Product {self.name}>'

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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False, index=True)
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)  # pending, process, success
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 關係
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.id}>'

class OrderItem(db.Model):
    """訂單項模型"""
    __tablename__ = 'order_item'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 關係
    product = db.relationship('Product', backref='order_items')
    toppings = db.relationship('Topping', secondary=order_item_topping, lazy='subquery',
                               backref=db.backref('order_items', lazy=True))
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'


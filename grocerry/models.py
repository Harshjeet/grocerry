from . import db
from flask_login import UserMixin
from datetime import datetime, timezone

# User Table
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), default='customer')  # customer or admin
    carts = db.relationship('Cart', backref='user', lazy=True, cascade="all, delete")
    orders = db.relationship('Order', backref='user', lazy=True, cascade="all, delete")

# Product Table
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    manufacture_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    carts = db.relationship('Cart', backref='product', lazy=True, cascade="all, delete")
    order_items = db.relationship('OrderItem', backref='product', lazy=True, cascade="all, delete")

# Cart Table
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    total_price = db.Column(db.Float, nullable=False)  

    # Constraints for unique cart items per user
    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='unique_cart_item'),
    )

# Order Table
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    total_amount = db.Column(db.Float, nullable=False) 
    status = db.Column(db.String(20), default='Pending')  
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete")

# Order Item Table
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    item_price = db.Column(db.Float, nullable=False)  # Derived field: product.price * quantity

# Category Table (Optional, for managing categories separately)
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    products = db.relationship('Product', backref='category_rel', lazy=True)

# Address Table (For storing user shipping addresses)
class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    is_default = db.Column(db.Boolean, default=False)  # Flag for default shipping address
    user = db.relationship('User', backref='addresses', lazy=True)

# Payment Table (For tracking payments)
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # e.g., Credit Card, PayPal, Stripe
    status = db.Column(db.String(20), default='Completed')  # Pending, Completed, Failed
    order = db.relationship('Order', backref='payment', lazy=True)

from Src import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.orm import backref, relationship
from sqlalchemy import ARRAY
from datetime import date


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    phone = db.Column(db.String(8), nullable=False)
    address = db.Column(db.String(80), nullable=False)
    secretQn = db.Column(db.String(80), nullable=False)
    isAdmin = db.Column(db.Boolean, nullable=False, default=False)
    balance = db.Column(db.Integer(), nullable=False, default=0)
    credit = db.Column(db.Integer(), nullable=False, default=0) 
    carts = db.relationship('Cart', backref='user', lazy=True)
    redeemedvouchers = db.relationship('RedeemedVouchers', backref='user', lazy=True)
    def add_to_cart(self, product, quantity):
        existing_cart = Cart.query.filter_by(user_id=self.id, product_id=product.id).first()
        if existing_cart:
            existing_cart.quantity += quantity
        else:
            new_cart = Cart(user_id=self.id, product_id=product.id, quantity=quantity)
            db.session.add(new_cart)
        db.session.commit()

    def remove_from_cart(self, product):
        existing_cart = Cart.query.filter_by(user_id=self.id, product_id=product.id).first()
        if existing_cart:
            db.session.delete(existing_cart)
            db.session.commit()

    
    def __init__(self, username, email, password, phone, address, secretQn, cart, image_file='default.jpg', isAdmin=False, balance=0,credit=0):
        self.username = username
        self.email = email
        self.image_file = image_file
        self.password = password
        self.phone = phone
        self.address = address
        self.secretQn = secretQn
        self.isAdmin = isAdmin
        self.balance = balance
        self.credit = credit
        self.cart = cart

    def __repr__(self): 
        return f"User('{self.username}','{self.email}','{self.image_file}')"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    country = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    stock = db.Column(db.Integer(), nullable=True, default=0)
    isValid = db.Column(db.Integer, nullable=False, default=1)
    orders = db.relationship('Order', backref='product', lazy=True)
    carts = db.relationship('Cart', backref='product', lazy=True)
    def update_stock(self, quantity):
        self.stock -= quantity
        db.session.commit()
    

    def __init__(self, name, description, category,country, price,image_file, stock,  isValid):
        self.name = name
        self.description = description
        self.category = category
        self.country = country
        self.price = price
        self.image_file = image_file
        self.stock = stock
        self.isValid = isValid
    
class Supplier(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    phone = db.Column(db.String(8), nullable=False)
    company = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(80), nullable=False)
    country = db.Column(db.String(80), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    isValid = db.Column(db.Integer, nullable=False, default=1)
    orders = db.relationship('Order', backref='supplier', lazy=True)
    def __init__(self, name, email,password, phone, company, address,country, image_file, isValid):
        self.name = name
        self.email = email
        self.password = password
        self.phone = phone
        self.company = company
        self.address = address
        self.country = country
        self.image_file = image_file
        self.isValid = isValid

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orderstock = db.Column(db.Integer, nullable=False, default=0)
    date_ordered = db.Column(db.String(60), nullable=False)
    date_decision = db.Column(db.String(60), nullable=False, default='--')
    status = db.Column(db.Integer, nullable=False, default=0)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)
    
    def __init__(self, orderstock, date_ordered, date_decision, status, product_id, supplier_id):
        self.orderstock = orderstock
        self.date_ordered = date_ordered
        self.date_decision = date_decision
        self.status = status
        self.product_id = product_id
        self.supplier_id = supplier_id

class Voucher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    credit = db.Column(db.Integer(), nullable=False)
    value = db.Column(db.Integer(), nullable=False)
    redeem_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    isValid = db.Column(db.Integer, nullable=False, default=1)
    redeemedvouchers = db.relationship('RedeemedVouchers', backref='voucher', lazy=True)
    def __init__(self, name, description, credit, value, redeem_date, expiry_date, image_file, isValid):
        self.name = name
        self.description = description
        self.credit = credit
        self.value = value
        self.redeem_date = redeem_date
        self.expiry_date = expiry_date
        self.image_file = image_file
        self.isValid = isValid

class RedeemedVouchers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer, nullable=False, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    voucher_id = db.Column(db.Integer, db.ForeignKey('voucher.id'), nullable=True)
    def __init__(self, status, user_id, voucher_id):
        self.user_id = user_id
        self.voucher_id = voucher_id
        self.status = status

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Link to User table
    rating = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    issue = db.Column(db.String(255), nullable=True)  # Issue should be string, not Integer
    feedback_date = db.Column(db.Date, nullable=False, default=date.today)
    email = db.Column(db.String(255), nullable=True)  # Store user's email

    user = db.relationship('User', backref='feedbacks')  # Establish relationship with User table

    def __init__(self, user_id=None, email=None, rating=0, description="", issue="", feedback_date=None):
        self.user_id = user_id
        self.rating = rating
        self.description = description
        self.issue = issue
        self.feedback_date = feedback_date if feedback_date else date.today()
        self.email = email


class Donation(db.Model):
    __tablename__ = 'donations'  # Explicit table name for clarity
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key linking to User
    amount = db.Column(db.Float, nullable=False)  # Donation amount
    organization = db.Column(db.String(100), nullable=True)  # Optional organization field
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Timestamp of donation

    # Relationship with User for easy querying
    user = db.relationship('User', backref='donations', lazy=True)

    def __init__(self, user_id, amount, organization=None, date=None):
        self.user_id = user_id
        self.amount = amount
        self.organization = organization
        self.date = date if date else datetime.utcnow()

    def __repr__(self):
        return (f"Donation(id={self.id}, user_id={self.user_id}, amount={self.amount}, "
                f"organization={self.organization}, date={self.date})")


class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    logo = db.Column(db.String(255))  # Store logo file path or URL

    def __repr__(self):
        return f'<Organization {self.name}>'
    
   
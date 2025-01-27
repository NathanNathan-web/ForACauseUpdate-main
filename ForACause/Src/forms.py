from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import SelectMultipleField, StringField,FloatField,RadioField, SelectField, PasswordField, SubmitField, BooleanField,FileField, EmailField, IntegerField,TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from .models import User, Product
from wtforms.fields import DateField
import pycountry


def country():
    country_list = []
    for country in pycountry.countries:
        choice = f'{country.name}', f'{country.name}'
        country_list.append(choice)
    return country_list

    

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Length(min=2, max=200)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=8,max=8)])
    address = StringField('Address', validators=[DataRequired()])
    secretQn = StringField("Secret Question (What is your favourite pet's name)", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_phone(self, phone):
        if len(phone.data) == 8 and (phone.data).isdigit() == True and phone.data[0] == '8' or '9' or '6':
            print('Success')
        else:
            raise ValidationError('Invalid phone number. Phone number needs to start with 8, 9 ,6')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class SupplierForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=20)])
    email = EmailField('Email', validators=[DataRequired(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=8,max=8)])
    company = StringField('Company', validators=[DataRequired(), Length(max=80)])
    address = StringField('Company Address', validators=[DataRequired(), Length(max=80)])
    country = SelectField('Country', choices=country(), validators=[DataRequired()])
    image_file = FileField('Logo', validators=[DataRequired(),FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    isValid = RadioField('Validity', coerce=int, choices=[(1, 'Available'), (0, 'Not Available')], default=1)
    submit = SubmitField('Add Supplier')
    def validate_phone(self, phone):
        if len(phone.data) == 8 and (phone.data).isdigit() == True and phone.data[0] == '8' or '9' or '6':
            print('Success')
        else:
            raise ValidationError('Invalid phone number. Phone number needs to start with 8, 9 ,6')

class VoucherForm(FlaskForm):
    name = StringField('Voucher Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    value = IntegerField('Voucher Value', validators=[DataRequired()])
    credits = IntegerField('Credits', validators=[DataRequired()])
    redeem_date = DateField('Redemption Date',format='%Y-%m-%d')
    expiry_date = DateField('Expiry Date',format='%Y-%m-%d')
    image_file = FileField('Logo', validators=[DataRequired(),FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    stock = IntegerField('Stock Quantity', validators=[DataRequired()])
    isValid = RadioField('Validity', coerce=bool, choices=[(True, 'Available'),(False, 'Not Available')], default=True)
    submit = SubmitField('Add Voucher')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=1000)])
    category = SelectField(
        'Category',
        choices=[
            ('Cakes and Pastries', 'Cakes and Pastries'),
            ('Bread and Rolls', 'Bread and Rolls'),
            ('Cookies and Biscuits', 'Cookies and Biscuits'),
            ('Pies and Tarts', 'Pies and Tarts'),
        ],
        validators=[DataRequired()],
        coerce=str,
        default=[]
    )
    allergens = SelectMultipleField(
        'Product Allergens',
        choices=[
            ('nuts', 'Nuts'),
            ('gluten', 'Gluten'),
            ('dairy', 'Dairy'),
            ('eggs', 'Eggs'),
            ('soy', 'Soy'),
            
        ],
        
        coerce=str,
        
    )
    price = FloatField('Product Price', validators=[DataRequired(), NumberRange(min=0, message="Price must be positive")])
    stock = IntegerField('Stock Quantity', validators=[DataRequired(), NumberRange(min=0, message="Stock cannot be negative")])
    image_file = FileField('Product Image', [FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Add Product')
    


class OrderForm(FlaskForm):
    orderstock = IntegerField('Stock Quantity', validators=[DataRequired()])
    submit = SubmitField('Add Order')

class FeedbackForm(FlaskForm):
    rating = RadioField('Rating', coerce=int, validators=[DataRequired()], choices=[(4, 'Very good'), (3, 'Good'), (2, 'Bad'), (1, 'Very bad')])
    description = TextAreaField('Description', validators=[DataRequired()])
    issue = SelectField('What topic of issues are you having?', choices=[(1,'Delivery Issues'),(2,'Payment Issues'),(3,'Services Issues'),(4,'Product Issues'),(5,'Other Issues')], validators=[DataRequired()])
    submit = SubmitField('Add Feedback')

class ForgetPassword(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Length(min=2, max=200)])
    secretQn = StringField("Secret Question (What is your favourite pet's name)", validators=[DataRequired()])
    submit = SubmitField('Reset Password')

class ResetPassword(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password')

class CartForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired()], default=0)
    submit = SubmitField('Add to cart')

class UpdateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Length(min=2, max=200)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=8,max=8)])
    address = StringField('Address', validators=[DataRequired()])
    secretQn = StringField("Secret Question (What is your favourite pet's name)", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    image_file = FileField('Product Image', validators=[DataRequired(),FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Update User')

    def validate_phone(self, phone):
        if len(phone.data) == 8 and (phone.data).isdigit() == True and phone.data[0] == '8' or '9' or '6':
            print('Success')
        else:
            raise ValidationError('Invalid phone number. Phone number needs to start with 8, 9 ,6')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user != user:
            raise ValidationError('That username is taken or is the current user username. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user != user:
            raise ValidationError('That email is taken or is the current user email. Please choose a different one.')

class UpdateOneUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=8,max=8)])
    address = StringField('Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    image_file = FileField('Product Image', validators=[DataRequired(),FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Update User')

    def validate_phone(self, phone):
        if len(phone.data) == 8 and (phone.data).isdigit() == True and phone.data[0] == '8' or '9' or '6':
            print('Success')
        else:
            raise ValidationError('Invalid phone number. Phone number needs to start with 8, 9 ,6')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user != user:
            raise ValidationError('That username is taken or is the current user username. Please choose a different one.')

class TopUpForm(FlaskForm):
    card = StringField('Card Number', validators=[DataRequired(), Length(min=2, max=20)])
    expiry = StringField('Expiry Date', validators=[DataRequired(), Length(min=2, max=20)])
    csv = IntegerField('CSV',validators=[DataRequired()])
    amount = FloatField('Amount',validators=[DataRequired()])
    submit = SubmitField('Top Up')

class RedeemVoucherForm(FlaskForm):
    submit = SubmitField('Check Out')



from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField,FloatField,RadioField, SelectField, PasswordField, SubmitField, BooleanField,FileField, EmailField, IntegerField,TextAreaField, TimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,NumberRange, Optional
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
        if len(phone.data) == 8 and phone.data.isdigit() and phone.data[0] in ['8', '9', '6']:
            return
        raise ValidationError('Invalid phone number. Phone number needs to start with 8, 9, or 6.')


class VoucherForm(FlaskForm):
    name = StringField('Voucher Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    value = IntegerField('Voucher Value', validators=[DataRequired()])
    credits = IntegerField('Credits', validators=[DataRequired()])
    redeem_date = DateField('Redemption Date',format='%Y-%m-%d')
    expiry_date = DateField('Expiry Date',format='%Y-%m-%d')
    image_file = FileField('Logo', validators=[DataRequired(),FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    isValid = RadioField('Validity', coerce=bool, choices=[(True, 'Available'),(False, 'Not Available')], default=True)
    submit = SubmitField('Add Voucher')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', coerce=int, choices=[(1,'Fruits'),(2,'Bakery and Bread'),(3,'Drinks'),(4,'Oil and Condiments'),(5,'Dairy, Cheese and Eggs'),(6,'Cereals'), (7, 'Meat'),(8,'Vegetable'),] ,validators=[DataRequired()])
    country = SelectField('Country', choices=country(), validators=[DataRequired()])
    price = FloatField('Product price', validators=[DataRequired('Please enter a valid price')])
    image_file = FileField('Product Image', validators=[DataRequired(),FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
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
    
class DonationItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', choices=[('clothes', 'Clothing'),('electronics', 'Electronics'),('books', 'Books'),('toys', 'Toys'),('food', 'Food (Non-Perishable)'),('others', 'Other')], validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    condition = RadioField('Condition', choices=[('new', 'New'),('used', 'Used')], validators=[DataRequired()])
    image_file = FileField('Item Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only.'),FileRequired()])
    preferred_drop_off_method = SelectField('Preferred Drop Off Method', choices=[('drop_off', 'Drop off at location'), ('pickup', 'Request for pickup')],validators=[DataRequired()])
    address = StringField('Pickup Address (if applicable)',validators=[Optional(), Length(max=200)])
    preferred_date = DateField('Preferred Date for Pickup', validators=[Optional()])
    preferred_time = TimeField('Preferred Time for Pickup', validators=[Optional()])
    organisation = SelectField('Choice of Organisation',choices=[('TSA', 'The Salvation Army'),('MINDS', 'MINDS'),('FFTH', 'Food from the Heart'),('RCS', 'Red Cross Singapore')],validators=[DataRequired()])
    submit = SubmitField('Submit Donation')

class DonateForm(FlaskForm):
    amount = FloatField(
        'Donation Amount',
        validators=[
            DataRequired(message="Please enter a valid donation amount."),
            NumberRange(min=1, message="Donation amount must be at least $1.")
        ]
    )
    organization = SelectField(
        'Organization',
        choices=[],  # Placeholder, will be populated dynamically
        validators=[
            DataRequired(message="Please select an organization.")
        ]
    )
    submit = SubmitField('Donate')
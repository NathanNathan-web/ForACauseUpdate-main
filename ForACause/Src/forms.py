from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField,FloatField,RadioField, SelectField, PasswordField, SubmitField, BooleanField,FileField, EmailField, IntegerField,TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,NumberRange,InputRequired
from Src.models import User, Product
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
    name = StringField(
        'Voucher Name',
        validators=[
            DataRequired(message="Voucher name is required."),
            Length(min=3, max=100, message="Voucher name must be between 3 and 100 characters.")
        ]
    )

    description = StringField(
        'Description',
        validators=[
            DataRequired(message="Description is required."),
            Length(min=10, max=200, message="Description must be between 10 and 200 characters.")
        ]
    )

    value = IntegerField(
        'Voucher Value',
        validators=[
            DataRequired(message="Voucher value is required."),
            NumberRange(min=1, max=1000, message="Voucher value must be between 1 and 1000.")
        ]
    )

    credits = IntegerField(
        'Credits',
        validators=[
            DataRequired(message="Credits are required."),
            NumberRange(min=1, max=1000, message="Credits must be between 1 and 1000.")
        ]
    )

    redeem_date = DateField(
        'Redemption Date',
        format='%Y-%m-%d',
        validators=[InputRequired(message="Redemption date is required.")]
    )

    expiry_date = DateField(
        'Expiry Date',
        format='%Y-%m-%d',
        validators=[InputRequired(message="Expiry date is required.")]
    )

    image_file = FileField(
        'Logo',
        validators=[
            DataRequired(message="Please upload an image."),
            FileAllowed(['jpg', 'png', 'jpeg'], 'Only JPG, PNG, and JPEG files are allowed.')
        ]
    )

    isValid = RadioField(
        'Validity',
        coerce=bool,
        choices=[(True, 'Available'), (False, 'Not Available')],
        default=True
    )

    submit = SubmitField('Add Voucher')

    # **🔥 Custom Validation: Ensure expiry date is after redeem date**
    def validate_expiry_date(self, expiry_date):
        if self.redeem_date.data and expiry_date.data:
            if expiry_date.data <= self.redeem_date.data:
                raise ValidationError("Expiry date must be after the redemption date.")

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
    rating = RadioField(
        'Rating',
        coerce=int,
        choices=[
            (4, 'Very good'),
            (3, 'Good'),
            (2, 'Bad'),
            (1, 'Very bad')
        ],
        validators=[
            DataRequired(message="Please select a rating."),
            NumberRange(min=1, max=4, message="Invalid rating selection.")
        ]
    )

    description = TextAreaField(
        'Description',
        validators=[
            DataRequired(message="Please provide a description."),
            Length(min=10, max=500, message="Description must be between 10 and 500 characters.")
        ]
    )

    issue = SelectField(
        'What topic of issues are you having?',
        choices=[
            ('', 'Select an issue'),  # Default empty choice
            (1, 'Delivery Issues'),
            (2, 'Payment Issues'),
            (3, 'Service Issues'),
            (4, 'Product Issues'),
            (5, 'Other Issues')
        ],
        coerce=int,
        validators=[
            DataRequired(message="Please select an issue type.")
        ]
    )

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
    
class DonateForm(FlaskForm):
    amount = FloatField(
        'Donation Amount (SGD)',
        validators=[
            DataRequired(message="Please enter a valid donation amount in SGD."),
            NumberRange(min=1, message="Donation amount must be at least $1 SGD.")
        ]
    )
    submit = SubmitField('Donate Now')
    
    organization = SelectField(
        'Organization',
        choices=[],  # Placeholder, will be populated dynamically
        validators=[
            DataRequired(message="Please select an organization.")
        ]
    )
    submit = SubmitField('Donate')
from ast import Return
from datetime import date, datetime
import random
from flask import jsonify, render_template, url_for, flash, redirect, request, session
from sqlalchemy import func
from . import app, db, bcrypt
from collections import Counter
from datetime import date
from flask import abort, render_template, url_for, flash, redirect, request, session, jsonify
from .forms import RegistrationForm, LoginForm, UpdateOneUserForm,UpdateUserForm,SupplierForm,RedeemVoucherForm,TopUpForm, VoucherForm, FeedbackForm, ForgetPassword, ResetPassword,ProductForm, OrderForm,CartForm, DonationItemForm, DonateForm
from .models import Donation, User, Supplier, Voucher, Feedback,Product,Order,Cart,RedeemedVouchers,DonateItem,VolunteerEvent,UserVolunteer,db
from . import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os
from flask_babel import _
from datetime import datetime, timedelta
import http.client  # Import for chatbot API
import json  # Required for JSON serialization and deserialization
from flask import render_template, url_for, flash, redirect, request, session, jsonify
import logging
import requests
import qrcode
from io import BytesIO
from flask import send_file
import stripe
from sched import scheduler
from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Message
import pytz
from sqlalchemy.exc import IntegrityError

stripe.api_key = "sk_test_51QkUOjJw6qEGWv892rSo4scTB2rqEM8PmzwgpEBjyhW9tDnXRmo3LuUEzmSJoHqyMbOphD8154ZSeB3UMTNqAGxL00OlAkeMM9"

def Vegetable():
    return "Vegetable"
def Fruits():
    return "Fruits"
def BakeryandBread():
    return "Bakery and Bread"
def OilandCondiments():
    return "Oil and Condiments"
def Drinks():
    return "Drinks"
def DairyCheeseEggs():
    return "Dairy, Cheese and Eggs"
def Cereals():
    return "Cereals"
def Meat():
    return "Meat"
def default():
    return "Uncategorized"

def category(i):
        switch={
                1:Fruits(),
                2:BakeryandBread(),
                3:Drinks(),
                4:OilandCondiments(),
                5:DairyCheeseEggs(),
                6:Cereals(),
                7:Meat(),
                8:Vegetable()
             }
        return switch.get(i, default())

scheduler = BackgroundScheduler()
scheduler.start()

def send_reminder_email(donation):
    if not isinstance(donation, DonateItem):
        raise ValueError("schedule_pickup_reminder only handles item donations.")
    
    try:
        print(f"Preparing to send email to {donation.user.email}")
        if not donation.user.email:
            print("No email address found for donation user.")
            return

        # Push app context manually
        with app.app_context():
            msg = Message(
                'Reminder: Your Pickup Schedule for Donation',
                recipients=[donation.user.email]
            )
            msg.body = f"""
            Dear {donation.user.username},

            Thank you once again for your generous donation! We wanted to send you a gentle reminder about your scheduled pickup.

            Here are the details of your donation:

            Donation Name: {donation.name}
            Description: {donation.description}
            Pickup Date: {donation.preferred_date}
            Pickup Time: {donation.preferred_time}

            Please ensure that you're available at the specified time for a smooth and efficient pickup.

            If you have any questions or need to make changes to your pickup details, feel free to reach out to us. 
            We truly appreciate your support in helping those in need!

            Warm regards,
            ForACause Team
            """

            mail.send(msg)
            print(f"Email sent to {donation.user.email}")
    except Exception as e:
        print(f"Error during email sending: {e}")


def schedule_pickup_reminder(donation):
    if not isinstance(donation, DonateItem):
        raise ValueError("schedule_pickup_reminder only handles item donations.")
    
    if donation.preferred_drop_off_method == 'pickup':
        tz = pytz.timezone('Asia/Singapore')  # Set your desired time zone
        
        # Localize preferred time to Singapore timezone
        preferred_time = tz.localize(datetime.combine(donation.preferred_date, donation.preferred_time))
        current_time = datetime.now(tz)  # Get current time in the same time zone
        
        # Calculate reminder time as 12 hours before the preferred pickup time
        reminder_time = preferred_time - timedelta(hours=24)

        # Check if the preferred time is at least 12 hours ahead of current time
        if preferred_time > current_time + timedelta(hours=24):
            # Schedule reminder email 12 hours before the preferred pickup time
            scheduler.add_job(
                send_reminder_email,
                'date',
                run_date=reminder_time,
                args=[donation],
                timezone=tz  # Specify time zone for the job
            )
            print(f"Reminder email scheduled for {donation.user.email} at {reminder_time}")
        else:
            print(f"Preferred time is too close to the current time for {donation.user.email}, skipping reminder.")

def send_collection_email(donation):
    if not isinstance(donation, DonateItem):
        raise ValueError("send_status_update_email only handles item donations.")
    
    try:
        print(f"Preparing to send status update email to {donation.user.email}")
        if not donation.user.email:
            print("No email address found for donation user.")
            return

        with app.app_context():
            msg = Message(
                'Update: Our Team is Out for Collection',
                recipients=[donation.user.email]
            )
            msg.body = f"""
            Dear {donation.user.username},

            We are happy to inform you that our team is now out to collect your donation items.

            Here are the details of your donation:

            Donation Name: {donation.name}
            Description: {donation.description}
            Pickup Date: {donation.preferred_date}
            Pickup Time: {donation.preferred_time}

            Thank you for your generosity and support. If you have any questions, please feel free to reach out.

            Warm regards,
            ForACause Team
            """

            mail.send(msg)
            print(f"Status update email sent to {donation.user.email}")
    except Exception as e:
        print(f"Error during email sending: {e}")

@app.route('/', methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        if current_user.isAdmin != True:
            form = FeedbackForm()
            if form.validate_on_submit():
                feedback = Feedback(rating=form.rating.data, description=form.description.data,
                                    issue=form.issue.data, feedback_date=date.today())
                db.session.add(feedback)
                db.session.commit()
                flash('Feedback created!', 'success')
                return redirect(url_for('home'))
            return render_template('index.html', form=form)
        else:
            return render_template('index.html')
    else:
        return render_template('index.html')


# To Set Admin Management View to Admin Customer View
@app.route('/adminCustomer')
def admincustomer():
    if current_user.is_authenticated:
        if current_user.isAdmin == True:
            adminStat = True
            if adminStat == True:
                adminStat = False
                return render_template('index.html', adminStat=adminStat)

# To Set Admin Customer View back to Admin Management View


@app.route('/returnAdmin')
def returnadmin():
    if current_user.is_authenticated:
        if current_user.isAdmin == True:
            adminStat = False
            if adminStat == False:
                print(adminStat)
                adminStat = True
                return render_template('accountAdmin.html', adminStat=adminStat)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('pagenotfound.html'), 404


@app.route('/forgetPw', methods=['GET', 'POST'])
def forgetpw():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ForgetPassword()
    for user in form:
        print(user)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print(user)
        print(user.secretQn)
        if user and user.secretQn == form.secretQn.data:
            session['email'] = user.email
            return redirect(url_for('resetpassword', form=form))
        else:
            flash('Email and Secret Question does not match!', 'danger')
    return render_template('forgetpw.html', form=form)


@app.route('/resetpassword', methods=['GET', 'POST'])
def resetpassword():
    form = ResetPassword()
    if form.validate_on_submit():
        print('asd')
        hashed_pw = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User.query.filter_by(email= session['email']).first()
        user.password = hashed_pw
        db.session.commit()
        flash('Account reset password is successful.', 'success')
        return redirect(url_for('login', form=form))
    else:
        flash('Password does not match!', 'warning')
    return render_template('resetpassword.html', form=form)


# ===================================== Customer =====================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw,
                    phone=form.phone.data, address=form.address.data, secretQn=form.secretQn.data, cart="")
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.isAdmin == True:
                login_user(user, remember=form.remember.data)
                flash(f'You have been logged in ({user.username})', 'success')
                return render_template('index.html', form=form, adminStat=True)
            else:
                login_user(user, remember=form.remember.data)
                flash(f'You have been logged in ({user.username})', 'success')
                return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)


@app.route('/account')
@login_required
def account():
    if current_user.is_authenticated:
        # Redeem vouchers and other user info (unchanged)
        redeemvoucher_list = []
        donateitem_list = []
        
        image_file = url_for('static', filename='images/' + current_user.image_file)
        
        user = User.query.filter_by(id=current_user.id).first()
        redeemvouchers = RedeemedVouchers.query.filter_by(user_id=current_user.id).all()
        donateitems=DonateItem.query.filter_by(user_id=current_user.id).all()
        
        for redeemvoucher in redeemvouchers:
            redeemvoucher_list.append(redeemvoucher)
        # Pass app or app.config['LANGUAGES'] to the template
        
        for donateitem in donateitems:
            if donateitem.image_file:
                donateitem.image_path = url_for('static', filename='uploads/' + donateitem.image_file)
            else:
                donateitem.image_path = None
            donateitem_list.append(donateitem)
        
        # Get order history from session (or temporary storage)
        order_history = session.get('order_history', [])
        
        return render_template(
            'account.html',
            image_file=image_file,
            user=user,
            redeemvoucher_list=redeemvoucher_list,
            donateitems=donateitem_list,
            order_history=order_history)
        
    else:
        return render_template('login.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/donateItem', methods=['GET', 'POST'])
@login_required
def donateItem():
    if current_user.isAdmin:
        flash('Admins cannot access this page!', 'danger')
        return redirect(url_for('home'))
    
    form = DonationItemForm()

    if form.validate_on_submit():  # Check if the form is valid and submitted
        image_file_path = None  # Default to None for no image

        # Handle image file if uploaded
        if form.image_file.data:
            image = form.image_file.data
            if allowed_file(image.filename):  # Check if the file is allowed
                filename = secure_filename(image.filename)  # Secure the filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                try:
                    image.save(file_path)  # Save the file to the server
                    image_file_path = filename  # Store the file name for DB
                except Exception as e:
                    flash(f"Error saving image: {str(e)}", 'danger')

        # Create a new DonateItem object with the form data
        new_donation = DonateItem(
            user_id=current_user.id, 
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            quantity=form.quantity.data,
            condition=form.condition.data,
            image_file=image_file_path,  # Store the image file path
            preferred_drop_off_method=form.preferred_drop_off_method.data,
            address=form.address.data,
            preferred_date=form.preferred_date.data,
            preferred_time=form.preferred_time.data,
            organisation=form.organisation.data
        )

        # Add the new donation to the database session and commit
        db.session.add(new_donation)
        db.session.commit()

        schedule_pickup_reminder(new_donation)

        # Flash success message and redirect to home page
        flash('Thank you for your donation!', 'success')
        return redirect(url_for('home'))

    # If form isn't submitted or valid, just render the form
    return render_template('donateItem.html', form=form)

@app.route('/edit_donation_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_donation_item(item_id):
    donate_item = DonateItem.query.get_or_404(item_id)
    
    # Create a form instance and populate it with existing data
    form = DonationItemForm(obj=donate_item)

    # Handle form submission
    if form.validate_on_submit():
        donate_item.name = form.name.data
        donate_item.description = form.description.data
        donate_item.category = form.category.data
        donate_item.quantity = form.quantity.data
        donate_item.condition = form.condition.data
        donate_item.image_file = form.image_file.data
        donate_item.preferred_drop_off_method = form.preferred_drop_off_method.data
        donate_item.address = form.address.data
        donate_item.preferred_date = form.preferred_date.data
        donate_item.preferred_time = form.preferred_time.data
        donate_item.organisation = form.organisation.data

        # Handle image file if uploaded
        if form.image_file.data:
            image = form.image_file.data
            if allowed_file(image.filename):  # Check if the file is allowed
                filename = secure_filename(image.filename)  # Secure the filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                try:
                    image.save(file_path)  # Save the file to the server
                    donate_item.image_file = filename  # Update the image file path in the DB
                except Exception as e:
                    flash(f"Error saving image: {str(e)}", 'danger')

        db.session.commit()

        schedule_pickup_reminder(donate_item)

        flash('Donation item updated successfully!', 'success')
        if current_user.isAdmin:
            return redirect(url_for('donateitemadmin')) 
        else:
            return redirect(url_for('account'))

    return render_template('editDonationItem.html', form=form)

@app.route('/donateItemAdmin')
@login_required
def donateitemadmin():
    donation_items = DonateItem.query.all()
    return render_template('donateItemAdmin.html', adminStat = True, donation_items=donation_items)

@app.route('/update_status/<int:id>/<string:new_status>', methods=['GET'])
@login_required
def update_status(id, new_status):
    # Fetch the item by ID
    item = DonateItem.query.get_or_404(id)
    
    # Update the status
    item.status = new_status
    db.session.commit()

    # Send email if status is "Out for Collection"
    if new_status == "Out for Collection":
        send_collection_email(item)

    return redirect(url_for('donateitemadmin'))

@app.route('/deleteDonationItem/<int:id>', methods=['POST'])
def deletedonationitem(id):
    item = DonateItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    
    if current_user.isAdmin:
        return redirect(url_for('donateitemadmin'))
    else:
        return redirect(url_for('account'))


@app.route('/topup', methods=['GET', 'POST'])
@login_required
def topup():
    if current_user.is_authenticated:
        form = TopUpForm()
        if form.validate_on_submit():
            user = User.query.filter_by(id=current_user.id).first()
            user.balance += form.amount.data
            db.session.commit()
            return redirect(url_for('account'))
        return render_template('topup.html',form=form)
    else:
        return render_template('login.html')

@app.route('/updateOneUser/<int:id>/', methods=['GET', 'POST'])
@login_required
def updateoneuser(id):
    if current_user.is_authenticated:
        form = UpdateOneUserForm()
        if request.method == 'POST' and form.validate():
            user = User.query.filter_by(id=id).first()
            if form.phone.data[0] == '8' or form.phone.data[0] == '9' or form.phone.data[0] == '6' and form.name.data.isalpha() == True:
                user.username = form.username.data
                user.phone = form.phone.data
                user.address = form.address.data
                user.password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
                user.image_file = form.image_file.data
                db.session.commit()
                flash('Update user success!', 'success')
                return redirect(url_for('account', idsite=True))
            else:
                flash('Update user failed, Phone number must start with 8 , 9 or 6 or Name cannot contain number', 'danger')
                return render_template('updateOneUser.html', form=form, idsite=True)
        else:
            user = User.query.filter_by(id=id).first()
            form.username.data = user.username
            form.phone.data = user.phone
            form.address.data = user.address
            form.password.data = user.password
            form.image_file.data = user.image_file
            userimagefile = ''
            userimagefile = user.image_file
            return render_template('updateOneUser.html', form=form, idsite=True, userimagefile=userimagefile)
    else:
        return redirect(url_for('login'))

@app.route('/product', methods=['GET', 'POST'])
def product():
    search_query = ''
    category_filter = ''
    allergy_filter = ''

    # Handle POST request
    if request.method == 'POST':
        search_query = request.form.get('search', '').strip().lower()
        category_filter = request.form.get('category', '')
        allergy_filter = request.form.get('allergy', '')

    # Fetch all products
    products_query = Product.query

    # Apply search filter
    if search_query:
        products_query = products_query.filter(Product.name.ilike(f"%{search_query}%"))

    # Apply category filter (now filtering by string)
    if category_filter:
        products_query = products_query.filter(Product.category == category_filter)

    # Apply allergy filter
    if allergy_filter:
        products_query = products_query.filter(~Product.allergens.ilike(f"%{allergy_filter}%"))

    # Execute query and fetch results
    products = products_query.all()

    # Category map for dropdowns (can now match string directly)
    category_map = {
        "Cakes and Pastries": "Cakes and Pastries",
        "Bread and Rolls": "Bread and Rolls",
        "Cookies and Biscuits": "Cookies and Biscuits",
        "Pies and Tarts": "Pies and Tarts"
    }

    return render_template(
        'product.html',
        products_list=products,
        category_map=category_map,
        search=search_query,
        category=category_filter,
        allergy=allergy_filter
    )
@app.route('/productDashboard')
@login_required
def product_dashboard():
    if not current_user.isAdmin:
        flash("Admin access required!", "warning")
        return redirect(url_for('home'))

    most_sold = [
        {"name": "Coffee Bread", "sales": 120},
        {"name": "Garlic Bread", "sales": 95},
        {"name": "Monster Cookie", "sales": 85}
    ]

    weekly_revenue = [200, 350, 200, 150, 500, 300, 400]

    total_orders = [21, 32, 12, 12, 54, 36, 44]

    category_sales = {
        "Cookies & Biscuits": 36,
        "Pies & Tarts": 10,
        "Cakes & Pastries": 20,
        "Bread & Rolls": 34
    }

    avg_order_value = [12, 15, 17, 19, 21, 22, 24]

    return render_template(
        'productDashboard.html',
        most_sold=most_sold,
        weekly_revenue=weekly_revenue,
        total_orders=total_orders,
        category_sales=category_sales,
        avg_order_value=avg_order_value,
    )


@app.route('/add_to_cart/<int:product_id>', methods=['GET'])
@login_required
def add_to_cart(product_id):
    # Fetch the product from the database
    product = Product.query.get_or_404(product_id)

    # Check if the product is already in the cart for the current user
    existing_cart_item = Cart.query.filter_by(product_id=product_id, user_id=current_user.id).first()

    if existing_cart_item:
        # Increment quantity if it exists
        if existing_cart_item.quantity < product.stock:
            existing_cart_item.quantity += 1
            flash(f"{product.name} quantity updated in your cart!", "success")
        else:
            flash(f"Cannot add more of {product.name}. Stock limit reached!", "danger")
    else:
        # Add new item to the cart
        new_cart_item = Cart(user_id=current_user.id, product_id=product.id, quantity=1)
        db.session.add(new_cart_item)
        flash(f"{product.name} added to your cart!", "success")

    # Commit the changes
    db.session.commit()

    # Redirect to the shopping cart page
    return redirect(url_for('cart'))


@app.route('/productDetails/<int:id>', methods=['GET', 'POST'])
def productdetails(id):
    if current_user.is_authenticated:
        product = Product.query.filter_by(id=id).first()
        cart = Cart.query.filter_by(product_id=id).first()
        form = CartForm()

        # Generate a new random rating (between 3.0 and 5.0) on every request
        random_rating = round(random.uniform(3.0, 5.0), 1)
        rounded_stars = round(random_rating)  # Round for star display

        if form.validate_on_submit:
            if 0 < form.quantity.data <= product.stock:
                quantity = form.quantity.data
                current_user.add_to_cart(product, quantity)
                return redirect(url_for('cart'))
            else:
                flash('Quantity must be within the stock amount', 'warning')
                return render_template('productdetails.html', product=product, idsite=True, form=form, random_rating=random_rating, rounded_stars=rounded_stars)
        else:
            flash('Quantity needs to be a valid number', 'warning')

        return render_template('productdetails.html', product=product, idsite=True, form=form, random_rating=random_rating, rounded_stars=rounded_stars)

    else:
        return redirect(url_for('login'))
        
@app.route('/update_profile_image', methods=['POST'])
@login_required
def update_profile_image():
    if 'profile_image' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('account'))

    file = request.files['profile_image']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('account'))

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Update the user's image_file field in the database
        user = User.query.get(current_user.id)
        user.image_file = filename
        db.session.commit()

        flash('Profile image updated successfully!', 'success')
        return redirect(url_for('account'))

@app.route('/change_language', methods=['POST'])
def change_language():
    """
    Updates the session with the selected language and redirects to the account page.
    """
    lang = request.form.get('lang')
    if lang in app.config['LANGUAGES']:
        session['lang'] = lang  # Save the selected language in the session
    return redirect(url_for('account'))  # Redirect to the account page

@app.route('/set_language', methods=['POST'])
def set_language():
    selected_language = request.form.get('language')
    if selected_language in app.config['LANGUAGES']:
        session['lang'] = selected_language
        flash(_('Language updated successfully!'), 'success')
    else:
        flash(_('Invalid language selection.'), 'danger')
    return redirect(request.referrer or url_for('home'))


# =================================  Cart ==================================


@app.route("/remove_from_cart/<int:product_id>", methods=['GET', 'POST'])
@login_required
def remove_from_cart(product_id):
    if current_user.is_authenticated:
        product = Product.query.get(product_id)
        current_user.remove_from_cart(product)
        return redirect(url_for('cart'))
    else:
        return redirect(url_for('login'))

@app.route("/shoppingcart", methods=['GET', 'POST'])
@login_required
def cart():
    carts_list = []  # Store valid cart items
    total = 0  # Initialize total price
    error_messages = []  # Store validation errors
    recommendations = []  # Store recommended products

    if current_user.is_authenticated:
        # Fetch all cart items for the logged-in user
        carts = Cart.query.filter_by(user_id=current_user.id).all()

        if request.method == 'POST':
            # Handle quantity updates from the form
            for cart in carts:
                quantity_field = f"quantity_{cart.id}"  # Get dynamic field name
                new_quantity = request.form.get(quantity_field, type=int)  # Fetch new quantity

                if new_quantity is not None:
                    # Validate new quantity
                    if new_quantity > cart.product.stock:
                        error_messages.append(
                            f"Quantity for '{cart.product.name}' cannot exceed available stock ({cart.product.stock})."
                        )
                    elif new_quantity <= 0:
                        error_messages.append(
                            f"Quantity for '{cart.product.name}' must be at least 1."
                        )
                    else:
                        # Update the cart item with the new valid quantity
                        cart.quantity = new_quantity
                        db.session.commit()

        # Calculate the total price correctly
        for cart in carts:
            if cart.product:  # Ensure product exists
                # Apply 10% discount only for "cookies and biscuits"
                if cart.product.category.lower() in ["cookies and biscuits", "cookies & biscuits"]:
                    item_price = cart.product.price * 0.90  # Apply 10% discount
                else:
                    item_price = cart.product.price  # Keep original price

                total += cart.quantity * item_price  # Accumulate total price
                carts_list.append(cart)  # Store valid cart items
            else:
                # Remove invalid cart entries (e.g., product no longer exists)
                db.session.delete(cart)
                db.session.commit()

        # Debugging: Print total to verify calculation
        print("Calculated Total:", total)

        # Fetch product recommendations
        if carts_list:
            first_product_category = carts_list[0].product.category  # Get category of first product
            cart_product_ids = [cart.product_id for cart in carts_list]  # Get product IDs in cart
            
            # Exclude products already in cart from recommendations
            recommendations = Product.query.filter(
                Product.category == first_product_category,
                ~Product.id.in_(cart_product_ids)
            ).limit(3).all()

        # Store the total in the session for consistency across views
        session['total'] = total

        # Render shopping cart page
        return render_template(
            'shoppingcart.html',
            carts=carts_list,
            total=total,
            error_messages=error_messages,
            recommendations=recommendations
        )

    else:
        # Redirect to login if the user is not authenticated
        flash("Please log in to view your shopping cart.", "warning")
        return redirect(url_for('login'))

@app.route('/order_confirmation')
@login_required
def order_confirmation():
    order_id = f"ORD-{random.randint(100000, 999999)}"  
    items = session.get('items', [])  
    delivery_method = session.get('delivery_method', 'Not Specified')
    time_slot = session.get('time_slot', 'Not Specified')
    total = session.get('total', 0)

    if not items or total == 0:
        return redirect(url_for('cart'))  

    # Convert datetime to Singapore timezone
    singapore_tz = pytz.timezone('Asia/Singapore')
    current_time = datetime.now(singapore_tz).strftime("%Y-%m-%d %H:%M:%S")  

    # ✅ Store order_id inside order dictionary
    order = {
        "order_id": order_id,  # Store the Order ID
        "date": current_time,
        "order_items": items,
        "delivery_method": delivery_method,
        "time_slot": time_slot,
        "total": total,
    }

    # ✅ Save order history with order_id
    order_history = session.get('order_history', [])
    order_history.append(order)
    session['order_history'] = order_history

    # ✅ Store order_id in session (for use in confirmation page)
    session['last_order_id'] = order_id  

    # ✅ Clear session variables after order is placed
    session.pop('items', None)
    session.pop('delivery_method', None)
    session.pop('time_slot', None)
    session.pop('total', None)

    return render_template(
        'order_confirmation.html',
        order_id=order_id,  
        items=order["order_items"],
        delivery_method=order["delivery_method"],
        time_slot=order["time_slot"],
        total=order["total"]
    )








@app.route('/finalize_payment', methods=['POST'])
@login_required
def finalize_payment():
    # Retrieve form data
    delivery_method = request.form.get('delivery_method', 'Not Specified')
    time_slot = request.form.get('time_slot', 'Not Specified')
    payment_method = request.form.get('payment_method')

    if not session.get('total'):
        flash("Total amount not found in session. Please try again.", "danger")
        return redirect(url_for('checkout'))

    if payment_method == "paynow":
        try:
            # Simulate product stock update
            carts = Cart.query.filter_by(user_id=current_user.id).all()
            items = []
            for cart in carts:
                product = cart.product  # Assuming Cart has a relationship to Product
                if product.stock >= cart.quantity:
                    product.stock -= cart.quantity  # Deduct purchased quantity
                    items.append({
                        "name": product.name,
                        "quantity": cart.quantity,
                        "price": product.price * 0.85,
                        "image_file": product.image_file,
                    })
                    db.session.delete(cart)  # Remove the cart item
                else:
                    flash(f"Insufficient stock for {product.name}. Please adjust your cart.", "danger")
                    return redirect(url_for('cart'))
            
            db.session.commit()  # Save changes to the database
            
            # Store items and delivery info in session
            session['items'] = items
            session['delivery_method'] = delivery_method
            session['time_slot'] = time_slot

            # Redirect to payment confirmation
            qr_code_path = "/static/images/yh_qr.jpg"  # Hardcoded QR code
            return render_template('payment_confirmation.html', qr_code_path=qr_code_path, total=session['total'])
        
        except Exception as e:
            flash(f"An error occurred while processing your payment: {str(e)}", "danger")
            return redirect(url_for('checkout'))
    else:
        flash("Unsupported payment method selected.", "warning")
        return redirect(url_for('checkout'))











@app.route('/usevoucher', methods=['GET', 'POST'])
def usevoucher():
    if current_user.is_authenticated:
        if request.method == 'POST':
            vouchercode = request.form.get('vouchercode')
            currentvoucher = RedeemedVouchers.query.filter_by(id = vouchercode).first()
            session['currentvoucher'] = currentvoucher.voucher.value
            session['totalprice'] -= session['currentvoucher']
        return redirect(url_for('cart'))
    else:
        return redirect(url_for('login'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        # Retrieve delivery method and time slot from form
        delivery_method = request.form.get('delivery_method')
        time_slot = request.form.get('time_slot')

        # Validate the inputs
        if not delivery_method or not time_slot:
            flash("Please select a delivery method and time slot.", "warning")
            return redirect(url_for('checkout'))

        # Store delivery details in the session
        session['delivery_details'] = {
            "delivery_method": delivery_method,
            "time_slot": time_slot
        }

        # Redirect to the payment page
        return redirect(url_for('payment_page'))

    # Render the checkout page
    total = session.get('total', 0)
    return render_template('checkout.html', total=total)



# =================================  VOUCHER ==================================
    
@app.route('/voucher')
def voucher():
    vouchers_list = []
    vouchers = Voucher.query.all()
    for voucher in vouchers:
        vouchers_list.append(voucher)
    return render_template('voucher.html', vouchers_list=vouchers_list)



@app.route('/redeemVoucher/<int:id>', methods= ['GET', 'POST'])
def redeemvoucher(id):
    if current_user.is_authenticated:
        current_user.credit += 500
        db.session.commit()
        vouchers = Voucher.query.filter_by(id=id).first()
        print(current_user.credit)
        print(vouchers.credit)
        if current_user.credit >= vouchers.credit:
            redeem = RedeemedVouchers(status=1, user_id=current_user.id, voucher_id=vouchers.id)
            current_user.credit -= vouchers.credit
            db.session.add(redeem)
            db.session.commit()
            return redirect(url_for('account'))
        else:
            flash('Not enough credit to redeem', 'warning')
            return redirect(url_for('voucher'))
    else:
        return redirect(url_for('login'))
# =================================  Service ==================================
@app.route('/service', methods=['GET', 'POST'])
@login_required
def service():
    if request.method == 'POST':
        # Retrieve form data
        rating = request.form.get('rating')
        description = request.form.get('description')
        issue = request.form.get('issue')
        feedback_date = request.form.get('feedback_date')

        # Validation
        if not rating or not description or not feedback_date:
            flash('Please fill in all required fields!', 'danger')
            return redirect(url_for('service'))

        # Save feedback data to the database
        feedback = Feedback(
            rating=int(rating),  # Convert rating to integer
            description=description,
            issue=issue,
            feedback_date=date.fromisoformat(feedback_date)  # Convert string to date object
        )
        db.session.add(feedback)
        db.session.commit()

        flash('Thank you for your feedback!', 'success')

        # Redirect to the homepage after submission
        return redirect(url_for('home'))

    return render_template('service.html')

    

# ===================================== Admin =====================================

@app.route('/accountAdmin')
@login_required
def accountadmin():
    if current_user.is_authenticated and current_user.isAdmin == True:
        user_list = []
        users = User.query.all()
        for user in users:
            user_list.append(user)
        return render_template('accountAdmin.html', adminStat=True, user_list=user_list)
    else:
        return redirect(url_for('login'))


@app.route('/deleteUser/<int:id>', methods=['POST'])
@login_required
def deleteuser(id):
    user = User.query.filter_by(id=id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('accountadmin', idsite=True))


# ============================= PRODUCT =============================

@app.route('/productadmin', methods=['GET', 'POST'])
@login_required
def productadmin():
    if current_user.is_authenticated and current_user.isAdmin:
        search_query = ''
        selected_category = ''
        selected_allergen = ''

        if request.method == 'POST':
            search_query = request.form.get('search', '').strip().lower()
            selected_category = request.form.get('category', '')
            selected_allergen = request.form.get('allergen', '')

        # Fetch all products
        products_query = Product.query

        # Apply search filter
        if search_query:
            products_query = products_query.filter(Product.name.ilike(f"%{search_query}%"))

        # Apply category filter
        if selected_category:
            products_query = products_query.filter(Product.category == selected_category)

        # Apply allergen filter (ensure it shows products containing the allergen)
        if selected_allergen:
            products_query = products_query.filter(Product.allergens.ilike(f"%{selected_allergen}%"))

        # Fetch the filtered products
        products = products_query.all()

        return render_template(
            'productAdmin.html',
            product_list=products,
            search=search_query,
            selected_category=selected_category,
            selected_allergen=selected_allergen,
            adminStat=True,
            suppliercount=Supplier.query.count()
        )
    else:
        flash("You need admin privileges to access this page.", "warning")
        return redirect(url_for('login'))



@app.route('/createProduct', methods=['GET', 'POST'])
@login_required
def createProduct():
    # Ensure only admin users can access this route
    if current_user.is_authenticated and current_user.isAdmin:
        # Initialize the ProductForm
        form = ProductForm()

        # Handle form submission
        if form.validate_on_submit():
            # Get selected allergens as a comma-separated string
            selected_allergens = ', '.join(form.allergens.data)

            # Create a new Product object with form data
            product = Product(
                name=form.name.data,
                description=form.description.data,
                category=form.category.data,
                allergens=selected_allergens,  # Save selected allergens
                price=form.price.data,
                stock=form.stock.data,
                image_file=form.image_file.data.filename,
                isValid=True
            )

            # Save the uploaded image file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], form.image_file.data.filename)
            form.image_file.data.save(file_path)

            # Add and commit the product to the database
            db.session.add(product)
            db.session.commit()

            # Flash a success message and redirect to the admin page
            flash('New product created successfully!', 'success')
            return redirect(url_for('productadmin'))

        # Render the form if it’s a GET request or form validation failed
        return render_template('createProduct.html', form=form, adminStat=True)
    
    # Redirect non-admin users to the login page
    return redirect(url_for('login'))


@app.route('/updateProduct', methods=['GET', 'POST'])
def updateProduct():
    product_id = request.args.get('id')  # Get product ID from query string
    product = Product.query.get(product_id)  # Fetch the product from the database

    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('productadmin'))  # Redirect to productAdmin if product is not found

    form = ProductForm(obj=product)  # Populate the form with existing product data

    # Ensure allergens are initialized correctly for pre-check
    if product.allergens:
        form.allergens.data = product.allergens.split(', ')
    else:
        form.allergens.data = []  # Initialize as an empty list if no allergens

    if form.validate_on_submit():
        # Update product fields with form data
        product.name = form.name.data
        product.description = form.description.data
        product.category = form.category.data

        # Handle allergens safely
        submitted_allergens = request.form.getlist('allergens[]')  # Get list of selected allergens
        product.allergens = ', '.join(submitted_allergens) if submitted_allergens else ''  # Save as a comma-separated string

        product.price = form.price.data
        product.stock = form.stock.data

        # Handle image upload (keep the old image if no new image is uploaded)
        if form.image_file.data:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], form.image_file.data.filename)
            form.image_file.data.save(file_path)
            product.image_file = form.image_file.data.filename  # Update the image file name in the database

        db.session.commit()  # Commit the changes to the database
        flash('Product updated successfully!', 'success')
        return redirect(url_for('productadmin'))  # Redirect to productAdmin after updating the product

    return render_template('updateProduct.html', form=form, product=product,adminStat=True)




@app.route('/updateUser/<int:id>/', methods=['GET', 'POST'])
def updateuser(id):
    if current_user.is_authenticated and current_user.isAdmin == True:
        form = UpdateUserForm()
        if request.method == 'POST' and form.validate():
            user = User.query.filter_by(id=id).first()
            if form.phone.data[0] == '8' or form.phone.data[0] == '9' or form.phone.data[0] == '6' and form.name.data.isalpha() == True:
                user.username = form.username.data
                user.email = form.email.data
                user.phone = form.phone.data
                user.secretQn = form.secretQn.data
                user.address = form.address.data
                user.password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
                user.image_file = form.image_file.data
                db.session.commit()
                flash('Update user success!', 'success')
                return redirect(url_for('accountadmin', idsite=True))
            else:
                flash('Update user failed, Phone number must start with 8 , 9 or 6 or Name cannot contain number', 'danger')
                return render_template('updateUser.html', form=form, idsite=True)
        else:
            user = User.query.filter_by(id=id).first()
            form.username.data = user.username
            form.email.data = user.email
            form.phone.data = user.phone
            form.secretQn.data = user.secretQn
            form.address.data = user.address
            form.password.data = user.password
            form.image_file.data = user.image_file
            userimagefile = ''
            userimagefile = user.image_file
            return render_template('updateUser.html', form=form, idsite=True, userimagefile=userimagefile)
    else:
        return redirect(url_for('login'))

@app.route('/deleteProduct/<int:id>', methods=['POST'])
@login_required
def deleteproduct(id):
    if current_user.is_authenticated and current_user.isAdmin == True:
        product = Product.query.filter_by(id=id).first()
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for('productadmin', idsite=True))




# ============================ INVENTORY ============================

@app.route('/inventoryAdmin', methods=['GET', 'POST'])
@login_required
def inventoryadmin():
    if current_user.is_authenticated and current_user.isAdmin == True:
        supplier_list = []
        suppliers = Supplier.query.all()
        for supplier in suppliers:  
            supplier_list.append(supplier)
        return render_template('inventoryAdmin.html', supplier_list=supplier_list, adminStat=True)
    else:
        return render_template('login.html')


@app.route('/createSupplier', methods=['GET', 'POST'])
@login_required
def createsupplier():
    # Ensure only admins can access this page
    if not current_user.isAdmin:
        flash('You must be an admin to access this page!', 'danger')
        return redirect(url_for('home'))

    form = SupplierForm()

    if form.validate_on_submit():  # Check if the form is valid and submitted
        image_file_path = None  # Default to None for no image

        # Handle image file if uploaded
        if form.image_file.data:
            image = form.image_file.data
            if allowed_file(image.filename):  # Check if the file is allowed
                filename = secure_filename(image.filename)  # Secure the filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                try:
                    image.save(file_path)  # Save the file to the server
                    image_file_path = filename  # Store the file name for DB
                except Exception as e:
                    flash(f"Error saving logo image: {str(e)}", 'danger')

        # Check if a supplier with the same name or email already exists
        existing_supplier = Supplier.query.filter(
            (Supplier.name == form.name.data) |
            (Supplier.email == form.email.data)
        ).first()

        if existing_supplier:
            flash('A supplier with this name or email already exists. Please use different details.', 'danger')
        else:
            # Create a new Supplier object with the form data
            new_supplier = Supplier(
                name=form.name.data,
                email=form.email.data,
                password=form.password.data,
                phone=form.phone.data,
                company=form.company.data,
                address=form.address.data,
                country=form.country.data,
                image_file=image_file_path,  # Store the image file path
                isValid=form.isValid.data == 1
            )

            # Add the new supplier to the database session
            db.session.add(new_supplier)

            try:
                db.session.commit()  # Commit the changes
                flash('New supplier created successfully!', 'success')
                return redirect(url_for('inventoryadmin'))
            except Exception as e:
                db.session.rollback()  # Rollback changes on error
                flash(f"An error occurred while saving the supplier: {str(e)}", 'danger')

    # If form isn't submitted or valid, just render the form
    return render_template('createSupplier.html', form=form, adminStat=True)



@app.route('/updateSupplier/<int:id>/', methods=['GET', 'POST'])
def updatesupplier(id):
    supplier = Supplier.query.get_or_404(id)  # Query supplier once
    
    # Create a form instance and populate it with existing data
    form = SupplierForm(obj=supplier)

    # Handle form submission
    if form.validate_on_submit():
        supplier.name = form.name.data
        supplier.email = form.email.data
        supplier.phone = form.phone.data
        supplier.company = form.company.data
        supplier.address = form.address.data
        supplier.country = form.country.data
        supplier.isValid = form.isValid.data  # Update validity status

        # Handle image file if uploaded
        if form.image_file.data:
            image = form.image_file.data
            if allowed_file(image.filename):  # Check if the file is allowed
                filename = secure_filename(image.filename)  # Secure the filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                try:
                    image.save(file_path)  # Save the file to the server
                    supplier.image_file = filename  # Update the image file path in the DB
                except Exception as e:
                    flash(f"Error saving image: {str(e)}", 'danger')

        db.session.commit()  # Commit the changes

        flash('Supplier updated successfully!', 'success')
        return redirect(url_for('inventoryadmin', idsite=True))  # Redirect after successful update

    return render_template('updateSupplier.html', adminStat=True, form=form, supplierimage=supplier.image_file, idsite=True)

@app.route('/deleteSupplier/<int:id>', methods=['POST'])
@login_required
def deletesupplier(id):
    if current_user.is_authenticated and current_user.isAdmin == True:
        supplier = Supplier.query.filter_by(id=id).first()
        db.session.delete(supplier)
        db.session.commit()
        return redirect(url_for('inventoryadmin', idsite=True))
    else:
        return redirect(url_for('login'))
    

@app.route('/createOrder/<int:id>/', methods=['GET', 'POST'])
def createorder(id):
    if current_user.is_authenticated and current_user.isAdmin == True:
        supplier = None
        form = OrderForm()
        product_list = []
        products = Product.query.all()
        for product in products:
                product_list.append(product)
        if request.method == 'POST' and form.validate():
            productname = request.form.get('productname')
            supplier = Supplier.query.filter_by(id=id).first()
            products = Product.query.all()
            for product in products:
                if product.name == productname:
                    new_order = Order(orderstock=form.orderstock.data, date_ordered=date.today(), date_decision='--' , status=1, supplier_id=supplier.id, product_id=product.id)
                    db.session.add(new_order)
                    db.session.commit()
                    
            return redirect(url_for('retrieveorder'))
        return render_template('createOrder.html', adminStat=True, form=form, supplier=supplier, idsite=True, product_list = product_list)
    else:
        return redirect(url_for('login'))

@app.route('/retrieveOrder')
def retrieveorder():
    if current_user.is_authenticated and current_user.isAdmin == True:
        # Get the search and filter parameters from the query string
        search_order_id = request.args.get('search_order_id', '')
        filter_status = request.args.get('filter_status', '')

        # Start with the base query
        orders_query = Order.query

        # Apply the filter by order ID if provided
        if search_order_id:
            orders_query = orders_query.filter(Order.id.like(f'%{search_order_id}%'))

        # Apply the filter by status if provided
        if filter_status:
            orders_query = orders_query.filter(Order.status == int(filter_status))

        # Fetch the filtered orders
        orders = orders_query.all()

        return render_template(
            'retrieveOrder.html', 
            adminStat=True, 
            order_list=orders, 
            search_order_id=search_order_id,  # Pass the search term back to the template
            filter_status=filter_status       # Pass the selected filter back to the template
        )
    else:
        return redirect(url_for('login'))
    
@app.route('/updateOrder/<int:order_id>/', methods=['GET', 'POST'])
@login_required
def updateOrder(order_id):
    if current_user.is_authenticated and current_user.isAdmin == True:
        order = Order.query.get_or_404(order_id)
        form = OrderForm()

        # Pre-populate product dropdown with current product list
        product_list = Product.query.all()
        
        if request.method == 'POST' and form.validate():
            productname = request.form.get('productname')
            # Find the corresponding product
            product = Product.query.filter_by(name=productname).first()
            if product:
                # Update order details
                order.orderstock = form.orderstock.data
                order.product_id = product.id
                db.session.commit()
                flash('Order updated successfully!', 'success')
                return redirect(url_for('retrieveorder'))  # Adjust as necessary for your flow

        # Render template with the current order and form
        return render_template('updateOrder.html', form=form, product_list=product_list, order=order)
    else:
        return redirect(url_for('login'))
    
# ===================================== Supplier ======================================

@app.route('/supplierLogin', methods=['GET', 'POST'])
def supplierlogin():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        supplier = Supplier.query.filter_by(email=form.email.data).first()
        if supplier and supplier.password == form.password.data:
            login_user(supplier, remember=form.remember.data)
            flash(f'You have been logged in ({supplier.email})', 'success')
            return redirect('/supplierIndex')
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('supplierLogin.html', form=form)

@app.route('/supplierIndex')
@login_required
def supplierhome():
    if current_user.is_authenticated:
        try:
            orders_list = []
            orders = Order.query.all()
            for order in orders:
                if order.supplier.id == current_user.id:
                    orders_list.append(order)
            return render_template('supplierindex.html', orders_list=orders_list)
        except:
            return render_template('supplierindex.html', orders_list=orders_list)

    else:
        return redirect(url_for('supplierlogin'))
   

@app.route('/deleteOrder/<int:id>', methods=['POST'])
@login_required
def deleteorder(id):
     if current_user.is_authenticated:
        try:
            orders = Order.query.filter_by(id=id).first()
            products = Product.query.all()
            for product in products:
                if product.id == orders.product_id:
                    orders.status = 0
                    db.session.commit()
                    return redirect(url_for('supplierhome'))
        except:
            return redirect(url_for('supplierhome'))

        else:
            return redirect(url_for('login'))
        

@app.route('/deleteOrders/<int:id>', methods=['POST'])
@login_required
def deleteorders(id):
    if current_user.is_authenticated:
        order = Order.query.filter_by(id=id).first()
        db.session.delete(order)
        db.session.commit()
        return redirect(url_for('retrieveorder', idsite=True))
    else:
        return redirect(url_for('login'))

@app.route('/acceptOrder/<int:id>')
def acceptorder(id):
    if current_user.is_authenticated:
        try:
            orders = Order.query.filter_by(id=id).first()
            products = Product.query.all()
            for product in products:
                if product.id == orders.product_id:
                    product.stock += orders.orderstock
                    orders.status = 2
                    db.session.commit()
                    return redirect(url_for('supplierhome'))
        except:
            return redirect(url_for('supplierhome'))

    else:
        return redirect(url_for('login'))
    
@app.route('/rejectOrder/<int:id>')
def rejectorder(id):
    if current_user.is_authenticated:
        try:
            order = Order.query.filter_by(id=id).first()
            
            if order:
                order.status = 0
                db.session.commit()
            
            return redirect(url_for('supplierhome')) 
        except:
            return redirect(url_for('supplierhome'))  
    else:
        return redirect(url_for('login'))  



# ===================== Voucher =======================


@app.route('/voucherAdmin', methods=['GET', 'POST'])
@login_required
def retrievevoucher():
    if current_user.is_authenticated and current_user.isAdmin == True:
        voucher_list = []
        vouchers = Voucher.query.all()
        for voucher in vouchers:
            voucher_list.append(voucher)
        return render_template('voucherAdmin.html', voucher_list=voucher_list, adminStat=True)
    else:
        return redirect(url_for('login'))


@app.route('/createVoucher', methods=['GET', 'POST'])
@login_required
def createvoucher():
    if current_user.is_authenticated and current_user.isAdmin == True:
        form = VoucherForm()
        if form.validate_on_submit():
            voucher = Voucher(name=form.name.data, description=form.description.data, value=form.value.data,credit=form.credits.data, redeem_date=form.redeem_date.data,
                            expiry_date=form.expiry_date.data, image_file=form.image_file.data, isValid=True)
            db.session.add(voucher)
            db.session.commit()
            flash('New Voucher created!', 'success')
            return redirect(url_for('retrievevoucher'))
        return render_template('createVoucher.html', form=form, adminStat=True)
    else:
        return redirect(url_for('login'))

@app.route('/updateVoucher/<int:id>/', methods=['GET', 'POST'])
def updatevoucher(id):
    if current_user.is_authenticated and current_user.isAdmin == True:
        form = VoucherForm()
        if request.method == 'POST' and form.validate():
            voucher = Voucher.query.filter_by(id=id).first()
            voucher.name = form.name.data
            voucher.description = form.description.data
            voucher.value = form.value.data
            voucher.credit =  form.credits.data
            voucher.redeem_date = form.redeem_date.data
            voucher.expiry_date = form.expiry_date.data
            voucher.image_file = form.image_file.data
            db.session.commit()
            return redirect(url_for('retrievevoucher'))
        else:
            voucher = Voucher.query.filter_by(id=id).first()
            form.name.data = voucher.name
            form.description.data = voucher.description
            form.value.data = voucher.value
            form.credits.data = voucher.credit
            form.redeem_date.data = voucher.redeem_date
            form.expiry_date.data = voucher.expiry_date
            form.image_file.data = voucher.image_file
            return render_template('updateVoucher.html', form=form, voucherimage=voucher.image_file, adminStat=True, idsite=True)
    else:
        return redirect(url_for('login'))


@app.route('/deleteVoucher/<int:id>', methods=['POST'])
@login_required
def deletevoucher(id):
    voucher = Voucher.query.filter_by(id=id).first()
    db.session.delete(voucher)
    db.session.commit()
    return redirect(url_for('retrievevoucher'), idsite=True)

# ============ SERVICE ===============


@app.route('/serviceAdmin')
@login_required
def serviceadmin():
    if current_user.isAdmin:  # Ensure only admins can access this route
        feedback_list = Feedback.query.all()  # Retrieve all feedbacks from the database
        return render_template('serviceAdmin.html', feedback_list=feedback_list, adminStat=True)
    else:
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('home'))



@app.route('/deleteFeedback/<int:id>', methods=['POST'])
@login_required
def deletefeedback(id):
    feedback = Feedback.query.filter_by(id=id).first()
    db.session.delete(feedback)
    db.session.commit()
    return redirect(url_for('serviceadmin', idsite=True))

# ============= Validity =============


@app.route('/inventoryValidity/<int:id>', methods=['GET', 'POST'])
@login_required
def inventoryvalidity(id):
    suppliers = Supplier.query.all()
    supplier = Supplier.query.filter_by(id=id).first()
    supplier_list = []
    for person in suppliers:
        print(person.name)
        supplier_list.append(person)
    if supplier.isValid == True:
        print(supplier.name)
        supplier.isValid = False
        db.session.commit()
    elif supplier.isValid == False:
        print(supplier.isValid)
        supplier.isValid = True
        db.session.commit()
    return render_template('inventoryAdmin.html', adminStat=True, supplier_list=supplier_list, idsite=True)

@app.route('/voucherValidity/<int:id>', methods=['GET', 'POST'])
@login_required
def vouchervalidity(id):
    vouchers = Voucher.query.all()
    voucher = Voucher.query.filter_by(id=id).first()
    voucher_list = []
    for person in vouchers:
        print(person.name)
        voucher_list.append(person)
    if voucher.isValid == True:
        print(voucher.name)
        voucher.isValid = False
        db.session.commit()
    elif voucher.isValid == False:
        print(voucher.isValid)
        voucher.isValid = True
        db.session.commit()
    return render_template('voucherAdmin.html', adminStat=True, voucher_list=voucher_list, idsite=True)

@app.route('/productValidity/<int:id>', methods=['GET', 'POST'])
@login_required
def productvalidity(id):
    products = Product.query.all()
    product = Product.query.filter_by(id=id).first()
    product_list = []
    for person in products:
        print(person.name)
        product_list.append(person)
    if product.isValid == True:
        print(product.name)
        product.isValid = False
        db.session.commit()
    elif product.isValid == False:
        print(product.isValid)
        product.isValid = True
        db.session.commit()
    return render_template('productAdmin.html', adminStat=True, product_list=product_list, idsite=True)

@app.route('/donate', methods=['GET', 'POST'])
@login_required
def donate():
    from .organization import organizations  # Import the organizations dictionary

    # Populate organization choices dynamically
    org_choices = [(key, value['name']) for key, value in organizations.items()]
    form = DonateForm()
    form.organization.choices = org_choices

    if form.validate_on_submit():  # Ensure form is validated
        donation_amount = form.amount.data
        selected_org = form.organization.data

        # Redirect to the payment page
        return redirect(url_for(
            'donation_payment',
            amount=donation_amount,
            organization=selected_org
        ))

    # If the form is not submitted or validation fails, re-render the form
    return render_template('donate.html', form=form, organizations=organizations)

@app.route('/generate_qr', methods=['GET'])
@login_required
def generate_qr():
    from io import BytesIO
    import qrcode

    # Your PayNow mobile number and other details
    uen_or_mobile = "88185649"  # Your PayNow mobile number
    merchant_name = "ForACause"  # Merchant name
    merchant_city = "Singapore"  # Merchant city
    amount = request.args.get('amount', type=float)  # Donation amount
    reference = "Donation"  # Fixed payment reference

    # Validate input
    if not uen_or_mobile or not amount:
        return "Invalid QR code parameters", 400

    # Construct SGQR payload
    payload = (
        "000201"  # Payload format indicator
        "010211"  # Static QR code
        "26440014SG.PAYNOW"  # PayNow identifier
        f"01012021{len(uen_or_mobile):02}{uen_or_mobile}"  # Mobile number proxy
        "5303702"  # Currency (SGD = 702)
        f"54{len(f'{amount:.2f}'):02}{amount:.2f}"  # Amount
        "5802SG"  # Country
        f"59{len(merchant_name):02}{merchant_name}"  # Merchant name
        f"60{len(merchant_city):02}{merchant_city}"  # Merchant city
        f"62{len(reference)+4:02}01{len(reference):02}{reference}"  # Reference
        "6304"  # CRC checksum placeholder
    )

    # Calculate CRC checksum
    crc = calculate_crc(payload)
    payload += crc

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    # Save QR code to a buffer
    buffer = BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(buffer)
    buffer.seek(0)

    # Return the QR code as a PNG
    return send_file(buffer, mimetype='image/png')


@app.route('/donation/payment', methods=['GET', 'POST'])
@login_required
def donation_payment():
    from .organization import organizations

    # Retrieve donation details from query parameters
    donation_amount = request.args.get('amount', type=float)
    selected_org = request.args.get('organization')

    # Validate the organization
    if selected_org not in organizations:
        flash('Invalid organization selected. Please try again.', 'danger')
        return redirect(url_for('donate'))

    # Organization details
    organization_name = organizations[selected_org]['name']
    uen_or_mobile = "88185649"  # Registered PayNow mobile number
    reference = "Donation"  # Payment reference

    if request.method == 'POST':
        # Handle Stripe or PayNow confirmation
        payment_method = request.form.get('payment_method')

        if payment_method == 'stripe':
            # Redirect to Stripe Checkout
            return redirect(url_for(
                'create_checkout_session',
                amount=donation_amount,
                organization=selected_org,
            ))

        elif payment_method == 'paynow':
            flash("Please scan the QR code with your PayNow app to complete the payment.", "info")
            return redirect(url_for('donation_payment', amount=donation_amount, organization=selected_org))

        flash('Invalid payment method selected. Please try again.', 'danger')

    return render_template(
        'payment.html',
        organization_name=organization_name,
        donation_amount=donation_amount,
        uen_or_mobile=uen_or_mobile,
        reference=reference
    )


def calculate_crc(payload: str) -> str:
    """Calculate CRC16-CCITT checksum for SGQR."""
    crc = 0xFFFF
    polynomial = 0x1021

    for byte in payload.encode("utf-8"):
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ polynomial
            else:
                crc <<= 1
        crc &= 0xFFFF  # Ensure 16-bit

    return f"{crc:04X}"  # Return checksum in uppercase hex


@app.route('/create-checkout-session', methods=['GET'])
@login_required
def create_checkout_session():
    try:
        # Retrieve donation details
        amount = int(request.args.get('amount', type=float) * 100)  # Convert to cents
        organization_name = request.args.get('organization', 'ForACause')

        # Create Stripe Checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'sgd',
                        'product_data': {
                            'name': f'Donation to {organization_name}',
                        },
                        'unit_amount': amount,
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=url_for('payment_success', _external=True),
            cancel_url=url_for('payment_cancel', _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('donate'))


@app.route('/payment/success')
@login_required
def payment_success():
    flash("Your payment was successful! Thank you for your donation.", "success")
    return redirect(url_for('home'))


@app.route('/payment/cancel')
@login_required
def payment_cancel():
    flash("Your payment was canceled. Please try again.", "warning")
    return redirect(url_for('donate'))



@app.route('/chat', methods=['POST'])
@login_required
def chat():
    try:
        # Get user message from the request
        user_message = request.json.get('message', '').strip()
        if not user_message:
            return jsonify({"reply": "Message cannot be empty."}), 400

        # API configuration
        url = "https://free-chatgpt-api.p.rapidapi.com/chat-completion-one"
        querystring = {"prompt": user_message}
        headers = {
            "x-rapidapi-key": os.getenv("RAPIDAPI_KEY", "a26de8c9c7msh2f30c7ea2545caep18aa6bjsn7536d84ca8f2"),  # Replace with your valid API key
            "x-rapidapi-host": "free-chatgpt-api.p.rapidapi.com"
        }

        # Make the request
        response = requests.get(url, headers=headers, params=querystring)

        # Check response status
        if response.status_code == 200:
            data = response.json()
            reply = data.get("response", "No reply available.")
            return jsonify({"reply": reply})
        else:
            return jsonify({"reply": f"API error: {response.status_code} - {response.reason}"}), response.status_code

    except Exception as e:
        return jsonify({"reply": f"An unexpected error occurred: {str(e)}"}), 500


# ============ Volunteer ===============
@app.route('/volunteer')
@login_required
def volunteer():
    if current_user.isAdmin:
        flash('Admins cannot access this page!', 'danger')
        return redirect(url_for('home'))

    # Fetch signed-up event IDs for the current user
    signed_up_event_ids = {signup.event_id for signup in current_user.volunteer_events}

    # Get filter parameters from the request
    search_name = request.args.get('search_name', '')
    filter_date = request.args.get('filter_date', '')
    show_signed_up = request.args.get('show_signed_up', 'false') == 'true'

    # Fetch all events
    events = VolunteerEvent.query.all()

    # Apply filters
    if search_name:
        events = [event for event in events if search_name.lower() in event.name.lower()]
    
    if filter_date:
        filter_date = datetime.strptime(filter_date, '%Y-%m-%d').date()
        events = [event for event in events if event.date == filter_date]

    if show_signed_up:
        events = [event for event in events if event.id in signed_up_event_ids]

    return render_template('volunteer.html', events=events, signed_up_event_ids=signed_up_event_ids)


@app.route('/volunteer/<int:event_id>', methods=['GET', 'POST'])
@login_required
def confirm_volunteer_event(event_id):
    event = VolunteerEvent.query.get_or_404(event_id)

    if request.method == 'POST':
        # Check if user is already signed up
        existing_signup = UserVolunteer.query.filter_by(
            user_id=current_user.id, event_id=event_id
        ).first()
        if existing_signup:
            flash('You are already signed up for this event!', 'warning')
        else:
            # Add new signup
            new_signup = UserVolunteer(
                user_id=current_user.id,
                event_id=event_id,
                sign_up_date=datetime.utcnow()
            )
            db.session.add(new_signup)
            db.session.commit()
            flash('You have successfully signed up!', 'success')

        return redirect(url_for('volunteer'))

    return render_template('confirm_volunteer.html', event=event)

def get_address_from_coordinates(lat, lon):
    api_key = 'AIzaSyCcL6Ot97Y8Gtk0-heploLjEebJOUgEJoo'
    url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={api_key}'
    response = requests.get(url)
    data = response.json()

    if data['status'] == 'OK':
        # Get the formatted address from the API response
        address = data['results'][0]['formatted_address']
        return address
    else:
        return "Address not found"
    

@app.route('/map_view', methods=['GET'])
@login_required
def map_view():
    # Fetch all events from the database
    events = VolunteerEvent.query.all()

    # Get the signed-up events for the current user
    signed_up_event_ids = {signup.event_id for signup in current_user.volunteer_events}

    # Prepare event data with the signed-up flag
    events_data = [
        {
            'id': event.id,
            'name': event.name,
            'description': event.description,
            'latitude': event.latitude,
            'longitude': event.longitude,
            'date': event.date.strftime('%Y-%m-%d') if event.date else 'Not available',
            'category': event.category if event.category else 'Not available',
            'address': event.address if event.address else 'Not available',
            'is_signed_up': event.id in signed_up_event_ids
        }
        for event in events
    ]

    # Serialize the events data to JSON for the map
    events_data_json = json.dumps(events_data)

    return render_template(
        'map_view.html',
        events_data=events_data_json,  # This will be used for the map markers
        events=events_data,  # This will be used for the list view
        api_key=app.config['GOOGLE_MAPS_API_KEY']
    )

@app.route("/calendar")
@login_required
def calendar_view():
    user_events = (
        db.session.query(VolunteerEvent.id, VolunteerEvent.name, VolunteerEvent.date)
        .join(UserVolunteer, UserVolunteer.event_id == VolunteerEvent.id)
        .filter(UserVolunteer.user_id == current_user.id)
        .all()
    )

    events = [
        {"id": event.id, "title": event.name, "start": event.date.isoformat()} 
        for event in user_events
    ]

    return render_template("calendar.html", events=events)

@app.route("/event/<int:event_id>")
@login_required
def event_detail(event_id):
    # Fetch the event details from the database using the event ID
    event = VolunteerEvent.query.get_or_404(event_id)

    # Render the event detail page and pass the event data
    return render_template("event_detail.html", event=event)

@app.route('/create_volunteer_event', methods=['GET', 'POST'])
@login_required
def create_volunteer_event():
    if not current_user.isAdmin:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        category = request.form['category']
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        image_file = None

        if 'image_file' in request.files and request.files['image_file'].filename != '':
            file = request.files['image_file']
            image_file = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_file))

        # Get the address from the latitude and longitude
        address = get_address_from_coordinates(latitude, longitude)

        # Create the new event
        new_event = VolunteerEvent(
            name=name,
            description=description,
            date=date,
            category=category,
            image_file=image_file, 
            latitude=latitude,
            longitude=longitude,
            address=address  
        )
        db.session.add(new_event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('create_volunteer_event'))

    events = VolunteerEvent.query.all()
    signups = UserVolunteer.query.all()

    return render_template(
        'create_volunteer_event.html',
        adminStat=True,
        events=events,
        signups=signups
    )


@app.route('/manage_volunteer_event')
@login_required
def manage_volunteer_event():
    if not current_user.isAdmin:
        abort(403)  # Restrict access to admins only
    
    events = VolunteerEvent.query.all()
    signups = UserVolunteer.query.all()
    return render_template(
        'create_volunteer_event.html',
        events=events,
        signups=signups
    )

@app.route('/edit_volunteer_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_volunteer_event(event_id):
    event = VolunteerEvent.query.get_or_404(event_id)
    
    if request.method == 'POST':
        event.name = request.form['name']
        event.description = request.form['description']
        event.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()  # Convert to date object
        event.category = request.form['category']
        
        # Update event image if a new one is uploaded
        if 'image_file' in request.files:
            image_file = request.files['image_file']
            if image_file:
                # Save the new image, or handle it according to your setup (e.g., store it in a static folder)
                filename = secure_filename(image_file.filename)
                image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                event.image = filename
        
        # Update event location (latitude and longitude)
        event.latitude = request.form['latitude']
        event.longitude = request.form['longitude']

        event.address = get_address_from_coordinates(event.latitude, event.longitude)
        
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('create_volunteer_event', event_id=event.id))  # Redirect to event detail page after update

    return render_template('edit_volunteer_event.html', event=event)

@app.route('/delete_volunteer_event/<int:event_id>', methods=['POST'])
@login_required
def delete_volunteer_event(event_id):
    if not current_user.isAdmin:
        abort(403)

    event = VolunteerEvent.query.get_or_404(event_id)

    # Delete related user signups
    UserVolunteer.query.filter_by(event_id=event_id).delete()
    
    db.session.delete(event)
    db.session.commit()
    flash('Volunteer event deleted successfully!', 'success')
    return redirect(url_for('create_volunteer_event'))

@app.route('/confirm_volunteer/<int:event_id>', methods=['GET', 'POST'])
@login_required
def confirm_volunteer(event_id):
    if current_user.isAdmin:
        flash('Admins cannot volunteer for events!', 'danger')
        return redirect(url_for('home'))

    event = VolunteerEvent.query.get_or_404(event_id)

    if request.method == 'POST':
        # Check if the user is already signed up
        existing_signup = UserVolunteer.query.filter_by(user_id=current_user.id, event_id=event.id).first()

        if existing_signup:
            flash('You are already signed up for this event!', 'warning')
        else:
            # Add user signup
            signup = UserVolunteer(user_id=current_user.id, event_id=event.id)
            db.session.add(signup)
            db.session.commit()
            flash(f'You have successfully signed up for {event.name}!', 'success')

        return redirect(url_for('volunteer'))

    return render_template('confirm_volunteer.html', event=event)

@app.route('/mark_attended/<int:event_id>/<int:user_id>', methods=['POST'])
@login_required
def mark_attended(event_id, user_id):
    if not current_user.isAdmin:
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('home'))

    # Fetch the signup record
    signup = UserVolunteer.query.filter_by(event_id=event_id, user_id=user_id).first()
    if not signup:
        flash('Signup record not found!', 'danger')
        return redirect(url_for('create_volunteer_event'))

    # Mark as attended
    signup.attended = True
    db.session.commit()
    flash(f'User {signup.user.username} marked as attended for {signup.event.name}.', 'success')
    return redirect(url_for('create_volunteer_event'))


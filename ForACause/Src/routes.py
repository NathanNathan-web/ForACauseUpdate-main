from datetime import date
from flask import render_template, url_for, flash, redirect, request, session
from Src.forms import RegistrationForm, LoginForm, UpdateOneUserForm,UpdateUserForm,SupplierForm,RedeemVoucherForm,TopUpForm, VoucherForm, FeedbackForm, ForgetPassword, ResetPassword,ProductForm, OrderForm,CartForm
from Src.models import Donation, User, Supplier, Voucher, Feedback,Product,Order,Cart,RedeemedVouchers
from Src import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os
from flask_babel import _
from Src.forms import DonateForm
import http.client  # Import for chatbot API
import json  # Required for JSON serialization and deserialization
from flask import render_template, url_for, flash, redirect, request, session, jsonify
import logging
import requests
import qrcode
from io import BytesIO
from flask import send_file
import stripe
from datetime import datetime
stripe.api_key = "sk_test_51QkUOjJw6qEGWv892rSo4scTB2rqEM8PmzwgpEBjyhW9tDnXRmo3LuUEzmSJoHqyMbOphD8154ZSeB3UMTNqAGxL00OlAkeMM9"
import timedelta
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
        redeemvoucher_list = []
        image_file = url_for('static', filename='images/' + current_user.image_file)
        user = User.query.filter_by(id=current_user.id).first()
        redeemvouchers = RedeemedVouchers.query.filter_by(user_id=current_user.id).all()
        for redeemvoucher in redeemvouchers:
            redeemvoucher_list.append(redeemvoucher)
        # Pass app or app.config['LANGUAGES'] to the template
        return render_template('account.html', image_file=image_file, user=user, redeemvoucher_list=redeemvoucher_list, languages=app.config['LANGUAGES'])
    else:
        return render_template('login.html')

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


@app.route('/product')
def product():
    products_list = []
    products = Product.query.all()
    for product in products:
        products_list.append(product)
    return render_template('product.html', products_list=products_list)


@app.route('/productDetails/<int:id>', methods=['GET','POST'])
def productdetails(id):
    if current_user.is_authenticated:
        product = Product.query.filter_by(id=id).first()
        cart = Cart.query.filter_by(product_id=id).first()
        form = CartForm()
        if form.validate_on_submit:
            if form.quantity.data > 0 and form.quantity.data <= product.stock:
                quantity = form.quantity.data
                current_user.add_to_cart(product,quantity)
                return redirect(url_for('cart'))
            else:
                flash('Quantity must be within the stock amount', 'warning')
                return render_template('productdetails.html', product = product, idsite = True, form=form)
                
        else:
            flash('Quantity need to be a valid number', 'warning')
        return render_template('productdetails.html', product = product, idsite = True, form=form)
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
    carts_list = []
    vouchers_list = []
    if current_user.is_authenticated:
        redeemvouchers = RedeemedVouchers.query.filter_by(user_id=current_user.id).all()
        for redeemvoucher in redeemvouchers:
            vouchers_list.append(redeemvoucher)
        total = 0
        carts = Cart.query.filter_by(user_id=current_user.id).all()

        for cart in carts:
            total += cart.quantity * cart.product.price
            carts_list.append(cart)
            print(cart)
        session['total'] = total
        return render_template('shoppingcart.html', carts=carts, total=total, carts_list = carts_list, vouchers_list = vouchers_list)
    else:
        return redirect(url_for('login'))


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
@app.route('/checkOut')
def checkout():
    if current_user.is_authenticated:
        if current_user.balance >= session['total']:
            carts = Cart.query.filter_by(user_id=current_user.id).all()
            for cart in carts:
                db.session.delete(cart)
                db.session.commit()
            current_user.balance -= session['total']
            flash('You have successfully checked out!')
            return redirect(url_for('home'))
        else:
            flash('Not even balance to checkout!')
            return redirect(url_for('cart'))
    else:
        return redirect(url_for('login'))

# =================================  VOUCHER ==================================
@app.route('/voucher', methods=['GET'])
def voucher():
    search_query = request.args.get('search', '')  # Get the search term from query parameters

    if search_query:
        # Filter vouchers based on the search query
        vouchers_list = Voucher.query.filter(
            (Voucher.name.ilike(f'%{search_query}%')) |
            (Voucher.description.ilike(f'%{search_query}%')) |
            (Voucher.id.ilike(f'%{search_query}%'))
        ).all()
    else:
        # Fetch all vouchers if no search query
        vouchers_list = Voucher.query.all()

    return render_template('voucher.html', vouchers_list=vouchers_list, search_query=search_query)



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

@app.route('/productAdmin')
@login_required
def productadmin():
    if current_user.is_authenticated and current_user.isAdmin == True:
        product_list = []
        products = Product.query.all()
        orders_list = []
        suppliercount = 0
        for product in products:
            orders = Order.query.filter_by(product_id=product.id)
            orders_list.append(orders)
            product_list.append(product)
        return render_template('productAdmin.html', product_list=product_list, adminStat = True, orders_list=orders_list, suppliercount = suppliercount)
    else:
        return redirect(url_for('login'))

@app.route('/createProduct', methods=['GET', 'POST'])
@login_required
def createProduct():
    if current_user.is_authenticated and current_user.isAdmin == True:
        form = ProductForm()
        if form.validate_on_submit():
            product = Product(name=form.name.data, description=form.description.data, category=category(form.category.data), country=form.country.data,price=form.price.data, stock=0, image_file=form.image_file.data, isValid=True)
            db.session.add(product)
            db.session.commit()
            flash('New Product created!', 'success')
            return redirect(url_for('productadmin'))
        return render_template('createProduct.html',form=form)
    else:
        return redirect(url_for('login'))

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
def createsupplier():
    if current_user.is_authenticated and current_user.isAdmin == True:
        form = SupplierForm()
        if form.validate_on_submit():
            if form.phone.data[0] == '8' or form.phone.data[0] == '9' or form.phone.data[0] == '6' and form.name.data.isalpha() == True:
                try:
                    supplier = Supplier(name=form.name.data, email=form.email.data, password=form.password.data, phone=form.phone.data, company=form.company.data,
                                        address=form.address.data, country=form.country.data, image_file=form.image_file.data, isValid=True)
                    db.session.add(supplier)
                    db.session.commit()
                    flash('New supplier created!', 'success')
                    return redirect(url_for('inventoryadmin'))
                except:
                    db.session.rollback()
                    flash('Supplier exist, try new name')
            else:
                flash(
                    'Update supplier failed, Phone number must start with 8 , 9 or 6 or Name cannot contain number', 'danger')
        return render_template('createSupplier.html', form=form, adminStat=True)
    else:
        return render_template('login.html')


@app.route('/updateSupplier/<int:id>/', methods=['GET', 'POST'])
def updatesupplier(id):
    if current_user.is_authenticated and current_user.isAdmin == True:
        form = SupplierForm()
        if request.method == 'POST' and form.validate():
            supplier = Supplier.query.filter_by(id=id).first()
            if form.phone.data[0] == '8' or form.phone.data[0] == '9' or form.phone.data[0] == '6' and form.name.data.isalpha() == True:
                supplier.name = form.name.data
                supplier.email = form.email.data
                supplier.phone = form.phone.data
                supplier.company = form.company.data
                supplier.address = form.address.data
                supplier.country = form.country.data
                supplier.image_file = form.image_file.data
                supplier.isValid = form.isValid.data
                db.session.commit()
                flash('Update supplier success!', 'success')
                return redirect(url_for('inventoryadmin', idsite=True))
            else:
                flash(
                    'Update supplier failed, Phone number must start with 8 , 9 or 6 or Name cannot contain number', 'danger')
                return render_template('updateSupplier.html', form=form, supplierimage=supplier.image_file, idsite=True)
        else:
            supplier = Supplier.query.filter_by(id=id).first()
            form.name.data = supplier.name
            form.email.data = supplier.email
            form.phone.data = supplier.phone
            form.company.data = supplier.company
            form.address.data = supplier.address
            form.country.data = supplier.country
            form.image_file.data = supplier.image_file
            return render_template('updateSupplier.html', form=form, supplierimage=supplier.image_file, idsite=True)
    else:
        return render_template('login.html')


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
        return render_template('createOrder.html', form=form, supplier=supplier, idsite=True, product_list = product_list)
    else:
        return redirect(url_for('login'))

@app.route('/retrieveOrder')
def retrieveorder():
    if current_user.is_authenticated and current_user.isAdmin == True:
        order_list = []
        orders = Order.query.all()
        for order in orders:
            order_list.append(order)
        return render_template('retrieveOrder.html', order_list=order_list)
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
    






# ===================== Voucher =======================



@app.route('/voucherAdmin', methods=['GET', 'POST'])
@login_required
def retrievevoucher():
    if current_user.is_authenticated and current_user.isAdmin:
        # Fetch all vouchers
        voucher_list = []
        vouchers = Voucher.query.all()
        for voucher in vouchers:
            voucher_list.append(voucher)

        # Fetch expired vouchers
        today = datetime.today().date()
        expired_vouchers = Voucher.query.filter(Voucher.expiry_date < today).all()
        notifications = [
            f"Voucher '{voucher.name}' expired on {voucher.expiry_date}."
            for voucher in expired_vouchers
        ]

        # Pass voucher list and notifications to the template
        return render_template(
            'voucherAdmin.html',
            voucher_list=voucher_list,
            adminStat=True,
            notifications=notifications
        )
    else:
        return redirect(url_for('login'))

@app.route('/toggleVoucherStatus/<int:id>', methods=['POST'])
@login_required
def toggle_voucher_status(id):
    if not current_user.is_authenticated or not current_user.isAdmin:
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    voucher = Voucher.query.get(id)
    if not voucher:
        return jsonify({"success": False, "message": "Voucher not found"}), 404

    # Toggle the status between 'valid' and 'non-valid'
    voucher.status = 'non-valid' if voucher.status == 'valid' else 'valid'
    db.session.commit()

    return jsonify({"success": True, "new_status": voucher.status})


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
    if voucher:
        db.session.delete(voucher)
        db.session.commit()
        flash('Voucher deleted successfully!', 'success')
    else:
        flash('Voucher not found.', 'danger')
    return redirect(url_for('retrievevoucher'))


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
    from Src.organization import organizations  # Import the organizations dictionary

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
    from Src.organization import organizations

    # Retrieve donation details from query parameters
    donation_amount = request.args.get('amount', type=float)
    selected_org = request.args.get('organization')

    # Validate the organization
    if selected_org not in organizations:
        flash('Invalid organization selected. Please try again.', 'danger')
        return redirect(url_for('donate'))

    # Organization details
    organization_name = organizations[selected_org]['name']
    reference = "Donation"  # Payment reference

    if request.method == 'POST':
        # Handle payment method selection
        payment_method = request.form.get('payment_method')

        if payment_method == 'stripe':
            # Redirect to Stripe Checkout
            return redirect(url_for(
                'create_checkout_session',
                amount=donation_amount,
                organization=selected_org,
            ))

        elif payment_method == 'paynow':
            # Simulate PayNow payment success
            flash("Your PayNow donation has been successfully processed!", "success")
            return redirect(url_for(
                'donation_success',
                amount=donation_amount,
                organization=selected_org
            ))

        flash('Invalid payment method selected. Please try again.', 'danger')

    return render_template(
        'payment.html',
        organization_name=organization_name,
        donation_amount=donation_amount,
        reference=reference
    )
@app.route('/donation/success', methods=['GET'])
@login_required
def donation_success():
    donation_amount = request.args.get('amount', type=float)
    organization_name = request.args.get('organization')

    return render_template(
        'donation.success.html',
        donation_amount=donation_amount,
        organization_name=organization_name
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
        return jsonify({"reply": f"An unexpected error occurred: {str(e)}"}), 
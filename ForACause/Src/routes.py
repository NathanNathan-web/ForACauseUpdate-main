from datetime import date
from flask import render_template, url_for, flash, redirect, request, session, jsonify,Response
from Src.forms import RegistrationForm, LoginForm, UpdateOneUserForm,UpdateUserForm,SupplierForm,RedeemVoucherForm,TopUpForm, VoucherForm, FeedbackForm, ForgetPassword, ResetPassword,ProductForm, OrderForm,CartForm
from Src.models import User, Supplier, Voucher, Feedback,Product,Order,Cart,RedeemedVouchers,VolunteerEvent,UserVolunteer,Wishlist,EventReview,db
from Src import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os
from flask_babel import _
from datetime import datetime
from collections import Counter
from sqlalchemy import func  # Import func for SQL functions
from sqlalchemy.sql import desc
import csv



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
        user = User.query.get(current_user.id)

        # Fetch user volunteering history
        user_volunteer_events = UserVolunteer.query.filter_by(user_id=current_user.id).all()

        # Prepare donation and volunteering history
        volunteering_history = [
            {
                "date": volunteer.sign_up_date.strftime('%Y-%m-%d'),
                "type": "Volunteering",
                "details": volunteer.event.name,
                "status": "Completed" if volunteer.attended else "Pending",
            }
            for volunteer in user_volunteer_events
        ]

        # Fetch user vouchers
        user_vouchers = RedeemedVouchers.query.filter_by(user_id=current_user.id).all()

        # Prepare voucher data
        voucher_data = [
            {
                "id": voucher.voucher.id,
                "value": voucher.voucher.value,
                "expiry_date": voucher.voucher.expiry_date.strftime('%Y-%m-%d'),
                "image_file": voucher.voucher.image_file,
                "status": "Active" if voucher.status == "active" else "Expired",
            }
            for voucher in user_vouchers
        ]

        # Pass data to the template
        return render_template(
            'account.html',
            user=user,
            donation_volunteering_history=volunteering_history,
            user_vouchers=voucher_data,
            languages=app.config['LANGUAGES'],
        )
    else:
        return redirect(url_for('login'))


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

@app.route('/service')
def service():
    return render_template('service.html')


# ===================================== Admin =====================================

@app.route('/accountadmin', methods=['GET'])
@login_required
def accountadmin():
    if current_user.is_authenticated and current_user.isAdmin:
        search_filter = request.args.get('search_filter', '').strip()

        # Start with all users
        query = User.query

        # Apply filter if provided
        if search_filter:
            query = query.filter(
                (User.username.ilike(f"%{search_filter}%")) |
                (User.email.ilike(f"%{search_filter}%"))
            )

        # Fetch the filtered users
        user_list = query.all()

        # Get the list of hidden users' IDs from the session
        hidden_users = session.get('hidden_users', [])

        # Filter out the hidden users
        visible_users = [user for user in user_list if user.id not in hidden_users]

        return render_template('accountAdmin.html', adminStat=True, user_list=visible_users)
    else:
        return redirect(url_for('login'))







@app.route('/deleteUser/<int:id>', methods=['POST'])
@login_required
def deleteuser(id):
    # We need to retrieve the user by ID, which is stored in the session
    user = User.query.filter_by(id=id).first()

    if user:
        # Add the user ID to the "hidden" list in the session
        if 'hidden_users' not in session:
            session['hidden_users'] = []

        session['hidden_users'].append(id)  # Add this user to the hidden list
        session.modified = True  # Mark session as modified

    return redirect(url_for('accountadmin'))



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
    feedback_list = []
    feedbacks = Feedback.query.all()
    for feedback in feedbacks:
        feedback_list.append(feedback)
    return render_template('serviceAdmin.html', feedback_list=feedback_list, adminStat=True)


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

# ============ Volunteer ===============
@app.route('/volunteer')
@login_required
def volunteer():
    if current_user.isAdmin:
        flash('Admins cannot access this page!', 'danger')
        return redirect(url_for('home'))

    # Fetch signed-up event IDs for the current user
    signed_up_event_ids = {signup.event_id for signup in current_user.user_volunteers}

    # Fetch wishlist event IDs for the current user
    wishlisted_event_ids = {item.event_id for item in current_user.wishlist_items}

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

    return render_template(
        'volunteer.html',
        events=events,
        signed_up_event_ids=signed_up_event_ids,
        wishlisted_event_ids=wishlisted_event_ids
    )



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

from sqlalchemy import func

@app.route('/create_volunteer_event', methods=['GET', 'POST'])
@login_required
def create_volunteer_event():
    if not current_user.isAdmin:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        try:
            name = request.form['name']
            description = request.form['description']
            date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            category = request.form['category']
            image_file = None

            if 'image_file' in request.files and request.files['image_file'].filename != '':
                file = request.files['image_file']
                image_file = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_file))

            new_event = VolunteerEvent(
                name=name,
                description=description,
                date=date,
                category=category,
                image_file=image_file
            )
            db.session.add(new_event)
            db.session.commit()
            flash('Event created successfully!', 'success')
        except Exception as e:
            flash(f"Error creating event: {str(e)}", "danger")
        return redirect(url_for('create_volunteer_event'))

    # Fetch all events
    events = VolunteerEvent.query.all()

    # Fetch all user signups
    signups = UserVolunteer.query.all()

    # Fetch event reviews with pagination (5 per page)
    page = request.args.get('page', 1, type=int)
    reviews = EventReview.query.order_by(EventReview.created_at.desc()).paginate(page=page, per_page=5)

    # Fetch the top volunteer (user with the most signups)
    top_volunteer_query = (
        db.session.query(User, func.count(UserVolunteer.id).label('signup_count'))
        .join(UserVolunteer, User.id == UserVolunteer.user_id)
        .group_by(User.id)
        .order_by(func.count(UserVolunteer.id).desc())
        .first()
    )

    top_volunteer = {
        'username': top_volunteer_query[0].username if top_volunteer_query else 'No Volunteers',
        'signup_count': top_volunteer_query[1] if top_volunteer_query else 0
    }

    # Fetch the top 5 volunteers
    top_volunteers_query = (
        db.session.query(User, func.count(UserVolunteer.id).label('signup_count'))
        .join(UserVolunteer, User.id == UserVolunteer.user_id)
        .group_by(User.id)
        .order_by(func.count(UserVolunteer.id).desc())
        .limit(5)
    )

    top_volunteers = [
        {'username': volunteer[0].username, 'signup_count': volunteer[1]} for volunteer in top_volunteers_query
    ]

    # Prepare event signup data for the pie chart
    event_data_query = (
        db.session.query(VolunteerEvent.name, func.count(UserVolunteer.id).label('signup_count'))
        .join(UserVolunteer, VolunteerEvent.id == UserVolunteer.event_id)
        .group_by(VolunteerEvent.id)
        .order_by(func.count(UserVolunteer.id).desc())
    )

    event_data = {event[0]: event[1] for event in event_data_query}

    return render_template(
        'create_volunteer_event.html',
        events=events,
        signups=signups,
        reviews=reviews,  # ✅ Add this line
        top_volunteer=top_volunteer,
        top_volunteers=top_volunteers,
        event_data=event_data
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
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('create_volunteer_event'))
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

@app.route('/dashboard')
def dashboard():
    # Top volunteer
    signup_counts = db.session.query(User.username, func.count(Signup.id)).join(Signup).group_by(User.username).all()
    top_volunteer = max(signup_counts, key=lambda x: x[1])

    # Event signup counts
    event_counts = db.session.query(Event.name, func.count(Signup.id)).join(Signup).group_by(Event.name).all()
    event_data = dict(event_counts)

    return render_template(
        'your_template.html',
        top_volunteer={'username': top_volunteer[0], 'signup_count': top_volunteer[1]},
        event_data=event_data
    )

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Debug: Check user and associated user_volunteer entries
    print(f"Deleting user: {user.id}, {user.username}")
    user_volunteer_entries = UserVolunteer.query.filter_by(user_id=user_id).all()
    print(f"Associated UserVolunteer entries: {user_volunteer_entries}")

    # Handle deletion logic
    try:
        UserVolunteer.query.filter_by(user_id=user_id).delete()
        Wishlist.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()
        flash(f"User {user.username} and associated data deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error during deletion: {e}")
        flash("An error occurred while deleting the user.", "danger")

    return redirect(url_for('accountadmin'))


@app.route('/export_users', methods=['GET'])
@login_required
def export_users():
    if not current_user.isAdmin:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('home'))

    # Fetch all user data
    users = User.query.all()

    # Prepare CSV data
    def generate_csv():
        data = [
            ['User ID', 'Username', 'Email', 'Password', 'Phone', 'Address', 'Secret Question', 'Balance', 'Credit']
        ]
        for user in users:
            data.append([
                user.id, 
                user.username, 
                user.email, 
                user.password, 
                user.phone, 
                user.address, 
                user.secretQn, 
                user.balance, 
                user.credit
            ])
        for row in data:
            yield ','.join(map(str, row)) + '\n'

    # Create and return CSV response
    return Response(
        generate_csv(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=users_data.csv'}
    )

@app.route('/export_events', methods=['GET'])
@login_required
def export_events():
    if not current_user.isAdmin:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('home'))

    events = VolunteerEvent.query.all()

    def generate_csv():
        data = [['Name', 'Category', 'Description', 'Date']]
        for event in events:
            data.append([event.name, event.category, event.description, event.date])
        for row in data:
            yield ','.join(map(str, row)) + '\n'

    return Response(
        generate_csv(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=events.csv'}
    )

@app.route('/export_user_signups', methods=['GET'])
@login_required
def export_user_signups():
    if not current_user.isAdmin:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('home'))

    # Fetch all user signups
    signups = UserVolunteer.query.all()

    # Debugging: Print the results to see if there are signups
    for signup in signups:
        print(f"User: {signup.user.username}, Event: {signup.event.name}, Date: {signup.sign_up_date}, Attended: {signup.attended}")

    def generate_csv():
        data = [['User', 'Email', 'Event', 'Sign-Up Date', 'Attended']]
        for signup in signups:
            data.append([
                signup.user.username,
                signup.user.email,
                signup.event.name,
                signup.sign_up_date.strftime('%Y-%m-%d %H:%M:%S'),
                'Yes' if signup.attended else 'No',
            ])
        for row in data:
            yield ','.join(map(str, row)) + '\n'

    return Response(
        generate_csv(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=user_signups.csv'}
    )

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from Src import db
from Src.models import Wishlist, VolunteerEvent  # Import Wishlist and other required models

@app.route('/add_to_wishlist/<int:event_id>', methods=['POST'])
@login_required
def add_to_wishlist(event_id):
    existing_wishlist_item = Wishlist.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if not existing_wishlist_item:
        wishlist_item = Wishlist(user_id=current_user.id, event_id=event_id)
        db.session.add(wishlist_item)
        db.session.commit()
    flash("Event added to your wishlist!", "success")
    return redirect(url_for('volunteer'))


@app.route('/wishlist')
@login_required
def wishlist():
    wishlisted_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    wishlisted_events = [item.event for item in wishlisted_items] if wishlisted_items else []

    # Debugging
    print("Wishlisted Events:", wishlisted_events)
    
    return render_template('wishlist.html', wishlisted_events=wishlisted_events)

@app.route('/remove_from_wishlist/<int:event_id>', methods=['POST'])
@login_required
def remove_from_wishlist(event_id):
    wishlist_item = Wishlist.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if wishlist_item:
        db.session.delete(wishlist_item)
        db.session.commit()
    flash("Event removed from your wishlist!", "success")
    return redirect(url_for('volunteer'))

@app.route('/submit_review/<int:event_id>', methods=['POST'])
@login_required
def submit_review(event_id):
    event = VolunteerEvent.query.get_or_404(event_id)
    rating = request.form.get('rating')
    feedback = request.form.get('feedback')

    if not rating or int(rating) < 1 or int(rating) > 5:
        flash("Invalid rating. Please provide a rating between 1 and 5.", "danger")
        return redirect(url_for('event_reviews', event_id=event_id))

    # Check if the user has already submitted a review for this event
    existing_review = EventReview.query.filter_by(event_id=event_id, user_id=current_user.id).first()
    if existing_review:
        flash("You have already reviewed this event.", "warning")
        return redirect(url_for('event_reviews', event_id=event_id))

    # Save the review
    review = EventReview(event_id=event.id, user_id=current_user.id, rating=int(rating), feedback=feedback)
    db.session.add(review)
    db.session.commit()
    flash("Your review has been submitted successfully!", "success")
    return redirect(url_for('event_reviews', event_id=event_id))



@app.route('/event_reviews/<int:event_id>')
def event_reviews(event_id):
    page = request.args.get('page', 1, type=int)
    event = VolunteerEvent.query.get_or_404(event_id)

    # Fetch all reviews for the event
    reviews = (
        EventReview.query.filter_by(event_id=event_id)
        .order_by(EventReview.created_at.desc())
        .paginate(page=page, per_page=5)
    )

    # Fetch the most useful review (highest likes - dislikes)
    most_useful_review = (
        EventReview.query.filter_by(event_id=event_id)
        .order_by((EventReview.likes - EventReview.dislikes).desc())
        .first()
    )

    return render_template(
        'event_reviews.html',
        event=event,
        reviews=reviews,
        most_useful_review=most_useful_review,
    )

@app.route('/api/review/<int:review_id>/thumbs-up', methods=['POST'])
def thumbs_up(review_id):
    review = EventReview.query.get_or_404(review_id)
    review.likes += 1
    db.session.commit()
    return jsonify({'success': True, 'new_likes': review.likes})

@app.route('/api/review/<int:review_id>/thumbs-down', methods=['POST'])
def thumbs_down(review_id):
    review = EventReview.query.get_or_404(review_id)
    review.dislikes += 1
    db.session.commit()
    return jsonify({'success': True, 'new_dislikes': review.dislikes})


@app.route('/api/filter-reviews', methods=['GET'])
def filter_reviews():
    filter_type = request.args.get('filter')  # Get filter type ('highest' or 'lowest')

    # Handle the filtering
    if filter_type == 'highest':
        reviews = EventReview.query.order_by(EventReview.rating.desc()).all()
    elif filter_type == 'lowest':
        reviews = EventReview.query.order_by(EventReview.rating.asc()).all()
    else:
        reviews = EventReview.query.all()  # Default: return all reviews

    # Prepare the reviews for the response
    reviews_list = [{
        'id': review.id,
        'user': review.user.username,
        'rating': review.rating,
        'feedback': review.feedback,
        'likes': review.likes,
        'dislikes': review.dislikes,
        'created_at': review.created_at.strftime('%d %b %Y')
    } for review in reviews]

    return jsonify({'reviews': reviews_list})


@app.route('/quiz')
def quiz():
    return render_template('quiz.html')


from flask import session, redirect, url_for

@app.route('/hideUser/<int:user_id>', methods=['POST'])
@login_required
def hideuser(user_id):
    # Initialize the hidden_users list in session if it doesn't exist
    if 'hidden_users' not in session:
        session['hidden_users'] = []

    # Add the user's ID to the hidden_users list in the session
    session['hidden_users'].append(user_id)
    session.modified = True  # Mark session as modified to save

    return redirect(url_for('accountadmin'))

from datetime import date
from flask import render_template, url_for, flash, redirect, request, session
from .forms import RegistrationForm, LoginForm, UpdateOneUserForm,UpdateUserForm,SupplierForm,RedeemVoucherForm,TopUpForm, VoucherForm, FeedbackForm, ForgetPassword, ResetPassword,ProductForm, OrderForm,CartForm, DonationItemForm
from .models import User, Supplier, Voucher, Feedback,Product,Order,Cart,RedeemedVouchers,DonateItem
from . import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os

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
        donateitem_list = []
        
        image_file = url_for('static', filename='images/' + current_user.image_file)
        
        user = User.query.filter_by(id=current_user.id).first()
        redeemvouchers = RedeemedVouchers.query.filter_by(user_id=current_user.id).all()
        donateitems = DonateItem.query.filter_by(user_id=current_user.id).all()
        
        for redeemvoucher in redeemvouchers:
            redeemvoucher_list.append(redeemvoucher)
        
        for donateitem in donateitems:
            if donateitem.image_file:
                donateitem.image_path = url_for('static', filename='uploads/' + donateitem.image_file)
            else:
                donateitem.image_path = None
            donateitem_list.append(donateitem)
        
        return render_template(
            'account.html',
            image_file=image_file,
            user=user,
            redeemvoucher_list=redeemvoucher_list,
            donateitems=donateitem_list
        )
    else:
        return render_template('login.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/donateItem', methods=['GET', 'POST'])
@login_required
def donateItem():
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

    return redirect(url_for('donateitemadmin'))

@app.route('/deleteDonationItem/<int:id>', methods=['POST'])
def deletedonationitem(id):
    item = DonateItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('donateitemadmin'))

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
        order_list = []
        orders = Order.query.all()
        for order in orders:
            order_list.append(order)
        return render_template('retrieveOrder.html', adminStat=True, order_list=order_list)
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

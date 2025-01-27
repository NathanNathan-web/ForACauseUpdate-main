from datetime import date, datetime
from flask import render_template, url_for, flash, redirect, request, session
from .forms import RegistrationForm, LoginForm, UpdateOneUserForm,UpdateUserForm,SupplierForm,RedeemVoucherForm,TopUpForm, VoucherForm, FeedbackForm, ForgetPassword, ResetPassword,ProductForm, OrderForm,CartForm
from .models import User, Supplier, Voucher, Feedback,Product,Order,Cart,RedeemedVouchers
from . import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os
from flask_babel import _
import qrcode
import pytz






@app.route('/favouritepage')
def favouritepage():
    # Logic for the favourites page
    return render_template('favouritepage.html')


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
        user = User.query.filter_by(id=current_user.id).first()
        redeemvouchers = RedeemedVouchers.query.filter_by(user_id=current_user.id).all()
        for redeemvoucher in redeemvouchers:
            redeemvoucher_list.append(redeemvoucher)

        # Get order history from session (or temporary storage)
        order_history = session.get('order_history', [])

        return render_template(
            'account.html',
            user=user,
            redeemvoucher_list=redeemvoucher_list,
            order_history=order_history,
            languages=app.config['LANGUAGES']
        )
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
    carts_list = []  # List to store cart items
    total = 0  # Total price of the cart
    error_messages = []  # Store validation errors
    recommendations = []  # List to store recommended products

    if current_user.is_authenticated:
        # Fetch all cart items for the logged-in user
        carts = Cart.query.filter_by(user_id=current_user.id).all()

        if request.method == 'POST':
            # Handle quantity updates from the form
            for cart in carts:
                # Get the dynamic field name for the quantity input
                quantity_field = f"quantity_{cart.id}"  
                new_quantity = request.form.get(quantity_field, type=int)  # Fetch new quantity from the form

                if new_quantity is not None:
                    # Validate the new quantity
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

        # Calculate the total price and validate cart items
        for cart in carts:
            if cart.product:  # Check if the product exists
                if cart.quantity > cart.product.stock:
                    error_messages.append(
                        f"'{cart.product.name}' quantity ({cart.quantity}) exceeds available stock ({cart.product.stock})."
                    )
                else:
                    # Add valid cart items to the list and calculate the total price
                    discounted_price = cart.product.price * 0.85  # Apply 15% discount
                    total += cart.quantity * discounted_price
                    carts_list.append(cart)
            else:
                # Remove invalid cart entries (e.g., product no longer exists)
                db.session.delete(cart)
                db.session.commit()

        # Fetch recommendations
        if carts_list:
            # Get the category of the first product in the cart
            first_product_category = carts_list[0].product.category

            # Exclude products already in the cart from recommendations
            cart_product_ids = [cart.product_id for cart in carts_list]
            recommendations = Product.query.filter(
                Product.category == first_product_category,
                ~Product.id.in_(cart_product_ids)
            ).limit(3).all()

        # Store the total in the session for use elsewhere
        session['total'] = total

        # Render the template with updated cart information
        return render_template(
            'shoppingcart.html',
            carts=carts_list,
            total=total,
            error_messages=error_messages,
            recommendations=recommendations  # Pass recommendations to the template
        )

    else:
        # Redirect to login if the user is not authenticated
        flash("Please log in to view your shopping cart.", "warning")
        return redirect(url_for('login'))



@app.route('/order_confirmation')
@login_required
def order_confirmation():
    items = session.get('items', [])  # Ensure items are passed as dictionaries
    delivery_method = session.get('delivery_method', 'Not Specified')
    time_slot = session.get('time_slot', 'Not Specified')
    total = session.get('total', 0)

    if not items or total == 0:
        return redirect(url_for('cart'))  # Redirect if order is incomplete

    # Convert datetime to Singapore timezone
    singapore_tz = pytz.timezone('Asia/Singapore')
    current_time = datetime.now(singapore_tz).strftime("%Y-%m-%d %H:%M:%S")  # Singapore time

    # Create the order
    order = {
        "date": current_time,
        "order_items": items,  # Items list with quantity
        "delivery_method": delivery_method,
        "time_slot": time_slot,
        "total": total,
    }

    # Append the order to the session's order history
    order_history = session.get('order_history', [])
    order_history.append(order)
    session['order_history'] = order_history

    # Clear session variables used for the order
    session.pop('items', None)
    session.pop('delivery_method', None)
    session.pop('time_slot', None)
    session.pop('total', None)

    return render_template(
        'order_confirmation.html',
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

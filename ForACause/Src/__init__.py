from flask import Flask, session, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os
import secrets
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_babel import Babel
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
secretKey = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database/db.sqlite3')
app.config['SECRET_KEY'] = secretKey
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
GOOGLE_MAPS_API_KEY = ['AIzaSyCcL6Ot97Y8Gtk0-heploLjEebJOUgEJoo']
app.config['GOOGLE_MAPS_API_KEY'] = GOOGLE_MAPS_API_KEY
app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
app.config['MAIL_PORT'] = 587 
app.config['MAIL_USE_TLS'] = True 
app.config['MAIL_USE_SSL'] = False 
app.config['MAIL_USERNAME'] = 'foracause2025@gmail.com'
app.config['MAIL_PASSWORD'] = 'nsda olut jbhm tfkv'
app.config['MAIL_DEFAULT_SENDER'] = 'foracause2025@gmail.com'
scheduler = BackgroundScheduler()
scheduler.start()
print("Scheduler started...")
# Configure languages for Flask-Babel
app.config['LANGUAGES'] = {
    'en': 'English',  # English
    'ta': 'Tamil',    # Tamil
    'zh': 'Chinese',  # Chinese
    'ms': 'Malay'     # Malay
}
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Initialize Flask-Babel
babel = Babel()

def get_locale():
    """
    Determines the best match for supported languages.
    If a user has a language preference saved in the session, it uses that.
    Otherwise, it uses the browser's preferred language.
    """
    return session.get('lang', request.accept_languages.best_match(app.config['LANGUAGES'].keys()))

# Initialize Babel with the locale selector
babel.init_app(app, locale_selector=get_locale)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
migrate = Migrate(app, db)
app.app_context().push()

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
from . import routes

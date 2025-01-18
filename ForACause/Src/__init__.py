from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
import os
import secrets
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_babel import Babel

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
secretKey = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database/db.sqlite3')
app.config['SECRET_KEY'] = secretKey
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure the upload folder
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static/images')

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
app.app_context().push()

from Src import routes

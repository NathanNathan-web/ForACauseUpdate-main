from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import secrets
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
secretKey = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database/db.sqlite3')
app.config['SECRET_KEY'] = secretKey
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'      
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.app_context().push()

from Src import routes

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_restful import Api

app = Flask(__name__)
app.config['SECRET_KEY'] = '2cf77c64b74f018eb8436c445303a27e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'flash_success'

from dashboard.api import DataUpdate
api = Api(app)
api.add_resource(DataUpdate, "/update/<int:device_id>/")

from dashboard import routes

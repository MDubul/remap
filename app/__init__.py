from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from config import config
from flask.ext.login import LoginManager
from flask_googlemaps import GoogleMaps

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()


login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.user_login'



def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config[config_name])
    app.config.from_envvar('remap-config')

    config[config_name].init_app(app)

    bootstrap.init_app(app) # not used
    mail.init_app(app)      # not used
    moment.init_app(app)
    db.init_app(app)
    GoogleMaps(app)


    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_Blueprint
    app.register_blueprint(auth_Blueprint, url_prefix='/auth')

    return app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_googlemaps import GoogleMaps

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.user_login'


def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config[config_name])
    app.config.from_envvar('remap-config')

    config[config_name].init_app(app)

    db.init_app(app)
    GoogleMaps(app)

    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app

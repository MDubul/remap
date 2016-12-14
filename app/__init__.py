from config import config
from flask import Flask
from flask_googlemaps import GoogleMaps
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

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

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .project import project as project_blueprint
    app.register_blueprint(project_blueprint, url_prefix='/project')

    return app

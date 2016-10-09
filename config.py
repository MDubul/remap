import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:

    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

    def init_app(app):
        pass

class DevelopmentConfig(Config):

    pass
    DEBUG = True

    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

class ProductionConfig(Config):

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = { 'development': DevelopmentConfig,
           'testing': TestingConfig,
           'production': ProductionConfig,
           'default': ProductionConfig
           }

import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), os.pardir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'NOTSOSECRET')
    SERVER_NAME = os.environ.get('SERVER_NAME', 'localhost:5000')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    REDIS_URL = os.environ.get('REDIS_URL', None)
    JSONIFY_PRETTYPRINT_REGULAR = False
    SITE_INDEX = 'https://github.com/ulyssesv/bflask'
    API_MIN_DISTANCE_METERS = 100
    API_MAX_DISTANCE_METERS = 5000
    API_DEFAULT_DISTANCE_METERS = 2500
    API_MAX_STOPS = 25

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL', None)


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', None)


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', None)

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

        import logging
        logger = logging.getLogger('raven.base.Client')
        logger.setLevel(logging.CRITICAL)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

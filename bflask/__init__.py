from flask import Flask
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_redis import Redis
from bflask.config import config
from bflask.models import db, Agency, Route, Stop
from raven.contrib.flask import Sentry

migrate = Migrate()
sentry = Sentry()
cors = CORS()
ma = Marshmallow()
redis = Redis()


def create_app(config_name='default'):
    app = Flask(__name__)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    sentry.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    cors.init_app(app, resources={r'/api/*': {'origins': '*'}})
    redis.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .api_v1 import api as api_v1_blueprint
    app.register_blueprint(api_v1_blueprint, url_prefix='/api/v1')

    return app

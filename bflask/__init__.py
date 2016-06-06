import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_redis import Redis
from bflask.models import db, Agency, Route, Stop
from raven.contrib.flask import Sentry

migrate = Migrate()
sentry = Sentry()
cors = CORS()
ma = Marshmallow()
redis = Redis()


def create_app():
    app = Flask(__name__)

    load_dotenv(os.path.join(os.path.dirname(__file__), os.pardir, '.env'))
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', None)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['REDIS_URL'] = os.environ.get('REDIS_URL', None)
    app.config['SITE_INDEX'] = 'https://github.com/ulyssesv/bflask'

    app.config['API_MIN_DISTANCE_METERS'] = 100
    app.config['API_MAX_DISTANCE_METERS'] = 5000
    app.config['API_DEFAULT_DISTANCE_METERS'] = 2500
    app.config['API_MAX_STOPS'] = 25

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

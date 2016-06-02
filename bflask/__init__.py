import os
from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from bflask.models import db, Agency, Route, Stop
from raven.contrib.flask import Sentry

migrate = Migrate()
sentry = Sentry()


def create_app():
    app = Flask(__name__)

    load_dotenv(os.path.join(os.path.dirname(__file__), os.pardir, '.env'))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', None)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    sentry.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

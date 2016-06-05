from bflask import create_app
from flask import current_app
from webargs import fields, validate


app = create_app()

with app.app_context():
    get_departures_args = {
        'latitude': fields.Number(required=True, validate=validate.Range(min=-85, max=85)),
        'longitude': fields.Number(required=True, validate=validate.Range(min=-180, max=180)),
        'distance': fields.Integer(
            missing=current_app.config['DEPARTURES_DEFAULT_DISTANCE_METERS'],
            validate=validate.Range(
                min=current_app.config['DEPARTURES_MIN_DISTANCE_METERS'],
                max=current_app.config['DEPARTURES_MAX_DISTANCE_METERS'])
        ),
    }

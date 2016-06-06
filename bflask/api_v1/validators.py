from bflask import create_app, db
from bflask.models import Stop
from flask import current_app
from webargs import fields, validate, ValidationError


app = create_app()

with app.app_context():
    def stop_exists(tag):
        if not db.session.query(db.exists().where(Stop.tag == tag)).scalar():
            # TODO: Return 404 instead of 422.
            raise ValidationError("Stop does not exist.")

    get_stop_args = {
        'tag': fields.Str(required=True, validate=stop_exists, location='view_args'),
    }

    get_location_args = {
        'latitude': fields.Number(required=True, validate=validate.Range(min=-85, max=85)),
        'longitude': fields.Number(required=True, validate=validate.Range(min=-180, max=180)),
        'distance': fields.Integer(
            missing=current_app.config['API_DEFAULT_DISTANCE_METERS'],
            validate=validate.Range(
                min=current_app.config['API_MIN_DISTANCE_METERS'],
                max=current_app.config['API_MAX_DISTANCE_METERS'])
        ),
    }

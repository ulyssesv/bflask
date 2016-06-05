from bflask.models import Stop, StopSchema
from flask import current_app
from webargs.flaskparser import use_args
from . import api
from .validators import get_departures_args


@api.route('/departures/', methods=['GET'])
@use_args(get_departures_args)
def get_departures(args):
    """
    Get a list of stops with their corresponding departure times
    in a range of <distance> from the <latitude>,<longitude> position.
    """
    stops = Stop.query_nearby(
        args['latitude'],
        args['longitude'],
        args['distance'],
        current_app.config['DEPARTURES_MAX_STOPS'])

    stop_schema = StopSchema()
    return stop_schema.jsonify(stops, many=True)

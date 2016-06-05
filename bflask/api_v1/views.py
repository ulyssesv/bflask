from bflask.models import Stop
from bflask.nextbus import NextBus
from flask import current_app as app, jsonify
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
    nb = NextBus()

    stops = Stop.query_nearby(
        args['latitude'],
        args['longitude'],
        args['distance'],
        app.config['DEPARTURES_MAX_STOPS'])

    # response = defaultdict(lambda: {'departures': []})
    for stop in stops:
        for route in stop.Stop.routes:
            nb.prepare_predictions(route.agency.tag, route.tag, stop.Stop.tag)
            # TODO: Enable caching.
            # departures = Departure.get_cached(route.agency.tag, route.tag, stop.Stop.tag)
            # response[stop.Stop.id]['departures'] += departures
            # if not departures:
            #     nb.prepare_predictions(route.agency.tag, route.tag, stop.Stop.tag)

    response = nb.fetch_predictions()

    return jsonify(response)

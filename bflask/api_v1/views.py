from bflask.models import Stop, StopSchema
from bflask.nextbus import NextBus
from flask import current_app as app, jsonify
from webargs.flaskparser import use_args
from . import api
from .validators import get_stop_args, get_location_args


@api.route('/stops/', methods=['GET'])
@use_args(get_location_args)
def get_stops(args):
    """
    Get a list of stops in a range of <distance> from the <latitude>,<longitude> position.
    """
    stops = Stop.query_nearby(
        args['latitude'],
        args['longitude'],
        args['distance'],
        app.config['API_MAX_STOPS'])

    for i in range(len(stops)):
        # TODO: Use a mapper or fix the query to inject
        # distance inside de Stop object for deserialization.
        stops[i].Stop.distance = stops[i].distance
        stops[i] = stops[i].Stop

    stop_schema = StopSchema()
    return stop_schema.jsonify(stops, many=True)


@api.route('/stops/<int:id>/departures', methods=['GET'])
@use_args(get_stop_args)
def get_stop_departures(args):
    """
    TODO.
    """
    return jsonify({})


@api.route('/departures/', methods=['GET'])
@use_args(get_location_args)
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
        app.config['API_MAX_STOPS'])

    # response = defaultdict(lambda: {'departures': []})
    for stop in stops:
        for route in stop.Stop.routes:
            stop.Stop.distance = stop.distance  # Injecting distance hybrid method into the object.
            nb.prepare_predictions(route.agency, route, stop.Stop)
            # TODO: Enable caching.
            # departures = Departure.get_cached(route.agency.tag, route.tag, stop.Stop.tag)
            # response[stop.Stop.id]['departures'] += departures
            # if not departures:
            #     nb.prepare_predictions(route.agency.tag, route.tag, stop.Stop.tag)

    response = nb.fetch_predictions()

    return jsonify(response)

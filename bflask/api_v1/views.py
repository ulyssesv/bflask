from bflask.models import Stop, StopSchema, stops_schema
from decimal import Decimal, InvalidOperation
from flask import request, jsonify
from werkzeug.exceptions import BadRequestKeyError
from . import api


@api.route('/departures/', methods=['GET'])
def get_departures():
    """
    Get departures from all stops within a range from
    the provided latitude and longitude.
    """
    try:
        latitude = Decimal(request.args['latitude'])
        longitude = Decimal(request.args['longitude'])
    except (BadRequestKeyError, InvalidOperation) as e:
        # TODO: Send an error code, validate arguments separately.
        message = {
            BadRequestKeyError: "Missing latitude and/or longitude arguments.",
            InvalidOperation: "Bad latitude and/or longitude arguments. Must be decimal.",
        }

        response = jsonify({'error': 'Bad Request', 'message': message[type(e)]})
        response.status_code = 400
        return response

    # TODO: Implement location based filter.
    stops = Stop.query.limit(10).all()
    return stops_schema.jsonify(stops)

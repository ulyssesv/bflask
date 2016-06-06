from datetime import datetime
from collections import defaultdict
from urllib.parse import urlencode
from distutils.util import strtobool
from xml.etree import ElementTree

import requests
import xmltodict


class NextBus:
    """
    Wrapper to the NextBus XML API.
    """
    API_URL = 'http://webservices.nextbus.com/service/publicXMLFeed'
    MAX_ROUTES_PER_ROUTE_CONFIG = 100
    MAX_STOPS_PER_PREDICTION = 150

    class APIError(Exception):
        pass

    def __init__(self):
        self._predictions_data = defaultdict(list)
        self._stop_data = {}

    def call(self, command, *args, **kwargs):
        kwargs['command'] = command

        url = self.API_URL
        url += '?{}&{}'.format(urlencode(kwargs), urlencode(args))

        r = requests.get(url, headers={'Accept-Encoding': 'gzip, deflate'})
        xml = ElementTree.fromstring(r.text)

        if xml[0].tag == 'Error':
            raise NextBus.APIError(xml[0].text.strip())

        force_list = {key: True for key in ('route', 'stop', 'predictions', 'direction', 'prediction')}
        return xmltodict.parse(r.text, force_list=force_list)

    def agency_list(self):
        return self.call('agencyList')

    def route_list(self, agency_tag):
        return self.call('routeList', a=agency_tag)

    def route_config(self, agency_tag, route_tag=None):
        route_arg = {'r': route_tag} if route_tag else {}
        return self.call('routeConfig', a=agency_tag, **route_arg)

    def predictions(self, agency_tag, route_stop_tags):
        """
        Request multiple predictions from the <agency>'s <route_stop_tags>.

        :param route_stop_tags: Format: `[{'route': <tag>, 'stop': <tag>}]`
        """
        # TODO: Respect `MAX_STOPS_PER_PREDICTION` API limit.
        stops = [('stops', '{}|{}'.format(item['route'].tag, item['stop'].tag)) for item in route_stop_tags]
        return self.call('predictionsForMultiStops', *stops, a=agency_tag)

    def prepare_predictions(self, agency, route, stop):
        """Add route/stop to a `_predictions_data` buffer in order to fetch as a batch with `fetch_predictions`."""
        self._predictions_data[agency].append({'route': route, 'stop': stop})
        self._stop_data[stop.tag] = stop

    def fetch_predictions(self):
        """Fetches batch predictions for the `_predictions_data` buffer by agency."""
        predictions = []
        for agency, route_stop_tags in self._predictions_data.items():
            for response in self.predictions(agency.tag, route_stop_tags)['body']['predictions']:
                response['@agencyTag'] = agency.tag  # We will need this later.
                predictions.append(response)

        stops = defaultdict(lambda: {'routes': {}})
        for prediction in predictions:
            stops[prediction['@stopTag']].update({
                'title': prediction['@stopTitle'],
                'latitude': self._stop_data[prediction['@stopTag']].latitude,
                'longitude': self._stop_data[prediction['@stopTag']].longitude,
                'distance': self._stop_data[prediction['@stopTag']].distance,
            })
            stops[prediction['@stopTag']]['routes'][prediction['@routeTag']] = {
                'agency_title': prediction['@agencyTitle'],
                'agency_tag': prediction['@agencyTag'],
                'trips': [],
            }

            for direction in prediction.get('direction', []):
                # TODO: Capture `dirTitleBecauseNoPrediction` attribute when no direction is present.
                for trip in direction.get('prediction', []):
                    stops[prediction['@stopTag']]['routes'][prediction['@routeTag']]['trips'].append({
                        'direction_title': direction['@title'],
                        'trip_tag': trip['@tripTag'],
                        'eta_timestamp': int(trip['@epochTime'])//1000.0,
                        'eta_seconds': int(trip['@seconds']),
                        'is_departure': bool(strtobool(trip['@isDeparture'])),
                        'is_affected_by_layover': bool(strtobool(trip.get('@affectedByLayover', 'False'))),
                        'vehicle': trip['@vehicle'],
                    })

        return stops

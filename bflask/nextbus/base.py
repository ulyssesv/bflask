from urllib.parse import urlencode
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

    def call(self, command, **kwargs):
        kwargs['command'] = command

        url = self.API_URL
        url += '?{}'.format(urlencode(kwargs))

        r = requests.get(url, headers={'Accept-Encoding': 'gzip, deflate'})
        xml = ElementTree.fromstring(r.text)

        if xml[0].tag == 'Error':
            raise NextBus.APIError(xml[0].text.strip())

        return xmltodict.parse(r.text, force_list={'route': True, 'stop': True})

    def agency_list(self):
        return self.call('agencyList')

    def route_list(self, agency_tag):
        return self.call('routeList', a=agency_tag)

    def route_config(self, agency_tag, route_tag=None):
        route_arg = {'r': route_tag} if route_tag else {}
        return self.call('routeConfig', a=agency_tag, **route_arg)

    def predictions(self, agency_tag, stop_id):
        return self.call('predictions', a=agency_tag, stopId=stop_id)

from urllib.parse import urlencode
from xml.etree import ElementTree

import requests
import xmltodict


class NextBus:
    """
    Wrapper to the NextBus XML API.
    """
    api_url = 'http://webservices.nextbus.com/service/publicXMLFeed'

    class APIError(Exception):
        pass

    def call(self, command, **kwargs):
        kwargs['command'] = command

        url = self.api_url
        url += '?{}'.format(urlencode(kwargs))

        r = requests.get(url, headers={'Accept-Encoding': 'gzip, deflate'})
        xml = ElementTree.fromstring(r.text)

        if xml[0].tag == 'Error':
            raise NextBus.APIError(xml[0].text.strip())

        return xmltodict.parse(r.text)

    def agency_list(self):
        return self.call('agencyList')

    def route_list(self, agency_tag):
        return self.call('routeList', a=agency_tag)

    def route_config(self, agency_tag, route_tag):
        return self.call('routeConfig', a=agency_tag, r=route_tag)

    def predictions(self, agency_tag, stop_id):
        return self.call('predictions', a=agency_tag, stopId=stop_id)

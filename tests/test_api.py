import unittest
import json
import httpretty
from flask import url_for
from bflask import create_app, db
from bflask.models import Agency, Route, Stop


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        # TODO: Use fixtures.
        agency = Agency(
            id=1,
            tag='sf-muni',
            title="San Francisco Muni",
        )
        db.session.add(agency)
        r1 = Route(
            id=1,
            tag='5R',
            title="5R-Fulton Rapid",
            agency_id=1,
        )
        r2 = Route(
            id=2,
            tag='60',
            title="Powell/Hyde Cable Car",
            agency_id=1,
        )
        db.session.add_all([r1, r2])
        s1 = Stop(
            tag='5644',
            title="Market Between 5th & 4th St",
            external_id='15644',
            latitude=37.7848399,
            longitude=-122.40683,
            routes=[r1],
        )
        s2 = Stop(
            tag='6063',
            title="Powell St & Market St",
            external_id='16063',
            latitude=37.7846999,
            longitude=-122.40768,
            routes=[r2],
        )
        db.session.add_all([s1, s2])
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_stops(self):
        params = {
            'latitude': '37.784792',
            'longitude': '-122.407223',
            'distance': 2500,
        }
        response = self.client.get(url_for('api.get_stops'), query_string=params)
        self.assertTrue(response.status_code == 200)
        expected = {
            'stops': [{
                'departures': '/api/v1/stops/5644/departures/',
                'distance': 35,
                'external_id': 15644,
                'id': 1,
                'latitude': 37.7848399,
                'longitude': -122.40683,
                'routes': [{
                    'agency': {
                        'id': 1,
                        'tag': 'sf-muni',
                        'title': 'San Francisco Muni'},
                    'id': 1,
                    'tag': '5R',
                    'title': '5R-Fulton Rapid'
                }],
                'tag': '5644',
                'title': 'Market Between 5th & 4th St'
            }, {
                'departures': '/api/v1/stops/6063/departures/',
                'distance': 41,
                'external_id': 16063,
                'id': 2,
                'latitude': 37.7846999,
                'longitude': -122.40768,
                'routes': [{
                    'agency': {
                        'id': 1,
                        'tag': 'sf-muni',
                        'title': 'San Francisco Muni'},
                    'id': 2,
                    'tag': '60',
                    'title': 'Powell/Hyde Cable Car'
                }],
                'tag': '6063',
                'title': 'Powell St & Market St'}]
        }
        response = json.loads(response.data.decode('utf-8'))
        self.assertDictEqual(response, expected)

    @httpretty.activate
    def test_stop_departures(self):
        stub = open('tests/test_stop_departures.xml').read()
        httpretty.register_uri(
            httpretty.GET,
            'http://webservices.nextbus.com/service/publicXMLFeed?command=predictionsForMultiStops&a=sf-muni&stops=5R|5644',
            body=stub,
            content_type='text/xml')

        response = self.client.get(url_for('api.get_stop_departures', tag='5644'))
        self.assertTrue(response.status_code == 200)
        self.maxDiff = None
        expected = {
            "stops": [{
                "tag": "5644",
                "title": "Market Between 5th & 4th St",
                "distance": None,
                "latitude": 37.7848399,
                "longitude": -122.40683,
                "routes": {
                    "5R": {
                        "agency_tag": "sf-muni",
                        "agency_title": "San Francisco Muni",
                        "title": "5R-Fulton Rapid",
                        "trips": [
                            {
                                "direction_title": "Inbound to Transbay Terminal",
                                "eta_seconds": 215,
                                "eta_timestamp": 1465250893.0,
                                "is_affected_by_layover": False,
                                "is_departure": False,
                                "trip_tag": "7127568",
                                "vehicle": "5413"
                            }, {
                                "direction_title": "Inbound to Transbay Terminal",
                                "eta_seconds": 663,
                                "eta_timestamp": 1465251341.0,
                                "is_affected_by_layover": False,
                                "is_departure": False,
                                "trip_tag": "7127569",
                                "vehicle": "5446"
                            }, {
                                "direction_title": "Inbound to Transbay Terminal",
                                "eta_seconds": 1144,
                                "eta_timestamp": 1465251822.0,
                                "is_affected_by_layover": False,
                                "is_departure": False,
                                "trip_tag": "7127570",
                                "vehicle": "5422"
                            }, {
                                "direction_title": "Inbound to Transbay Terminal",
                                "eta_seconds": 1442,
                                "eta_timestamp": 1465252120.0,
                                "is_affected_by_layover": False,
                                "is_departure": False,
                                "trip_tag": "7127571",
                                "vehicle": "5420"
                            }, {
                                "direction_title": "Inbound to Transbay Terminal",
                                "eta_seconds": 2009,
                                "eta_timestamp": 1465252687.0,
                                "is_affected_by_layover": False,
                                "is_departure": False,
                                "trip_tag": "7127572",
                                "vehicle": "5473"
                            }
                        ],
                    }
                }
            }]
        }
        response = json.loads(response.data.decode('utf-8'))
        self.assertDictEqual(response, expected)

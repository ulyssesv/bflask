.. _api:

API documentation
=================

GET /stops/
-----------

Retrieves a list of bus stops within within <distance> from <latitude>,<longitude>.

+----------------------------------------------------+
| Query String Arguments                             |
+============+=======================================+
| latitude   | Latitude of the center point.         |
|            +---------------------------------------+
|            | Required                              |
|            +---------------------------------------+
|            | Range: -85 to 85                      |
+------------+---------------------------------------+
| longitude  | Longitude of the center point.        |
|            +---------------------------------------+
|            | Required                              |
|            +---------------------------------------+
|            | Range: -180 to 180                    |
+------------+---------------------------------------+
| distance   | Radius in meters to search for stops. |
|            +---------------------------------------+
|            | Range: 100 to 5000                    |
|            +---------------------------------------+
|            | Default: 2500                         |
+------------+---------------------------------------+

**Example**

Request:

::

    GET /api/v1/stops/?distance=5000&latitude=37.78484&longitude=-122.40682989999999

Response:

::

    STATUS 200 OK
    Content-Type: application/json

.. code-block:: javascript

    {
      "stops": [
        {
          "id": 7206,
          "tag": "5644",
          "external_id": 15644,
          "title": "Market Between 5th & 4th St",
          "latitude": 37.7848399,
          "longitude": -122.40683,
          "distance": 35,
          "departures": "/api/v1/stops/5644/departures/",
          "routes": [
            {
              "id": 98,
              "tag": "5",
              "title": "5-Fulton",
              "agency": {
                "id": 2,
                "tag": "sf-muni",
                "title": "San Francisco Muni"
              }
            }
          ]
        }
      ]
    }

GET /stops/<tag>/departures/
----------------------------

Retrieves the list of departures for all bus routes of the <tag> stop.

+--------------------------------+
| URI Arguments                  |
+============+===================+
| tag        | Stop tag.         |
+------------+-------------------+

**Example**

Request:

::

    GET /api/v1/stops/5644/departures/

Response:

::

    STATUS 200 OK
    Content-Type: application/json

.. code-block:: javascript

    {
      "stops": [
        {
          "tag": "5644",
          "title": "Market Between 5th & 4th St",
          "latitude": 37.7848399,
          "longitude": -122.40683,
          "distance": null,
          "routes": {
            "5": {
              "agency_tag": "sf-muni",
              "agency_title": "San Francisco Muni",
              "title": "5-Fulton",
              "trips": [
                {
                  "direction_title": "Inbound to Transbay Terminal",
                  "eta_seconds": 2330,
                  "eta_timestamp": 1465285133,
                  "is_affected_by_layover": true,
                  "is_departure": false,
                  "trip_tag": "7127472",
                  "vehicle": "5446"
                },
                {
                  "direction_title": "Inbound to Transbay Terminal",
                  "eta_seconds": 3950,
                  "eta_timestamp": 1465286753,
                  "is_affected_by_layover": true,
                  "is_departure": false,
                  "trip_tag": "7127471",
                  "vehicle": "5427"
                }
              ]
            }
          }
        }
      ]
    }

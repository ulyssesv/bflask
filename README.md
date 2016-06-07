# BFlask

    An API proxy for NextBus departure information.

This app fetches routes and stops information from the NextBus public API and
stores it locally in a database. It also provides departure information for the
closest stops of a desired location.

**Backend repository**  
https://github.com/ulyssesv/bflask/

**Frontend repository**  
https://github.com/ulyssesv/bangular/

**Backend host**  
http://bflask-dev.us-east-1.elasticbeanstalk.com/

**Frontend host**  
http://bangular-static.s3-website-us-east-1.amazonaws.com/

**Documentation**  
http://bflask.readthedocs.io/en/latest/

## Development Environment

At a bare minimum you'll need:
- Python 3
- PostgreSQL
- Virtualenv

Assuming you have the required dependencies, then run:

```bash
$ git clone <repo>
$ cd <project>
$ mkdir env | virtualenv env --python python3
$ source env/bin/activate
$ pip install -r requirements.txt
```

The app uses a `.env` file to export environment variables to its instance
settings. Create a `.env` file like the sample below and modify according to
your local setup.

```
FLASK_DEBUG=1
DEV_DATABASE_URL=postgresql://user:password@host:port/database
```

The app uses [Alembic](https://bitbucket.org/zzzeek/alembic) to manage database
migrations. Run `$ python manage.py db upgrade` to install after creating the database.

To load the initial required data, simply run `$ python manage.py load`. This will query the NextBus API for agencies, routes and stops and save it to the database. Currently we're limiting the loading to the SF Muni agency.

To run the development server, run `$ python manage.py runserver`.

## Testing

[![Build Status](https://travis-ci.org/ulyssesv/bflask.svg?branch=master)](https://travis-ci.org/ulyssesv/bflask)

Tests can be run using nose:
```bash
$ nosetests
```

The `TEST_DATABASE_URL` environment variable is required to be set or defined in the `.env` file.

More on tests under the [Application Architecture](#application-architecture) section.

## Production Environment

The app is hosted on AWS using the following services:  
**bflask application:**  Elastic Beanstalk/EC2  
**bflask database:**  RDS  
**bangular static website:** S3

The `DATABASE_URL` environment variable is required to be set in the production environment. You can also set `SENTRY_DSN` for exception logging.

Possible improvements:
- add CloudFront to the static website
- enable SSL on the application load balancer using Certificate Manager
- enable SSL on the CloudFront endpoint
- manage the architecture using CloudFormation instead of clicking on the interface

## Monitoring

Exception monitoring is done via [Sentry](http://www.getsentry.com/).

Possible improvements:
- monitor the NextBus API for downtimes
- monitor long queries
- improve the application logging and save it using rotation

## Application Architecture

### Language & Framework

Python is the language I'm most comfortable with and I've been working with Python/Django for years. Even though Django would be up to the task for the application and I'm very rusty on Flask, I decided to go with Flask some reasons:
- Django becomes the application and it's easy to end up with a monolithic solution
- Django is more about configuration so it can shadow the coding
- I've read somewhere that Flask is well used inside Uber
- it would be a good exercise and I like to take risks

### Dependencies

Some may say that using too many dependencies is an anti-pattern (specially after the left-pad incident), but I decided to use a lot of them for this project. The time was short and most of the dependencies are up to date and well tested.

In a production scenario, I'd think carefully about each dependency/package before adding them to the project; if it's widely used in the community, if it's easy to fork and hack, if it's too old, if it supports my other dependencies, if there's any security risk, etc.

### Database

Since we're talking about using coordinates, one clear choice is PostgreSQL. It could be extendend to use the GIS addons (I'm not using), or even to PostGIS without going too far. Another option would be Redis with its Geo API (GEOADD, GEOSET). Persistance is not a big issue since the data isn't sensitive (it should be reloaded any time).

### Application Structure

The app structure was heavily based on [Flasky](https://github.com/miguelgrinberg/flasky).

The biggest concerns on designing the app were:
- respecting most of the [12factor](http://12factor.net/) factors
- avoiding too much coupling among the modules
- trying to assign a single responsability to each module
- writing modules that are easy to test
- avoiding really crappy performance (looped queries, huge memory comsumption) code
- avoiding really insecure code

### Data Source

I chose the [NextBus](http://www.nextbus.com/xmlFeedDocs/NextBusXMLFeed.pdf) data source. The [511 API](http://511.org/developer-resources_transit-api.asp) will soon be discontinued. I should actually have chosen the [Transport for London Unified API](https://api.tfl.gov.uk/) which has way better endpoints and documentation. Most of the coding time was spent towards getting around the weird API calls, limits and data modelling (i.e.: the entries don't have an unique ID, there's no endpoing for gathering a single resource data).

The data source is encapsulated in a `nextbus` module that provides a facade to the API calls and formats the responses from XML to dictionaries.

### Data Modelling and Initial Data

As we're using a relation database, it was simple to define the models and attributes.

`Agencies` have many `Routes`.  
`Routes` have many `Stops`.  
`Stops` belongs to many `Routes`  

The `Departure` model wasn't needed since its data is proxied from the NextBus API to the API endpoints.

The `Agencies`, `Routes` and `Stops` data is fetched from the NextBus API in an initial step and stored to provide faster access for the API endpoints (such as retrieving the nearests stops within a distance).

> **_Warning!_**  
> The loader has a bug. It bulk inserts all the data without considering duplicate `Stops`. There is no unique ID for a `Stop`. To check for uniqueness it's needed to join the `Agency.tag` and the `Stop.tag`, and the current code doesn't do that.

### The API

#### Versioning

The API is versioned just for demonstration purposes.

It's indeed recommended to version an API (with a deprecation policy) to improve support for old systems or outdated apps.

In Flask this can be done using multiple Blueprints and separating the code from the views to a shared library.

#### Throttling

There is currently no throttling for the API.

It is a **big deal** since it is a public API that does not require authentication and requests to the API results in requests to the NextBus service and trigger its own limit, denying service.

It can be easily done using [Flask-Limiter](https://flask-limiter.readthedocs.io/en/stable/) and a cache backend (such as Redis). We have to take into account that simply using the remote IP address can impact users behind a NAT, so using a combination of the User-Agent and the IP address, for example, could be more fair.

#### Caching

There is currently no caching in the API.

It is a **very big deal** since requests to the API results in requests to the NextBus service - which is really slow (besides the rate limiting issue described above). Caching would dramatically improve the scalability of the API and is essential to this aplication.

Caching could be easily done by using a cache backend (such as Redis) and storing the NextBus responses for each bus stop/route departure information. Since the nature of the service depends on a close to real-time response for quality, the cache keys could have a TTL of 1 or 2 minutes.

Another improvement is to cache the entire location based request by adding error to the coordinates (i.e.: reducing one or two digits from the lat/lon) and querying for a bigger area. This way we could increase the chance of a cache hit and reduce latency/database access since we would serve the entire request using only the cache.

Possible improvements:
- cache the departure times for a bus/route
- cache the location based requests

#### Authentication

There is currently no authentication for the API.

This is not a big deal since the endpoints never save to the database but it's easier for someone to abuse the service.

Possible improvement:
- add HMAC/Token based authentication

#### Security

Security is not a big concern in this project.

Since it's a public API, there is no need to setup CORS. There is no traffic of private data, so SSL is not essential. There's no risk of XSS as there is no authentication. SQL Injection is dealt with in the framework level.

In a similar application that deals with sensitive data, we could check for the data source certificate and add some kind of checksum for the API responses.

### Geographic Support

The project is using a `GeoLocation` class that implements the calculations from [this very good article](http://janmatuschek.de/LatitudeLongitudeBoundingCoordinates) about geodesic distance calculation.

The math is not trivial since Earth is a geodesic sphere and the distance must be calculated taking this shape into account.

This class also provides a method to find the bounding box for a Great Circle, so we can use indexes to speed up the queries that selects points in a certain distance from another point.

### Tests

There are currently only 2 test cases that tests against the API endpoints used in the frontend: `api.get_stops` and `api.get_stop_departures`. The test setup creates some minimal models based on real data and the test cases run against the views using [HTTPretty](https://github.com/gabrielfalcao/HTTPretty) to mock the request to the NextBus API when needed.

The coverage is very low, so improvements are needed.

Possible improvements:
- add NextBus module tests
- add GeoLocation module tests
- add models tests
- add tests against the live NextBus API

### Coding Guidelines

This project aims to follow the Zen of Python and PEP-8 (except the 80 character line limit).

There are a lot of `# TODO: ...` comments that should be avoided in a production project.

### Version Control

Everything was done in the master branch, which is obviously a bad idea when coding in a team. In a production project, I'd employ some feature branch technique (git-flow or at least a develop branch) and tags for versioning.

There's also no versioning/changelog. A possible improvement is to use semantic versioning, define the version in the app package and maintain a CHANGELOG file.

### Documentation

The documentation is generated with Sphinx and hosted in Read the Docs.

Possible improvements:
- document the models
- document the `NextBus` class
- document the `GeoLocation` class
- add PyDoc to everything

### Frontend App

The [frontend app](https://github.com/ulyssesv/bangular) is just a small Angular single page (in this case, single view also) website.

The structure is based on some huge Yeoman boilerplate that works really well and respects a componentized structure. It comes with helpers to inject the scripts and styles without having to declare everything and it also builds and minifies everything (with sourcemaps) for distribution.

The app itself is very simple: it has a `StopService` that fetches the stops and departures per stop from the API and a single `MapController` component that displays the map and opens extra information when clicking a bus stop.

Despite having a long track record with Angular/Ionic apps, I'd go with React/Redux if starting a new production project.

from nextbus import NextBus
from bflask import create_app, db
from bflask.models import Agency, Route, Stop
from flask_migrate import MigrateCommand, Migrate
from flask_script import Manager, Server
from sqlalchemy import func
from sqlalchemy.orm import load_only

app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
manager.add_command("runserver", Server())


@manager.command
def load():
    """Load NextBus API entries."""
    # TODO: Deal with IntegrityError from the unique constraint or add logic to synchronize the data.

    print("Loading NextBus entries")

    nb = NextBus()

    # Load agencies.
    print("Loading agencies... ", end="", flush=True)
    r = nb.agency_list()
    agencies = []
    for agency in r['body']['agency']:
        agencies.append(Agency(tag=agency['@tag'], title=agency['@title']))

    db.session.bulk_save_objects(agencies)
    print("done.")

    # Load routes.
    print("Loading routes... ", end="", flush=True)
    agencies = Agency.query.all()
    routes = []
    for agency in agencies:
        r = nb.route_list(agency.tag)
        for route in r['body']['route']:
            routes.append(Route(agency_id=agency.id, tag=route['@tag'], title=route['@title']))

    db.session.bulk_save_objects(routes)
    print("done.")

    # Load stops.
    print("Loading stops... ", end="", flush=True)
    agencies = db.session.query(Agency, func.count(Route.id)).join(Agency.routes).group_by(Agency.id).all()
    stops = []

    # Caches the routes to avoid querying in the loop to add relationship instances.
    routes = Route.query.options(load_only('id', 'tag', 'agency_id')).all()
    route_cache = {'{}:{}'.format(i.agency_id, i.tag): i for i in routes}

    def _add_stop():
        # Helper method to add a stop using outer scope variables.
        stop_id_arg = {'external_id': stop['@stopId']} if '@stopId' in stop.keys() else {}
        return Stop(
            tag=stop['@tag'],
            title=stop['@title'],
            latitude=stop['@lat'],
            longitude=stop['@lon'],
            **stop_id_arg
        )

    for (agency, route_count) in agencies:
        if route_count < NextBus.MAX_ROUTES_PER_ROUTE_CONFIG:
            # The API returns up to 100 routes for an agency if the route_tag parameter is supressed.
            r = nb.route_config(agency_tag=agency.tag)
            for route in r['body']['route']:
                for stop in route['stop']:
                    s = _add_stop()
                    s.routes.append(route_cache['{}:{}'.format(agency.id, route['@tag'])])
                    stops.append(s)
        else:
            # An error is returned if an agency has more than 100 routes. The only option is to query one by one since
            # we have no pagination or batch request.
            routes = agency.routes.all()
            for route in routes:
                r = nb.route_config(agency_tag=agency.tag, route_tag=route.tag)
                for stop in r['body']['route'][0]['stop']:
                    s = _add_stop()
                    s.routes.append(route_cache['{}:{}'.format(agency.id, route.tag)])
                    stops.append(s)

    db.session.bulk_save_objects(stops)
    print("done.")

    print("Committing to database...", end="", flush=True)
    db.session.commit()
    print("done.")


if __name__ == '__main__':
    manager.run()

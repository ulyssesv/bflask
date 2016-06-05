from bflask.geolocation import GeoLocation
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from sqlalchemy import func, asc
from sqlalchemy.ext.hybrid import hybrid_method

db = SQLAlchemy()
ma = Marshmallow()


route_stop = db.Table(
    'route_stop',
    db.Column('route_id', db.Integer, db.ForeignKey('route.id')),
    db.Column('stop_id', db.Integer, db.ForeignKey('stop.id'))
)


class Agency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(30), unique=True, index=True)
    title = db.Column(db.Unicode(100))
    routes = db.relationship('Route', backref='agency', lazy='dynamic')


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agency_id = db.Column(db.Integer, db.ForeignKey('agency.id'))
    tag = db.Column(db.String(30), index=True)
    title = db.Column(db.Unicode(100))


class Stop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(30), index=True)
    external_id = db.Column(db.Integer)
    latitude = db.Column(db.Numeric(10, 7), index=True)
    longitude = db.Column(db.Numeric(10, 7), index=True)
    title = db.Column(db.Unicode(100))
    routes = db.relationship('Route', secondary=route_stop, backref=db.backref('stops', lazy='dynamic'))

    @hybrid_method
    def distance(self, center_latitude, center_longitude):
        return (
            GeoLocation.EARTH_RADIUS *
            func.acos(
                func.cos(func.radians(center_latitude)) *
                func.cos(func.radians(self.latitude)) *
                func.cos(func.radians(self.longitude) - func.radians(center_longitude)) +
                func.sin(func.radians(center_latitude)) *
                func.sin(func.radians(self.latitude)))
            )

    @classmethod
    def query_nearby(cls, latitude, longitude, distance, limit):
        """Returns the closest <limit> Stops within <distance> meters from <latitude>,<longitude>."""
        location = GeoLocation.from_degrees(latitude, longitude)
        (sw_location, ne_location) = location.bounding_locations(distance)

        return cls.query. \
            add_columns(Stop.distance(latitude, longitude).label('distance')). \
            join(Route, Stop.routes). \
            filter(
                Stop.latitude.between(sw_location.deg_lat, ne_location.deg_lat),
                Stop.longitude.between(sw_location.deg_lon, ne_location.deg_lon)). \
            order_by(asc(Stop.distance(latitude, longitude))). \
            limit(limit).all()


class StopSchema(ma.ModelSchema):
    distance = fields.Decimal(places=0, dump_only=True)

    class Meta:
        model = Stop
        fields = ('id', 'tag', 'external_id', 'latitude', 'longitude', 'title', 'distance')

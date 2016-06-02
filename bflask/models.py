from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


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

route_stop = db.Table('route_stop',
    db.Column('route_id', db.Integer, db.ForeignKey('route.id')),
    db.Column('stop_id', db.Integer, db.ForeignKey('stop.id'))
)


class Stop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(30), index=True)
    external_id = db.Column(db.Integer)
    latitude = db.Column(db.Numeric(10, 7), index=True)
    longitude = db.Column(db.Numeric(10, 7), index=True)
    title = db.Column(db.Unicode(100))
    routes = db.relationship('Route', secondary=route_stop, backref=db.backref('stops', lazy='dynamic'))

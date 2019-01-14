from geoalchemy2 import Geometry

from gis_polygon.extensions import db


class GisPolygon(db.Model):
    _created = db.Column(db.DateTime, nullable=False, default=db.text("now()"))
    _edited = db.Column(db.DateTime, nullable=False, default=db.text("now()"))
    id = db.Column(db.Integer, db.Sequence('gis_polygon_id_seq'), primary_key=True)
    class_id = db.Column(db.Integer)
    name = db.Column(db.VARCHAR)
    props = db.Column(db.JSON)
    geom = db.Column(Geometry("POLYGON", 4326))

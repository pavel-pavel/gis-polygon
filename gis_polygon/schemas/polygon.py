import pyproj
from functools import partial

from flask import request
from flask_restful import abort
from marshmallow import fields, post_load, pre_dump, post_dump
from shapely.ops import transform

from gis_polygon.extensions import ma
from gis_polygon.schemas.custom_schema_fields import GeomSchemaField

GIS_PROJECTIONS = {
    "EPSG": {'4326', '32644'}
}


class PolygonSchema(ma.ModelSchema):
    """
    Схема полигона для валидации, сериализации, десериализации.
    """

    polygon_id = fields.Int(attribute='id')
    geom = GeomSchemaField(required=True)
    name = fields.Str()
    props = fields.Raw(allow_none=True)
    class_id = fields.Int()

    def _get_projection(self, args):
        """
        Возвращает проекцию из аргументов.
        """

        if args and args.get('projection'):
            try:
                projection_name, projection_value = args.get('projection').lower().split(':')
            except ValueError:
                abort(400, error='incorrect projection')
                return

            gis_projection = GIS_PROJECTIONS.get(projection_name.upper())
            if gis_projection and projection_value in gis_projection:
                return args.get('projection')

            abort(400, error='incorrect projection')

    @post_load
    def make_polygon(self, polygon):
        user_projection = self._get_projection(request.args)
        if user_projection:
            project = partial(
                pyproj.transform,
                pyproj.Proj(init=user_projection),
                pyproj.Proj(init='epsg:4326')
            )
            polygon.geom = transform(project, polygon.geom)

    @pre_dump
    def dump_polygon(self, polygon):
        user_projection = self._get_projection(request.args)
        if user_projection:
            project = partial(
                pyproj.transform,
                pyproj.Proj(init='epsg:4326'),
                pyproj.Proj(init=user_projection)
            )
            polygon.geom = transform(project, polygon.geom)
        return polygon

    @post_dump(pass_many=True)
    def dump_polygons(self, polygons, is_collection):
        if is_collection:
            return {
                "polygons": polygons
            }
        else:
            return polygons

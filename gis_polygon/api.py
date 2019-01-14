import logging
from datetime import datetime

from flask import Blueprint, request
from flask_restful import Api, Resource, abort

from gis_polygon.extensions import db
from gis_polygon.models import GisPolygon
from gis_polygon.schemas.polygon import PolygonSchema

polygon_blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(polygon_blueprint)
logger = logging.getLogger(__name__)


class PolygonResource(Resource):

    def get(self, polygon_id=None):
        if polygon_id:
            return self.get_polygon(polygon_id)
        else:
            return self.get_polygons()

    def get_polygon(self, polygon_id: int):
        """
        Возвращает полигон.

        Пример:
        requests:
            GET /api/polygon
            response:
                200 +
                {
                    "props": null,
                    "geom": {
                        "type": "Polygon",
                        "coordinates": [[[0, 0], [1, 1], [1, 0]]]
                    },
                    "name": null,
                    "polygon_id": 4,
                    "class_id": null
                }
        """

        polygon = GisPolygon.query.get_or_404(polygon_id)

        logger.info('polygon {0} was received'.format(polygon.id))
        return PolygonSchema().dump(polygon)

    def get_polygons(self):
        """
        Возвращает все полигоны.

        Пример:
        requests:
            GET /api/polygon/{polygon_id}
            response:
                200 +
                {
                    "polygons": [
                        {
                            "props": null,
                            "geom": {
                                "type": "Polygon",
                                "coordinates": [[[0, 0], [1, 1], [1, 0]]]
                            },
                            "name": null,
                            "polygon_id": 4,
                            "class_id": null
                        }
                    ]
                }
                404
        """
        polygons = GisPolygon.query.all()
        logger.info('all polygons was received')
        return PolygonSchema(many=True).dump(polygons)

    def post(self):
        """
        Создаёт полигон.

        Пример:
        requests:
            POST /api/polygon
            Content-Type: application/json
            {
                "props": {"prop1": "value"},
                "geom": {
                    "type": "Polygon",
                    "coordinates": [
                        [[0, 0], [1, 1], [1, 0]]
                    ]
                },
                "name": "test"
            }
            response:
                200 + {"info": "OK"}
                400 + {"errors": {"geom": ["Not a valid polygon."]}}
                404
        """
        polygon_validation = PolygonSchema().load(request.json)
        if polygon_validation.errors:
            logger.debug('validation error, polygon creation cancelled')
            abort(400, errors=polygon_validation.errors)

        polygon = polygon_validation.data

        db.session.add(polygon)
        db.session.commit()
        logger.info('polygon {0} was created'.format(polygon.id))
        return {'info': 'ok'}

    def put(self, polygon_id: int):
        """
        Изменяет полигон.

        Пример:
        requests:
            PUT /api/polygon/{polygon_id}
            Content-Type: application/json
            {
                "props": {"prop1": "value"},
                "geom": {
                    "type": "Polygon",
                    "coordinates": [
                        [[0, 0], [1, 1], [1, 0]]
                    ]
                },
                "name": "test"
            }
            response:
                200 + {"info": "OK"}
                400 + {"errors": {"geom": ["Not a valid polygon."]}}
                404
        """
        polygon = GisPolygon.query.get_or_404(polygon_id)
        polygon_validation = PolygonSchema().load(request.json, instance=polygon)
        if polygon_validation.errors:
            logger.debug('validation error, polygon editing cancelled')
            abort(400, errors=polygon_validation.errors)

        polygon._edited = datetime.now()
        db.session.add(polygon)
        db.session.commit()

        logger.info('polygon {0} was edited'.format(polygon_id))
        return {'info': 'ok'}

    def delete(self, polygon_id: int):
        """
        Удаляет полигон.

        Пример:
        requests:
            DELETE /api/polygon/{polygon_id}
        response:
            200 + {"info": "OK"}
            404
        """
        polygon = GisPolygon.query.get_or_404(polygon_id)
        db.session.delete(polygon)
        db.session.commit()
        logger.info('polygon {0} was deleted'.format(polygon_id))
        return {'info': 'ok'}


api.add_resource(PolygonResource, '/polygon',
                 '/polygon/<int:polygon_id>')

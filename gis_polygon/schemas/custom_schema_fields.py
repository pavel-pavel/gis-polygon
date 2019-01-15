import json

import geojson
from flask import current_app
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape, from_shape
from marshmallow import fields
from shapely.geometry import shape


class GeomSchemaField(fields.Field):
    """
    Кастомное поле полигона для схемы marshmallow.
    """

    default_error_messages = {
        'invalid': 'Not a valid polygon.'
    }

    def _serialize(self, value: WKBElement, attr: str, obj, **kwargs):
        try:
            serialized = json.loads(geojson.dumps(to_shape(value)))
        except ValueError:
            return None
        return serialized

    def _deserialize(self, value, attr: str, data, **kwargs):
        geom = self._validated(value)
        return from_shape(shape(geom), srid=current_app.config['DEFAULT_SRID'])

    def _to_string(self, value):
        return str(value)

    def _validated(self, value):
        """Format the value or raise a :exc:`ValidationError` if an error occurs."""
        try:
            geom = geojson.loads(json.dumps(value))
            if not all([geom.coordinates, geom.type]):
                raise ValueError
            else:
                return geom
        except (TypeError, ValueError, AttributeError):
            self.fail('invalid')




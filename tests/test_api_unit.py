import pytest
from flask import json, abort, current_app
from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon, shape

from gis_polygon.app import create_app

app = create_app(testing=True)


class MockPolygon:
    """Мокает модель полигона и методы BaseQuery."""

    def __init__(self, id=None, name=None, geom=None, _created=None, _edited=None, props=None, class_id=None):
        self.id = id
        self.name = name
        self.geom = geom
        self.props = props
        self._created = _created
        self._edited = _edited
        self.class_id = class_id

    def __call__(self, *args, **kwargs):
        return self

    @property
    def query(self):
        return self

    def all(self):
        return [self]

    def get_or_404(self, id):
        if self.id == id:
            return self
        else:
            abort(404)


class MockDb:
    """Мокает модель sqlalchemy и методы session."""

    @property
    def session(self):
        return self

    def add(self, arg):
        return self

    def commit(self):
        return self

    def merge(self, arg):
        return self

    def delete(self, arg):
        return self


POLYGON_FOR_TEST = {
    "geom": {
        "type": "Polygon",
        "class_id": 1,
        "coordinates": [
            [
                [
                    40.42968749999999,
                    63.31268278043484
                ],
                [
                    35.15625,
                    57.89149735271034
                ],
                [
                    46.7578125,
                    54.265224078605684
                ],
                [
                    60.1171875,
                    57.61010702068388
                ],
                [
                    55.8984375,
                    63.470144746565424
                ],
                [
                    40.42968749999999,
                    63.31268278043484
                ]
            ]
        ]
    },
    "name": "test polygon"
}


def post_json(url, data, headers):
    data = json.dumps(data)
    response = app.test_client().post(url, headers=headers, data=data)
    return response


def get_json(url, headers):
    response = app.test_client().get(url, headers=headers)
    return response


def put_json(url, data, headers):
    data = json.dumps(data)
    response = app.test_client().put(url, headers=headers, data=data)
    return response


def delete_json(url, headers):
    response = app.test_client().delete(url, headers=headers)
    return response


@pytest.mark.parametrize('data, expected_code', [
    (
        POLYGON_FOR_TEST, 200
    ),
    (
        {
            "geom": {
                "type": "Polygon",
                "coordinates": []
            },
            "name": "test polygon"
        },
        400
    ),
    (
            {
                "geom": {},
                "name": "test polygon"
            },
            400
    ),
    (
            {}, 400
    ),
])
def test_create_polygon(monkeypatch, data, expected_code):
    """Тест создания полигона"""

    monkeypatch.setattr('gis_polygon.api.db', MockDb())
    headers = {'Content-Type': 'application/json'}
    response = post_json('/api/polygon', data, headers)
    assert response.status_code == expected_code


@pytest.mark.parametrize('data, expected_code, endpoint', [
    (
        POLYGON_FOR_TEST, 200, '/api/polygon?projection=epsg:4326'
    ),
    (
        POLYGON_FOR_TEST, 200, '/api/polygon?projection=epsg:32644'
    ),
    (
        POLYGON_FOR_TEST, 400, '/api/polygon?projection=epsg:12345'
    ),
    (
        POLYGON_FOR_TEST, 400, '/api/polygon?projection=epsg4326'
    ),
    (
        POLYGON_FOR_TEST, 200, '/api/polygon?anotherArgs=canWorks'
    ),
])
def test_create_polygon_with_projection(monkeypatch, data, expected_code, endpoint):
    """Тест создания полигона, полученного в другой проекции."""

    monkeypatch.setattr('gis_polygon.api.db', MockDb())
    headers = {'Content-Type': 'application/json'}
    response = post_json(endpoint, data, headers)
    assert response.status_code == expected_code


def test_get_polygons(monkeypatch):
    polygon = Polygon([(0, 0), (1, 1), (1, 0)])

    with app.app_context():
        monkeypatch.setattr(
            'gis_polygon.api.GisPolygon',
            MockPolygon(id=1, geom=from_shape(shape(polygon), srid=current_app.config['DEFAULT_SRID']))
        )

    headers = {'Content-Type': 'application/json'}
    response = get_json('/api/polygon', headers)
    assert response.json == {
        'polygons': [
            {
                'polygon_id': 1,
                'class_id': None,
                'geom':
                    {
                        'type': 'Polygon',
                        'coordinates': [[[0.0, 0.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]]
                    },
                'props': None,
                'name': None
            }
        ]
    }


@pytest.mark.parametrize('endpoint, expected_response', [
    (
        '/api/polygon?projection=epsg:4326',
        {
            'polygons': [
                {
                    'polygon_id': 1,
                    'class_id': None,
                    'geom':
                        {
                            'type': 'Polygon',
                            'coordinates': [[[0.0, 0.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]]
                        },
                    'props': None,
                    'name': None
                }
            ]
        }
    ),
    (
        '/api/polygon?projection=epsg:32644',
        {
            'polygons': [
                {
                    'polygon_id': 1,
                    'class_id': None,
                    'geom': None,
                    'props': None,
                    'name': None
                }
            ]
        }
    ),
    (
        '/api/polygon?projection=epsg:12345',
        {'error': 'incorrect projection'}
    ),
    (
        '/api/polygon?projection=epsg4326',
        {'error': 'incorrect projection'}
    ),
    (
        '/api/polygon?anotherArgs=canWorks',
        {
            'polygons': [
                {
                    'polygon_id': 1,
                    'class_id': None,
                    'geom':
                        {
                            'type': 'Polygon',
                            'coordinates': [[[0.0, 0.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]]
                        },
                    'props': None,
                    'name': None
                }
            ]
        }
    ),
])
def test_get_polygons_with_projection(monkeypatch, endpoint, expected_response):
    polygon = Polygon([(0, 0), (1, 1), (1, 0)])

    with app.app_context():
        monkeypatch.setattr(
            'gis_polygon.api.GisPolygon',
            MockPolygon(id=1, geom=from_shape(shape(polygon), srid=current_app.config['DEFAULT_SRID']))
        )

    headers = {'Content-Type': 'application/json'}
    response = get_json(endpoint, headers)
    assert response.json == expected_response


@pytest.mark.parametrize('endpoint, expected_response', [
    (
        '/api/polygon/1?projection=epsg:4326',
        {
            'polygon_id': 1,
            'class_id': None,
            'geom':
                {
                    'type': 'Polygon',
                    'coordinates': [[[0.0, 0.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]]
                },
            'props': None,
            'name': None
        },
    ),
    (
        '/api/polygon/1?projection=epsg:32644',
        {
            'polygon_id': 1,
            'class_id': None,
            'geom': None,
            'props': None,
            'name': None
        }
    ),
    (
        '/api/polygon/1?projection=epsg:12345',
        {'error': 'incorrect projection'}
    ),
    (
        '/api/polygon/1?projection=epsg4326',
        {'error': 'incorrect projection'}
    ),
    (
        '/api/polygon/1?anotherArgs=canWorks',
        {
            'polygon_id': 1,
            'class_id': None,
            'geom':
                {
                    'type': 'Polygon',
                    'coordinates': [[[0.0, 0.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]]
                },
            'props': None,
            'name': None
        }
    ),
])
def test_get_polygon_with_projection(monkeypatch, endpoint, expected_response):
    polygon = Polygon([(0, 0), (1, 1), (1, 0)])

    with app.app_context():
        monkeypatch.setattr(
            'gis_polygon.api.GisPolygon',
            MockPolygon(id=1, geom=from_shape(shape(polygon), srid=current_app.config['DEFAULT_SRID']))
        )

    headers = {'Content-Type': 'application/json'}
    response = get_json(endpoint, headers)
    assert response.json == expected_response


def test_get_polygon(monkeypatch):
    polygon = Polygon([(0, 0), (1, 1), (1, 0)])

    with app.app_context():
        monkeypatch.setattr(
            'gis_polygon.api.GisPolygon',
            MockPolygon(id=1, geom=from_shape(shape(polygon), srid=current_app.config['DEFAULT_SRID']))
        )

    headers = {'Content-Type': 'application/json'}
    response = get_json('/api/polygon/1', headers)
    assert response.json == {
        'polygon_id': 1,
        'class_id': None,
        'geom':
            {
                'type': 'Polygon',
                'coordinates': [[[0.0, 0.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]]
            },
        'props': None,
        'name': None
    }


@pytest.mark.parametrize('data, expected_code', [
    (
        POLYGON_FOR_TEST, 200
    ),
    (
        {
            "geom": {
                "type": "Polygon",
                "coordinates": []
            },
            "name": "test polygon"
        }, 400
    ),
    (
        {
            "geom": {},
            "name": "test polygon"
        }, 400
    ),
])
def test_edit_polygon(monkeypatch, data, expected_code):
    polygon = Polygon([(0, 0), (1, 1), (1, 0)])

    with app.app_context():
        monkeypatch.setattr(
            'gis_polygon.api.GisPolygon',
            MockPolygon(id=1, geom=from_shape(shape(polygon), srid=current_app.config['DEFAULT_SRID']))
        )

    monkeypatch.setattr(
        'gis_polygon.api.db',
        MockDb()
    )

    headers = {'Content-Type': 'application/json'}
    response = put_json('/api/polygon/1', data, headers)
    assert response.status_code == expected_code


@pytest.mark.parametrize('polygon_id, expected_code', [
    (
        1, 200
    ),
    (
        101, 404
    ),
])
def test_delete_polygon(monkeypatch, polygon_id, expected_code):
    monkeypatch.setattr('gis_polygon.api.db', MockDb())
    monkeypatch.setattr('gis_polygon.api.GisPolygon', MockPolygon(id=1))
    headers = {'Content-Type': 'application/json'}
    response = delete_json('/api/polygon/{0}'.format(polygon_id), headers)
    assert response.status_code == expected_code

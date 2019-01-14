import logging

from flask import Flask

from gis_polygon import api
from gis_polygon.extensions import db, migrate

logger = logging.getLogger('server')
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(filename)s[LINE:%(lineno)d] %(message)s")


def create_app(config=None, testing=False, cli=False):
    app = Flask('server')
    configure_app(app, testing)
    configure_extensions(app, cli)
    db.init_app(app)
    app.register_blueprint(api.polygon_blueprint)
    return app


def configure_app(app, testing=False):
    """
    Конфигурирует приложение.
    """
    # default configuration
    app.config.from_object('gis_polygon.config')
    if testing is True:
        # override with testing config
        app.config.from_envvar('TEST_CONFIG', silent=True)
    else:
        # override with env variable, fail silently if not set
        app.config.from_envvar('SERVER_CONFIG', silent=True)


def configure_extensions(app, cli):
    """
    Настраивает расширения Flask.
    """
    db.init_app(app)

    if cli is True:
        migrate.init_app(app, db)

import click
from flask.cli import FlaskGroup

from gis_polygon.app import create_app


def create_server(information):
    """
    Вызывает функцию для создания экземпляра приложения.
    """
    return create_app(cli=True)


@click.group(cls=FlaskGroup, create_app=create_server)
def cli():
    """
    Главный entrypoint для cli.
    """


if __name__ == '__main__':
    cli()

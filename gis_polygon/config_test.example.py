class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/gis_polygon'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    PROPAGATE_EXCEPTIONS = False
    DEBUG = True
    TESTING = True
    DEFAULT_SRID = 4326

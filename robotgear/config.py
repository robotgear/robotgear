class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite://db.db'

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

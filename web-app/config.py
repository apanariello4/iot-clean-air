from os import environ, path
import os


class Config:

    # General Flask Config
    SECRET_KEY = b'ergergergergegg/'  # session cookie
    # USE_PROXYFIX = True

    APPLICATION_ROOT = '/'

    FLASK_APP = 'app.py'
    FLASK_RUN_HOST = '0.0.0.0'
    FLASK_RUN_PORT = 80

    FLASK_DEBUG = 0
    FLASK_ENV = "development"
    # FLASK_ENV = "production"

    DEBUG = True  # True enables dynamic debugger
    TESTING = False  # True

    SESSION_TYPE = 'sqlalchemy'  # 'redis'
    SESSION_SQLALCHEMY_TABLE = 'sessions'
    SESSION_COOKIE_NAME = 'my_cookieGetFace'
    SESSION_PERMANENT = True

    # Database

    # = 'mysql://username:password@localhost/db_name'
    SQLALCHEMY_DATABASE_URI = "sqlite:///example.sqlite"

    #SQLALCHEMY_ECHO = False
    #SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CACHE_TYPE = "simple"  # Flask-Caching related configs
    #CACHE_DEFAULT_TIMEOUT = 100

    # MQTT

    MQTT_BROKER_URL = '151.81.17.207'
    MQTT_BROKER_PORT = 1883
    MQTT_USERNAME = 'user'
    MQTT_PASSWORD = 'secret'
    MQTT_REFRESH_TIME = 1.0  # refresh time in seconds

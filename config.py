import os
from dotenv import load_dotenv
from app.parse import jobs


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class BaseConfig(object):
    'Base config class'
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
        '8cb0bdb613a84295a19863f6c5986105'
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['cjpf@charliejuliet.net']
    DEBUG = True
    TESTING = False


class DevelopmentConfig(BaseConfig):
    'Development environment specific config'
    DEBUG = True
    TESTING = True


class ProductionConfig(BaseConfig):
    'Production specific config'
    DEBUG = False
    TESTING = False


class TestConfig(BaseConfig):
    'Unit Testing Config'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

import os
from dotenv import load_dotenv
from app.parse import jobs

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class BaseConfig(object):
    'Base config class'
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
        '8cb0bdb613a84295a19863f6c5986105'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['cjpf@charliejuliet.net']
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    ESS_LOG = os.environ.get('ESS_LOG') or \
        'ess.log'
    JOBS = [
        {
            'id': 'job1',
            'func': jobs.hello_job,
            'trigger': 'cron',
            'day_of_week': '*',
            'hour': '*',
            'minute': '10,25,40,55'
        }
    ]
    # SCHEDULER_JOBSTORES = {
    #     'default': SQLAlchemyJobStore(url='sqlite:///jobs.db')
    # }
    SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 1}
    }
    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 3
    }
    SCHEDULER_API_ENABLED = True
    DEBUG = True
    TESTING = False


class DevelopmentConfig(BaseConfig):
    'Development environment specific config'
    DEBUG = True
    TESTING = True
    SECRET_KEY = "cb43703ec988496e9b7afa85590939ea"


class ProductionConfig(BaseConfig):
    'Production specific config'
    DEBUG = False
    TESTING = False
    # SECRET_KEY = open('/path/to/secret/key/file').read()


class TestConfig(BaseConfig):
    'Unit Testing Config'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SCHEDULER_API_ENABLED = False

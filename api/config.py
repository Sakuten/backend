from cryptography.fernet import Fernet
import os
from pathlib import Path
from datetime import datetime, time, timedelta, timezone
import api


class BaseConfig(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@db/postgres'
    DB_GEN_POLICY = os.getenv('DB_GEN_POLICY', 'first_time')
    DB_FORCE_INIT = os.getenv('DB_FORCE_INIT', 'false') == 'true'
    SECRET_KEY = Fernet.generate_key()
    ROOT_DIR = Path(api.__file__).parent.parent
    ID_LIST_FILE = ROOT_DIR / Path('cards/ids.json')
    ERROR_TABLE_FILE = ROOT_DIR / Path('errors.json')
    WINNERS_NUM = 90
    RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')
    RECAPTCHA_THRESHOLD = 0.09  # more than 0.09
    TIMEZONE = timezone(timedelta(hours=+9), 'JST')
    START_DATETIME = datetime(2018, 9, 16, 8,  40, 0, tzinfo=TIMEZONE)
    END_DATETIME = datetime(2018, 9, 17, 16, 00, 0, tzinfo=TIMEZONE)
    DRAWING_TIME_EXTENSION = timedelta(minutes=10)
    TIMEPOINT_END_MARGIN = timedelta(minutes=1)
    TIMEPOINTS = [
        (time(8,  50), time(9,  20)),
        (time(10, 15), time(10, 45)),
        (time(12, 25), time(12, 55)),
        (time(13, 50), time(14, 20)),
    ]
    ONE_DAY_KIND = ['visitor']


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    ENV = 'development'
    ID_LIST_FILE = BaseConfig.ROOT_DIR / 'cards/test_users.json'


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    ENV = 'development'
    ID_LIST_FILE = BaseConfig.ROOT_DIR / 'cards/test_users.json'
    WINNERS_NUM = 3  # just small value
    # Recaptcha test key for automated testing.
    # https://developers.google.com/recaptcha/docs/faq#id-like-to-run-automated-tests-with-recaptcha-v2-what-should-i-do
    RECAPTCHA_SECRET_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'


class PreviewDeploymentConfig(BaseConfig):
    DEBUG = True
    TESTING = False
    ID_LIST_FILE = BaseConfig.ROOT_DIR / 'cards/test_users.json'
    WINNERS_NUM = 3  # just small value
    # DATABASE_URL is to be set by Heroku
    # SECRET_KEY is to be set in config vars
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ENV = 'development'
    START_DATETIME = datetime(2018, 8, 2, 0, 0, 0, tzinfo=BaseConfig.TIMEZONE)
    END_DATETIME = datetime(2018, 8, 2, 23, 59, 59, tzinfo=BaseConfig.TIMEZONE)
    DRAWING_TIME_EXTENSION = timedelta(minutes=10)
    TIMEPOINTS = [
        (time(14,  30), time(14,  35)),
    ]


class DeploymentConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ENV = 'production'
    WINNERS_NUM = 4
    START_DATETIME = datetime(2018, 9, 14, 21,  0, 0, tzinfo=TIMEZONE)
    END_DATETIME = datetime(2018, 9, 14, 22, 30, 0, tzinfo=TIMEZONE)
    DRAWING_TIME_EXTENSION = timedelta(minutes=10)
    TIMEPOINT_END_MARGIN = timedelta(minutes=1)
    TIMEPOINTS = [
        (time(21,  0), time(21, 10)),
        (time(21, 25), time(21, 35)),
        (time(21, 50), time(22,  0)),
        (time(22, 15), time(22, 25)),
    ]

from cryptography.fernet import Fernet
import os
from pathlib import Path
from datetime import datetime, time, timedelta, timezone
import json

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
    CLASSROOM_TABLE_FILE = ROOT_DIR / Path('classrooms.json')
    WINNERS_NUM = 85
    WAITING_NUM = 30
    RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')
    RECAPTCHA_THRESHOLD = 0.09  # more than 0.09
    TIMEZONE = timezone(timedelta(hours=+9), 'JST')
    # Don't forget to update START/END DATETIME every year
    # DONT MERGE THIS TO MASTER/DEVELOP - THIS CONFIGURATION IS TEMPORARILY
    START_DATETIME = datetime(2019, 4, 18, 12, 00, 0, tzinfo=TIMEZONE)
    END_DATETIME = datetime(2019, 4, 18, 13, 00, 0, tzinfo=TIMEZONE)
    DRAWING_TIME_EXTENSION = timedelta(minutes=10)
    TIMEPOINT_END_MARGIN = timedelta(minutes=1)
    TIMEPOINTS = [
        (time(12, 15), time(12, 35)),
    ]
    ONE_DAY_KIND = ['visitor']


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    ENV = 'development'
    ID_LIST_FILE = BaseConfig.ROOT_DIR / 'cards/test_users.json'
    # Don't forget to update START/END DATETIME every year
    # Update BaseConfig too
    START_DATETIME = datetime(2018, 9, 17, 0, 0, 0, tzinfo=BaseConfig.TIMEZONE)
    END_DATETIME = datetime(2019, 9, 16, 23, 59, 59,
                            tzinfo=BaseConfig.TIMEZONE)
    TIMEPOINTS = [
        # applications are accepted in these durations and TIMEPOINT_END_MARGIN
        # lottery is carried out during DRAWING_TIME_EXTENTION
        # modify here when debugging
        (time(0, 0), time(23, 49)),
    ]


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    ENV = 'development'
    ID_LIST_FILE = BaseConfig.ROOT_DIR / 'cards/test_users.json'
    WINNERS_NUM = 5  # just small value
    WAITING_NUM = 3
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


def _get_timepoints_from_json(json_str):
    """
        Get TIMEPOINTS list from JSON string.

        Expected JSON looks like:
        ```json
        [
          ["0:00", "5:59"],
          ["6:00", "11:59"],
          ["12:00", "17:59"],
          ["18:00", "24:00"]
        ]
        ```
    """

    return json_str and \
        [tuple(datetime.strptime(t, '%H:%M').time() for t in pair)
         for pair
         in json.loads(json_str)]


def _parse_datetime(datetime_str):
    """
        Parse datetime string to datetime,
        and set BaseConfig.TIMEZONE
    """

    return datetime_str and \
        datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S') \
        .astimezone(BaseConfig.TIMEZONE)


class DeploymentConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ENV = 'production'
    START_DATETIME = _parse_datetime(os.environ.get('START_DATETIME')) or \
        BaseConfig.START_DATETIME
    END_DATETIME = _parse_datetime(os.environ.get('END_DATETIME')) or \
        BaseConfig.END_DATETIME
    TIMEPOINTS = _get_timepoints_from_json(os.environ.get('TIMEPOINTS')) or \
        BaseConfig.TIMEPOINTS

from cryptography.fernet import Fernet
import os


class BaseConfig(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@db/postgres'
    SECRET_KEY = Fernet.generate_key()


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    ENV = 'development'


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    ENV = 'development'


class PreviewDeploymentConfig(BaseConfig):
    DEBUG = True
    TESTING = False
    # DATABASE_URL is to be set by Heroku
    # SECRET_KEY is to be set in config vars
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ENV = 'development'


class DeploymentConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    # None, to be configured in config.cfg in instance directory
    SQLALCHEMY_DATABASE_URI = None
    SECRET_KEY = None
    ENV = 'production'

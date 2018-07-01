import os
import sys
import tempfile
import json
from cryptography.fernet import Fernet

import pytest

# Append current path so that we can execute tests from repository root
sys.path.append(os.getcwd())

from api import app
from api.models import User, Classroom, Lottery, Application
from api.auth import decrypt_token
from api.schemas import (
    user_schema,
    classrooms_schema,
    classroom_schema,
    lotteries_schema,
    lottery_schema
)


pre_config = os.getenv('FLASK_CONFIGURATION', 'default')

# ===============================  settings and utils
@pytest.fixture
def client():
    """make a client for testing
        client (class flask.app.Flask): application <Flask 'api.app'>
        test_client (class 'Flask.testing.FlaskClient'): test client <FlaskClient <Flask 'api.app'>>
    """

    # set app config to 'testing'.
    os.environ['FLASK_CONFIGURATION'] = 'testing'
    client = app.create_app()
    test_client = client.test_client()

    yield test_client


def teardown():
    os.environ['FLASK_CONFIGURATION'] = pre_config

def login(client, username, password):
    """logging in as 'username' with 'password'
        client (class Flask.testing.FlaskClient): the client generated by 'client' [help wanted]
        username (str): the username to login
        password (str): the password for the 'username'
    """
    return client.post('/auth/', json={
        'username': username,
        'password': password
    }, follow_redirects=True).get_json()


def as_user_get(client, username, password, url):
    """make a response as logined user
         1. login as the user
         2. make GET request with 'token' made in 1.
         3. return response
         client (class Flask.testing.FlaskClient): the client generated by 'client' [help wanted]
         username (str): the username to login
         password (str): the password for the 'username'
   """
    login_data = login(client, username, password)
    token = login_data['token']
    header = 'Bearer ' + token
   
    return client.get(url, headers={'Authorization': header})

# ================================= tests

# ---------- User API
def test_login(client):
    """ attempt to login as
            * admin     (with proper/wrong password)
            * test_user('example1')     (with proper/wrong password)
            * non_exist_user('nonexist')

        target_url: /api/auth/
    """
    resp = login(client, 'admin', 'admin')
    assert 'Login Successful' in resp['message']
    resp = login(client, 'example1', 'example1')
    assert 'Login Successful' in resp['message']
    resp = login(client, 'notexist', 'notexist')
    assert 'Login Unsuccessful' in resp['message']

    resp = login(client, 'admin', 'wrong_admin')
    assert 'Login Unsuccessful' in resp['message']
    resp = login(client, 'example1', 'wrong_example1')
    assert 'Login Unsuccessful' in resp['message']


def test_auth_token(client):
    """test vaild token is returned
       1. test token is contained in response
       2. test token is effective
       target_url: /api/auth/
    """
    resp = login(client, 'admin', 'admin')
    assert 'token' in resp

    token = resp['token']
    with client.application.app_context():
        data = decrypt_token(token)
        user = User.query.filter_by(id=data['data']['user_id']).first()

    assert user is not None


# UNDER CONSTRUCTION
def test_status(client):
    user = {'username':'admin',
            'password':'admin'}
    resp = as_user_get(client, user['username'], user['password'], '/api/status')
    assert 'id' in resp.get_json()['status']

    with client.application.app_context():
        db_status = User.query.filter_by(id=user['username']).first()

    assert resp.get_json()['status'] == user_schema.dump(db_status)[0].dump()



# ---------- Lottery API


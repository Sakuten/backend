import os
import sys
import tempfile
import json

import pytest

# Append current path so that we can execute tests from repository root
sys.path.append(os.getcwd())

from api import app
from api.models import User, Classroom, Lottery, Application
from api.auth import decrypt_token

@pytest.fixture
def client():
    """make a client for testing
        client (class flask.app.Flask): application <Flask 'api.app'>
        test_client (class 'Flask.testing.FlaskClient'): test client <FlaskClient <Flask 'api.app'>>
    """
    client = app.create_app({
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite://',
        'TESTING': True,
        'SECRET_KEY': Fernet.generate_key(),
        'ENV': 'development'
        })
    test_client = client.test_client()

    yield test_client

def post_json(client, url, json_dict):
    """send POST request to 'url' with 'json_dict' as data
        Args:
        client (obj): The client application for test. Generated in 'client' method
        url (str): URL to post JSON.
        json_dict (dict): A JSON data to post
    """
    return client.post(url, json=json_dict, content_type='application/json') # here should be checked , because 'dict' might be wrong usage


def login(client, username, password):
    """logging in as 'username' with 'password'
        
    """
    return client.post('/auth/', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def test_login(client):
    resp = login(client, 'admin', 'admin')
    assert b'token' in resp.get_json
    resp = login(client, 'example1', 'example1')
    assert b'token' in resp.get_json

def test_toppage(client):
    resp = client.get('/')
    assert b'DOC' in resp.data


def test_auth(client):
    """test whether authorization works correctly
       1. test token is contained in response
       2. test token is effective
    """
    resp = post_json(client, '/auth/', json_dict={
        'username':'admin', 'password':'admin'
    })
    assert b'token' in resp.get_json

    token = resp.data['token']
    data = decrypt_token(token)
    user = User.query.filter_by(id=data['data']['user_id']).first()

    assert user is not None


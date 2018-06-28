import os
import tempfile
import json

import pytest

from api import app
from api.models import User, Classroom, Lottery, Application
from api.auth import decrypt_token

@pytest.fixture
def client():
    """make a client for testing
        client (class flask.app.Flask): application <Flask 'api.app'>
        test_client (class 'Flask.testing.FlaskClient'): test client <FlaskClient <Flask 'api.app'>>
    """
    client = app.create_app()
    db_fd, client.config['DATABASE'] = tempfile.mkstemp()
    client.config['TESTING'] = True
    # I have to defined, but I don't know which to set.so, I'll comment out this
    # client.config['SQLALCHEMY_DATABASE_URI'] = ''
    test_client = client.test_client()

    yield test_client

    os.close(db_fd)
    os.unlink(client.config['DATABASE'])

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


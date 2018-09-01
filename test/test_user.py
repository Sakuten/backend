import pytest
from unittest import mock
from datetime import date
from utils import (
    as_user_get,
    login_with_form,
    login,
    admin,
    test_user,
    test_student
)
from api.models import User, db
from api.schemas import user_schema
from api.auth import decrypt_token
# ---------- User API


def test_login(client):
    """ attempt to login as
            * admin
            * test_user('example1')
            * non_exist_user('nonexist')

        target_url: /auth
    """
    resp = login(client, admin['secret_id'], admin['g-recaptcha-response'])
    assert 'Login Successful' in resp['message']
    resp = login(client, test_user['secret_id'],
                 test_user['g-recaptcha-response'])
    assert 'Login Successful' in resp['message']
    resp = login(client, 'notexist', 'notexist')
    assert 'Login Unsuccessful' in resp['message']


def test_login_form(client):
    """ attempt to login as
            * admin
            * test_user('example1')
            * non_exist_user('nonexist')
        with Content-Type: application/x-www-form-urlencoded
        target_url: /auth
    """
    resp = login_with_form(
        client, admin['secret_id'], admin['g-recaptcha-response'])
    assert 'Login Successful' in resp['message']
    resp = login_with_form(
        client, test_user['secret_id'], test_user['g-recaptcha-response'])
    assert 'Login Successful' in resp['message']
    resp = login_with_form(client, 'notexist', 'notexist')
    assert 'Login Unsuccessful' in resp['message']


def test_login_invalid(client):
    """logging in with invalid request params as
            * test_user
        target_url: /auth
    """
    resp = client.post('/auth', json={
        'secret_id': test_user['secret_id'],
    }, follow_redirects=True)
    assert resp.status_code == 400
    assert 'Invalid request' in resp.get_json()['message']

    resp = client.post('/auth', json={
        'secret_id': test_user['secret_id'],
        'g-recaptcha-response': test_user['g-recaptcha-response'],
    }, follow_redirects=True, content_type='application/xml')
    assert resp.status_code == 400
    assert 'Unsupported content type' in resp.get_json()['message']


def test_auth_token(client):
    """test vaild token is returned
       1. test: token is contained in response
       2. test: token is vaild

       target_url: /auth
    """
    resp = login(client, admin['secret_id'], admin['g-recaptcha-response'])
    assert 'token' in resp

    token = resp['token']
    with client.application.app_context():
        data = decrypt_token(token)
        user = User.query.filter_by(id=data['data']['user_id']).first()

    assert user is not None


def test_status(client):
    """test it return a vaild response
        1. test: response contains 'id'
        2. test: response matches the data in DB

        auth: required
        target_url: /status
    """
    user = test_user
    resp = as_user_get(client, user['secret_id'],
                       user['g-recaptcha-response'], '/status')
    assert 'id' in resp.get_json()

    with client.application.app_context():
        db_status = User.query.filter_by(secret_id=user['secret_id']).first()

        assert resp.get_json() == user_schema.dump(db_status)[0]


def test_status_invalid_header(client):
    """attempt to get status with wrong header.
        this cause error in /api/auth. not in /api/routes/api
        target_url: /status
    """
    resp = client.get('/status',
                      headers={'Authorization_wrong': 'Bearer no_token_here'})
    assert resp.status_code == 401
    assert 'token_required' in resp.headers['WWW-Authenticate']


def test_status_invalid_auth(client):
    """attempt to get status with wrong auth data.
        this cause error in /api/auth. not in /api/routes/api
        target_url: /status
    """
    resp = client.get('/status',
                      headers={'Authorization': 'Bearer wrong_token_here'})
    assert resp.status_code == 401
    assert 'invalid_token' in resp.headers['WWW-Authenticate']


def test_translate_user_ids(client):
    """test it return a vaild response
        test: response contains correct public_id
        target_url: /public_id
    """
    token_user = admin
    target_user = test_user
    token = login(client, token_user['secret_id'], '')['token']
    resp = client.get('public_id/' + target_user['secret_id'],
                      headers={'Authorization': f'Bearer {token}'})

    with client.application.app_context():
        public_id = User.query.filter_by(secret_id=target_user['secret_id']
                                         ).first().public_id

    assert resp.status_code == 200
    assert resp.get_json()['public_id'] == public_id


def test_translate_user_ids_invalid_secret_id(client):
    """attempt to translate invalid secret_id
        target_url: /public_id
    """
    token_user = admin
    token = login(client, token_user['secret_id'], '')['token']
    resp = client.get(f'public_id/Non_EXST_KEY',
                      headers={'Authorization': f'Bearer {token}'})

    assert resp.status_code == 404
    assert 'no such user found' in resp.get_json()['message']


def test_auth_used_user(client):
    """for 'todays_user' method.
        attempt to get token as used uer
        target_url: /auth
    """
    login_user = test_user
    date_before = date(2018, 1, 1)
    date_login = date(2018, 1, 2)
    with client.application.app_context():
        user = User.query.filter_by(secret_id=login_user['secret_id']).first()
        user.first_access = date_before
        db.session.add(user)
        db.session.commit()

    with mock.patch('api.auth.date',
                    return_value=date_login):
        resp = client.post('/auth', json={
                           'id': login_user['secret_id'],
                           'g-recaptcha-response':
                               login_user['g-recaptcha-response']
                           }, follow_redirects=True)

    assert resp.status_code == 400
    assert resp.get_json()['message'] == 'Login Unsuccessful'


@pytest.mark.skip(reason="field 'kind' is not added yet")
def test_auth_overtime_as_student(client):
    """attempt to use same `user`(which isn't in ONE_DAY_KIND) for 2 days
    target_url: /auth
    """
    login_user = test_student
    date_before = date(2038, 1, 1)
    date_login = date(2038, 1, 2)
    with client.application.app_context():
        user = User.query.filter_by(secret_id=login_user['secret_id']).first()
        user.first_access = date_before
        db.session.add(user)
        db.session.commit()

    with mock.patch('api.auth.date',
                    return_value=date_login):
        resp = client.post('/auth', json={
                           'id': login_user['secret_id'],
                           'g-recaptcha-response':
                               login_user['g-recaptcha-response']
                           }, follow_redirects=True)

    assert resp.status_code == 200
    assert resp.get_json()['message'] == 'Login Successful'

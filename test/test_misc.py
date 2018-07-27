from flask import current_app
import datetime
from unittest import mock
from utils import login, test_user


def test_trailing_slash(client):
    """test the behavior of trailing slash
        target_url: /api/classrooms, /api/classrooms/
        both urls are expected to behave samely
    """
    resp = client.get('/api/classrooms', follow_redirects=False)
    resp_with_slash = client.get('/api/classrooms/', follow_redirects=False)

    assert resp_with_slash.status_code != 300
    assert resp.get_json() == resp_with_slash.get_json()


def test_token_revoke(client):
    """test tokens are revoked correctly
        target_url: /api/status (for this test)

        1. test: whether user can use token before the end
        2. test: wheter user cannot use token after the end
    """
    user = test_user
    token = login(client,user['username'], user['g-recaptcha-response'])['token']
    with client.application.app_context():
        end = current_app.config['END_DATETIME']
    before_end = end - datetime.timedelta.resolution
    after_end = end + datetime.timedelta.resolution
    print(f'before_end: {before_end}')
    print(f'after_end: {after_end}')
    with mock.patch('api.time_management.get_current_datetime',
                    return_value=before_end):
        resp = client.get('/status',headers={'Authorization': 'Bearer '+ token})
        assert resp.status_code == 200

    with mock.patch('api.time_management.get_current_datetime',
                    return_value=after_end):
        resp = client.get('/status',headers={'Authorization': 'Bearer '+ token})
        assert resp.status_code == 403

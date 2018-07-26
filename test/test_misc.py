from flask import current_app
import datetime
from unittest import mock
from utils import as_user_get, test_user


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
    with client.application.app_context():
        end = current_app.config['END_DATETIME']
    delta = datetime.timedelta(minutes=10)
    before_end = end - delta
    after_end = end + delta
    with mock.patch('api.time_management.get_current_datetime',
                    return_value=before_end):
        resp = as_user_get(client, user['username'],
                           user['g-recaptcha-response'], '/status')

        assert resp.status_code == 200

    with mock.patch('api.time_management.get_current_datetime',
                    return_value=after_end):
        resp = as_user_get(client, user['username'],
                           user['g-recaptcha-response'], '/status')

        assert resp.status_code == 403

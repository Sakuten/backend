import tempfile
from flask import current_app
import datetime
from unittest import mock
from utils import login, test_user
from api.utils import calc_sha256


def test_trailing_slash(client):
    """test the behavior of trailing slash
        target_url: /classrooms, /classrooms/
        both urls are expected to behave samely
    """
    resp = client.get('/classrooms', follow_redirects=False)
    resp_with_slash = client.get('/classrooms/', follow_redirects=False)

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
    before_end = end - datetime.timedelta.resolution
    after_end = end + datetime.timedelta.resolution
    with mock.patch('api.auth.get_current_datetime',
                    return_value=before_end):
        token = login(client, user['secret_id'],
                      user['g-recaptcha-response'])['token']
        resp = client.get(
            '/status', headers={'Authorization': 'Bearer ' + token})
        assert resp.status_code == 200

    with mock.patch('api.auth.get_current_datetime',
                    return_value=after_end):
        resp = client.get(
            '/status', headers={'Authorization': 'Bearer ' + token})
        assert resp.status_code == 403


def test_calc_sha256(client):
    """test `calc_sha256`
    """
    val_list = [{'value': 'abcdef',
                'hash': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'},  # noqa: E501
                {'value': 'testoftest',
                 'hash': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'}  # noqa: E501
               ]
    for val in val_list:
        with tempfile.NamedTemporaryFile(mode='w', prefix='test') as f:
            f.write(val['value'])

            assert calc_sha256(f.name) == val['hash']

import pytest
from api.error import error_response

def test_error_response(client):
    with client.application.app_context():
        resp, http_code = error_response(0)
        resp = resp.get_json()
        assert http_code is not None
        assert 'message' in resp
        assert 'code' in resp
        assert resp['code'] == 0

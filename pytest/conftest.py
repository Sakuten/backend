import os
import sys
import json
import pytest

# Append current path so that we can execute tests from repository root
sys.path.append(os.getcwd())

from api import app


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
    """reset environment
    """
    os.environ['FLASK_CONFIGURATION'] = pre_config


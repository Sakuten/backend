from api import app

import os
import pytest

pre_config = os.environ['FLASK_CONFIGURATION']

# ===============================  settings and utils


@pytest.fixture
def client():
    """make a client for testing
        client (class flask.app.Flask): application <Flask 'api.app'>
        test_client (class 'Flask.testing.FlaskClient'):
                        test client <FlaskClient <Flask 'api.app'>>
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

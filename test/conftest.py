
import sys
import os
import pytest

# Append current path so that we can execute tests from repository root
sys.path.append(os.getcwd())  # noqa: E402
from api import app
from cards.id import load_id_json_file

from utils import admin, test_user

pre_config = os.environ.get('FLASK_CONFIGURATION', None)

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
    json_path = client.config['ID_LIST_FILE']
    id_list = load_id_json_file(json_path)
    admin['secret_id'] = next(i for i in id_list if i['authority'] == 'admin')['secret_id']
    test_user['secret_id'] = next(i for i in id_list if i['authority'] != 'admin')['secret_id']

    test_client = client.test_client()

    yield test_client


def teardown():
    """reset environment
    """
    os.environ['FLASK_CONFIGURATION'] = pre_config


import sys
import os
import pytest

# Append current path so that we can execute tests from repository root
sys.path.append(os.getcwd())  # noqa: E402
from api import app
from cards.id import load_id_json_file

from utils import admin, checker, test_user, test_user1, \
                  test_user2, test_user3, test_user4, test_student

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
    admin_cred = next(i for i in id_list if i['authority'] == 'admin')
    admin['secret_id'] = admin_cred['secret_id']
    checker_cred = next(i for i in id_list if i['authority'] == 'checker')
    checker['secret_id'] = checker_cred['secret_id']
    student_cred = next(i for i in id_list if i['kind'] == 'student')
    test_student['secret_id'] = student_cred['secret_id']
    test_creds = (i for i in id_list if i['kind'] == 'visitor')
    for user in [test_user, test_user1, test_user2, test_user3, test_user4]:
        test_cred = next(test_creds)
        user['secret_id'] = test_cred['secret_id']

    with client.app_context():
        app.init_and_generate()

    test_client = client.test_client()

    yield test_client


def teardown():
    """reset environment
    """
    os.environ['FLASK_CONFIGURATION'] = pre_config

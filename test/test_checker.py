from unittest import mock
import pytest
from utils import test_user, checker, as_user_get
from api.models import Classroom, Lottery, User, Application, db


@pytest.mark.parametrize("def_status", ["pending", "won", "lose"])
def test_checker(client, def_status):
    """use `/checker` endpoint with winner user
        target_url: /checker/{classroom_id}/{secret_id}
    """
    index = 1
    target_user = test_user
    staff = checker
    secret_id = target_user['secret_id']

    with client.application.app_context():
        classroom = Classroom.query.filter_by(grade=5, index=0).first()
        classroom_id = classroom.id
        lottery_id = Lottery.query.filter_by(classroom_id=classroom_id,
                                             index=index).first().id
        user = User.query.filter_by(secret_id=secret_id).first()
        application = Application(user_id=user.id,
                                  lottery_id=lottery_id, status=def_status)
        db.session.add(application)
        db.session.commit()

    with mock.patch('api.routes.api.get_prev_time_index',
                    return_value=index):
        resp = as_user_get(client, staff['secret_id'],
                           staff['g-recaptcha-response'],
                           f'/checker/{classroom_id}/{secret_id}')

    assert resp.status_code == 200
    assert resp.get_json()['status'] == def_status
    assert resp.get_json()['classroom'] == '5A'


def test_checker_no_application(client):
    """attempt to use `/checker` endpoint without application for that
       target_url: /checker/{classroom_id}/{secret_id}
    """
    classroom_id = 1
    index = 1
    target_user = test_user
    secret_id = target_user['secret_id']
    staff = checker

    with mock.patch('api.routes.api.get_prev_time_index',
                    return_value=index):
        resp = as_user_get(client, staff['secret_id'],
                           staff['g-recaptcha-response'],
                           f'/checker/{classroom_id}/{secret_id}')
    assert resp.status_code == 404
    assert resp.get_json()['message'] == 'No application found'


def test_checker_invalid_user(client):
    """attempt to use `/checker` endpoint with wrong user
    """
    classroom_id = 1
    index = 1
    staff = checker
    secret_id = "NOTEXIST_SECRET_KEY"

    with mock.patch('api.routes.api.get_prev_time_index',
                    return_value=index):
        resp = as_user_get(client, staff['secret_id'],
                           staff['g-recaptcha-response'],
                           f'/checker/{classroom_id}/{secret_id}')

    assert resp.status_code == 404
    assert resp.get_json()['message'] == 'No such user found'

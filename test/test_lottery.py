from unittest import mock
import pytest
import datetime

from utils import (
    login,
    admin,
    test_user,
    test_user1,
    test_user2,
    test_user3,
    test_user4,
    test_user5,
    as_user_get,
    invalid_classroom_id,
    invalid_lottery_id,
    make_application
)

from api.models import Lottery, Classroom, User, Application, db
from api.schemas import (
    classrooms_schema,
    classroom_schema,
    application_schema,
    applications_schema,
    lotteries_schema,
    lottery_schema
)
from api.time_management import mod_time


# ---------- Lottery API

@pytest.mark.classrooms
@pytest.mark.all
def test_get_allclassrooms(client):
    """test proper infomation is returned from the API
        target_url: /classrooms
    """
    resp = client.get('/classrooms')

    with client.application.app_context():
        db_status = Classroom.query.all()
        classroom_list = classrooms_schema.dump(db_status)[0]

    assert resp.get_json() == classroom_list


def test_get_specific_classroom(client):
    """test proper infomation is returned from the API
        target_url: /classrooms/<id>
    """
    idx = 1  # classroom id to test
    resp = client.get(f'/classrooms/{idx}')

    with client.application.app_context():
        db_status = Classroom.query.filter_by(id=idx).first()
        classroom = classroom_schema.dump(db_status)[0]

    assert resp.get_json() == classroom


def test_get_specific_classroom_invalid_id(client):
    """test proper errpr is returned from the API
        target_url: /classrooms/<id>
    """
    idx = invalid_classroom_id  # classroom id to test
    resp = client.get(f'/classrooms/{idx}')

    assert resp.status_code == 404
    assert 'Classroom could not be found.' in resp.get_json()['message']


def test_get_alllotteries(client):
    """test proper infomation is returned from the API
        target_url: /lotteries
    """
    resp = client.get('/lotteries')

    with client.application.app_context():
        db_status = Lottery.query.all()
        lottery_list = lotteries_schema.dump(db_status)[0]

    assert resp.get_json() == lottery_list


def test_get_specific_lottery(client):
    """test proper infomation is returned from the API
        target_url: /lotteries/<id>
    """
    idx = 1  # lottery id to test
    resp = client.get(f'/lotteries/{idx}')

    with client.application.app_context():
        db_status = Lottery.query.filter_by(id=idx).first()
        lottery = lottery_schema.dump(db_status)[0]

    assert resp.get_json() == lottery


def test_get_specific_lottery_invalid_id(client):
    """test proper errpr is returned from the API
        target_url: /lotteries/<id>
    """
    idx = invalid_lottery_id  # lottery id to test
    resp = client.get(f'/lotteries/{idx}')

    assert resp.status_code == 404
    assert 'Lottery could not be found.' in resp.get_json()['message']


def test_apply_normal(client):
    """attempt to apply new application.
        1. test: error isn't returned
        2. test: DB is changed
        target_url: /lotteries/<id> [POST]
    """
    idx = 1
    user_info = test_user
    token = login(client, user_info['secret_id'],
                  user_info['g-recaptcha-response'])['token']
    with client.application.app_context():
        lottery = Lottery.query.get(idx)
    with mock.patch('api.routes.api.get_time_index',
                    return_value=lottery.index):
        resp = client.post(f'/lotteries/{idx}',
                           headers={'Authorization': f'Bearer {token}'},
                           data={'group_members': []})
        assert resp.status_code == 200

    with client.application.app_context():
        # get needed objects
        target_lottery = Lottery.query.filter_by(id=idx).first()
        user = User.query.filter_by(secret_id=user_info['secret_id']).first()
        # this application should be added by previous 'client.put'
        application = Application.query.filter_by(
            lottery=target_lottery, user_id=user.id).first()

        assert application is not None
        assert resp.get_json() == application_schema.dump(application)[0]


def test_apply_admin(client):
    """attempt to apply new application as admin
        test: 403 is returned
        target_url: /lotteries/<id> [POST]
    """
    idx = 1
    token = login(client, admin['secret_id'],
                  admin['g-recaptcha-response'])['token']
    resp = client.post(f'/lotteries/{idx}',
                       headers={'Authorization': f'Bearer {token}'},
                       data={'group_members': []})

    assert resp.status_code == 403


@pytest.mark.skip(reason='not implemented yet')
def test_apply_noperm(client):
    """attempt to apply without proper permission.
        target_url: /lotteries/<id>/apply [POST]
    """
    idx = 1
    token = login(client, admin['secret_id'],
                  admin['g-recaptcha-response'])['token']
    resp = client.post(f'/lotteries/{idx}',
                       headers={'Authorization': f'Bearer {token}'},
                       data={'group_members': []})

    assert resp.status_code == 403
    assert 'no permission' in resp.get_json().keys()  # not completed yet


def test_apply_invalid(client):
    """attempt to apply to non-exsit lottery
        target_url: /lotteries/<id> [PUT]
    """
    idx = invalid_lottery_id
    token = login(client, test_user['secret_id'],
                  test_user['g-recaptcha-response'])['token']
    resp = client.post(f'/lotteries/{idx}',
                       headers={'Authorization': f'Bearer {token}'},
                       data={'group_members': []})

    assert resp.status_code == 404
    assert 'Lottery could not be found.' in resp.get_json()['message']


def test_apply_already_done(client):
    """attempt to apply previously drawn application.
        1. test: error is returned
        target_url: /lotteries/<id> [POST]
    """
    idx = 1
    token = login(client, test_user['secret_id'],
                  test_user['g-recaptcha-response'])['token']

    with client.application.app_context():
        target_lottery = Lottery.query.filter_by(id=idx).first()
        target_lottery.done = True
        db.session.add(target_lottery)
        db.session.commit()

    resp = client.post(f'/lotteries/{idx}',
                       headers={'Authorization': f'Bearer {token}'},
                       data={'group_members': []})

    assert resp.status_code == 400
    assert 'already done' in resp.get_json()['message']


def test_apply_same_period(client):
    """attempt to apply to the same period with the previous application
        1. test: error is returned
        target_url: /lotteries/<id> [POST]
    """
    idx = 1
    token = login(client, test_user['secret_id'],
                  test_user['g-recaptcha-response'])['token']

    with client.application.app_context():
        target_lottery = Lottery.query.filter_by(id=idx).first()
        index = target_lottery.index
        booking_lottery = Lottery.query.filter_by(
            index=index).filter(Lottery.id != idx).first()
        user = User.query.filter_by(secret_id=test_user['secret_id']).first()
        application = Application(lottery=booking_lottery, user_id=user.id)
        db.session.add(application)
        db.session.commit()

    with mock.patch('api.routes.api.get_time_index',
                    return_value=index):
        resp = client.post(f'/lotteries/{idx}',
                           headers={'Authorization': f'Bearer {token}'},
                           data={'group_members': []})

    message = resp.get_json()['message']

    assert resp.status_code == 400
    assert 'already applying to a lottery in this period' in message


def test_apply_same_period_same_lottery(client):
    """attempt to apply to the same lottery in the same period
        1. test: error is returned
        target_url: /lotteries/<id> [POST]
    """
    idx = 1
    token = login(client, test_user['secret_id'],
                  test_user['g-recaptcha-response'])['token']

    with client.application.app_context():
        target_lottery = Lottery.query.filter_by(id=idx).first()
        index = target_lottery.index
        user = User.query.filter_by(secret_id=test_user['secret_id']).first()
        application = Application(lottery=target_lottery, user_id=user.id)
        db.session.add(application)
        db.session.commit()

    with mock.patch('api.routes.api.get_time_index',
                    return_value=index):
        resp = client.post(f'/lotteries/{idx}',
                           headers={'Authorization': f'Bearer {token}'},
                           data={'group_members': []})

    message = resp.get_json()['message']

    assert resp.status_code == 400
    assert 'already accepted' in message


def test_apply_time_invalid(client):
    """attempt to apply to lottery out of range
        target_url: /lotteries/<id> [POST]
    """
    idx = 1
    token = login(client, test_user['secret_id'],
                  test_user['g-recaptcha-response'])['token']

    with client.application.app_context():
        index = Lottery.query.get(idx).index
    with mock.patch('api.routes.api.get_time_index',
                    return_value=index + 1):
        resp = client.post(f'/lotteries/{idx}',
                           headers={'Authorization': f'Bearer {token}'},
                           data={'group_members': []})
        assert resp.status_code == 400
        assert "This lottery is not acceptable now." in \
               resp.get_json()['message']


def test_apply_group(client):
    """test group applying works correctly
        target_url: /lotteries/<id> [POST]
    """
    idx = 1
    user = test_user
    members = [test_user1['secret_id'],
               test_user2['secret_id'],
               test_user3['secret_id'],
               test_user4['secret_id'],
               test_user5['secret_id']
               ]
    token = login(client, user['secret_id'],
                  user['g-recaptcha-response'])['token']

    with client.application.app_context():
        index = Lottery.query.get(idx).index
        user_id = User.query.filter_by(secret_id=user['secret_id']).first()
    with mock.patch('api.routes.api.get_time_index',
                    return_value=index + 1):
        resp = client.post(f'/lotteries/{idx}',
                           headers={'Authorization': f'Bearer {token}'},
                           data={'group_members': members})

    with client.application.app_context():
        application = Application.query.filter_by(lottery_id=idx,
                                                  user_id=user_id).first
        assert application.is_rep is True
        assert application.group_members == members

        assert resp.status_code == 200
        assert resp.get_json() == application_schema.dump(application)[0]


def test_apply_group_invalid(client):
    """attempt to add invalid secret_id as one of members
        target_url: /lotteries/<id> [POST]
    """
    idx = 1
    user = test_user
    members = [test_user1['secret_id'],
               test_user2['secret_id'],
               test_user3['secret_id'],
               test_user4['secret_id'],
               "wrong_secret_id"
               ]
    token = login(client, user['secret_id'],
                  user['g-recaptcha-response'])['token']

    with client.application.app_context():
        index = Lottery.query.get(idx).index
    with mock.patch('api.routes.api.get_time_index',
                    return_value=index):
        resp = client.post(f'/lotteries/{idx}',
                           headers={'Authorization': f'Bearer {token}'},
                           data={'group_members': members})

    assert resp.status_code == 401
    assert 'wrong secret id is given.' in resp.get_json()['message']


def test_apply_group_same_period(client):
    """attempt to make application in the same period as member of group
        target_url: /lotteries/<id> [POST]

        1. make an application as member
        2. attempt to apply
    """
    idx = 1
    user = test_user
    members = [test_user1['secret_id'],
               test_user2['secret_id'],
               test_user3['secret_id'],
               test_user4['secret_id'],
               test_user5['secret_id']
               ]
    token = login(client, user['secret_id'],
                  user['g-recaptcha-response'])['token']

    with client.application.app_context():
        index = Lottery.query.get(idx).index
        lottery = Lottery.query.filter(index == index, id != idx).first()
        violation_user = User.query.filter_by(secret_id=members[0]).first()
        application = Application(lottery=lottery, user_id=violation_user.id)
        db.session.add(application)
        db.session.commit()

    with mock.patch('api.routes.api.get_time_index',
                    return_value=index):
        resp = client.post(f'/lotteries/{idx}',
                           headers={'Authorization': f'Bearer {token}'},
                           data={'group_members': members})

        assert resp.status_code == 400
        assert 'You’re already applying to a lottery in this period' in \
            resp.get_json()['message']


def test_get_allapplications(client):
    """test proper infomation is returned from the API to a normal user
        target_url: /applications
    """
    lottery_id = 1
    make_application(client, test_user['secret_id'], lottery_id)

    resp = as_user_get(client,
                       test_user['secret_id'],
                       test_user['g-recaptcha-response'],
                       '/applications')

    with client.application.app_context():
        db_status = Application.query.all()
        application_list = applications_schema.dump(db_status)[0]

    assert resp.get_json() == application_list


def test_get_allapplications_admin(client):
    """test 403 is returned from the API to admin
        target_url: /applications
    """
    lottery_id = 1
    make_application(client, admin['secret_id'], lottery_id)

    resp = as_user_get(client,
                       admin['secret_id'],
                       admin['g-recaptcha-response'],
                       '/applications')

    assert resp.status_code == 403


def test_get_specific_application_normal(client):
    """test proper infromation is returned from the API to a normal user
        target_url: /applications/<id>
    """
    lottery_id = 1
    application_id = make_application(
        client, test_user['secret_id'], lottery_id)

    resp = as_user_get(client,
                       test_user['secret_id'],
                       test_user['g-recaptcha-response'],
                       f'/applications/{application_id}')

    with client.application.app_context():
        db_status = Application.query.filter_by(id=application_id).first()
        application = application_schema.dump(db_status)[0]

    assert resp.get_json() == application


def test_get_specific_application_admin(client):
    """test 403 is returned from the API to admin
        target_url: /applications/<id>
    """
    lottery_id = 1
    application_id = make_application(
        client, admin['secret_id'], lottery_id)

    resp = as_user_get(client,
                       admin['secret_id'],
                       admin['g-recaptcha-response'],
                       f'/applications/{application_id}')

    assert resp.status_code == 403


def test_get_specific_application_invaild_id(client):
    """test proper errpr is returned from the API
        target_url: /applications/<id>
    """
    lottery_id = 1
    application_id = make_application(
        client, test_user['secret_id'], lottery_id)

    # application id to test
    idx = application_id + 1
    resp = as_user_get(client,
                       test_user['secret_id'],
                       test_user['g-recaptcha-response'],
                       f'/applications/{idx}')

    assert resp.status_code == 404
    assert 'Application could not be found.' in resp.get_json()['message']


def test_cancel_normal(client):
    """test: cancel added application
        1. add new application to db
        2. send request to cancel as a normal user
        3. check response's status_code and db status
        target_url: /applications/<id> [DELETE]
    """
    lottery_id = 1
    application_id = make_application(
        client, test_user['secret_id'], lottery_id)

    token = login(client, test_user['secret_id'],
                  test_user['g-recaptcha-response'])['token']
    user_resp = client.get('/status',
                           headers={'Authorization': f'Bearer {token}'})
    user_id = user_resp.get_json()['id']
    resp = client.delete(f'/applications/{application_id}',
                         headers={'Authorization': f'Bearer {token}'})
    with client.application.app_context():
        application = Application.query.filter_by(
            lottery_id=lottery_id, user_id=user_id).first()

    assert resp.status_code == 200
    assert application is None


def test_cancel_admin(client):
    """test: return 403 for canceling by admin
    """
    lottery_id = 1
    application_id = make_application(
        client, admin['secret_id'], lottery_id)

    token = login(client, admin['secret_id'],
                  admin['g-recaptcha-response'])['token']
    resp = client.delete(f'/applications/{application_id}',
                         headers={'Authorization': f'Bearer {token}'})

    assert resp.status_code == 403


def test_cancel_already_done_normal(client):
    """attempt to cancel application that already-done lottery
        1. create 'done' application
        2. attempt to cancel that application
        target_url: /lotteries/<id> [DELETE]
    """
    token = login(client, test_user['secret_id'],
                  test_user['g-recaptcha-response'])['token']
    lottery_id = 1
    application_id = make_application(
        client, test_user['secret_id'], lottery_id)

    with client.application.app_context():
        target_application = Application.query.filter_by(
            id=application_id).first()
        target_application.status = 'lose'
        db.session.add(target_application)
        db.session.commit()

    resp = client.delete(f'/applications/{application_id}',
                         headers={'Authorization': f'Bearer {token}'})

    assert resp.status_code == 400
    assert 'The Application has already fullfilled' in resp.get_json()[
        'message']


@pytest.mark.skip(reason='not implemented yet')
def test_cancel_noperm(client):
    """attempt to cancel without permission
        1. create new application.
        2. attempt to cancel with other user's token
    """
    idx = 1
    owner = test_user
    user = {'secret_id': 'hoge', 'g-recaptcha-response': 'hugo'}
    owner_token = login(client, owner['secret_id'],
                        owner['g-recaptcha-response'])['token']
    user_token = login(client, user['secret_id'],
                       user['g-recaptcha-response'])['token']

    client.post(f'/lotteries/{idx}',
                headers={'Authorization': f'Bearer {owner_token}'})
    resp = client.delete(f'/applications/{idx}',
                         headers={'Authorization': f'Bearer {user_token}'})

    assert resp.status_code == 403
    assert 'insufficient_scope' in resp.headers['WWW-Authenticate']


def test_draw(client):
    """attempt to draw a lottery
        1. make some applications to one lottery
        2. draws the lottery
        3. test: status code
        4. test: DB is changed
        target_url: /lotteries/<id>/draw [PUT]
    """
    idx = 1

    with client.application.app_context():
        target_lottery = Lottery.query.filter_by(id=idx).first()
        users = User.query.all()
        for user in users:
            application = Application(lottery=target_lottery, user_id=user.id)
            db.session.add(application)
        db.session.commit()

        token = login(client,
                      admin['secret_id'],
                      admin['g-recaptcha-response'])['token']

        _, end = client.application.config['TIMEPOINTS'][int(idx)]
        with mock.patch('api.time_management.get_current_datetime',
                        return_value=end):
            resp = client.post(f'/lotteries/{idx}/draw',
                               headers={'Authorization': f'Bearer {token}'})

        assert resp.status_code == 200

        winners_id = [winner['id'] for winner in resp.get_json()]
        users = User.query.all()
        target_lottery = Lottery.query.filter_by(id=idx).first()
        assert target_lottery.done
        for user in users:
            application = Application.query.filter_by(
                lottery=target_lottery, user_id=user.id).first()
            if application:
                status = 'won' if user.id in winners_id else 'lose'
            assert application.status == status


def test_draw_noperm(client):
    """attempt to draw without proper permission.
        target_url: /lotteries/<id>/draw [POST]
    """
    idx = 1
    token = login(client, test_user['secret_id'],
                  test_user['g-recaptcha-response'])['token']
    resp = client.post(f'/lotteries/{idx}/draw',
                       headers={'Authorization': f'Bearer {token}'})

    assert resp.status_code == 403
    assert 'Forbidden' in resp.get_json()['message']


def test_draw_invalid(client):
    """attempt to draw non-exsit lottery
        target_url: /lotteries/<id>/draw [POST]
    """
    idx = invalid_lottery_id
    token = login(client, admin['secret_id'],
                  admin['g-recaptcha-response'])['token']

    resp = client.post(f'/lotteries/{idx}/draw',
                       headers={'Authorization': f'Bearer {token}'})

    assert resp.status_code == 404
    assert 'Lottery could not be found.' in resp.get_json()['message']


def test_draw_time_invalid(client):
    """attempt to draw in not acceptable time
        target_url: /draw_all [POST]
    """
    with client.application.app_context():
        target_lottery = Lottery.query.filter_by(id=1).first()

    def try_with_datetime(t):
        with mock.patch('api.time_management.get_current_datetime',
                        return_value=t):
            resp = client.post(f'/lotteries/{target_lottery.id}/draw',
                               headers={'Authorization': f'Bearer {token}'})

            assert resp.status_code == 400
            assert 'Not acceptable' in resp.get_json()['message']

    token = login(client, admin['secret_id'],
                  admin['g-recaptcha-response'])['token']
    outofhours1 = client.application.config['START_DATETIME'] - \
        datetime.timedelta.resolution
    try_with_datetime(outofhours1)
    outofhours2 = client.application.config['END_DATETIME'] + \
        datetime.timedelta.resolution
    try_with_datetime(outofhours2)

    timepoints = client.application.config['TIMEPOINTS']
    ext = client.application.config['DRAWING_TIME_EXTENSION']
    _, en = timepoints[target_lottery.index]
    res = datetime.timedelta.resolution
    try_with_datetime(mod_time(en, -res))
    try_with_datetime(mod_time(en, +ext+res))


def test_draw_already_done(client):
    """attempt to draw previously drawn lottery.
        1. test: error is returned
        target_url: /lotteries/<id>/draw [POST]
    """
    idx = 1
    token = login(client, admin['secret_id'],
                  admin['g-recaptcha-response'])['token']

    with client.application.app_context():
        target_lottery = Lottery.query.filter_by(id=idx).first()
        target_lottery.done = True
        db.session.add(target_lottery)
        db.session.commit()

    _, end = client.application.config['TIMEPOINTS'][int(idx)]
    with mock.patch('api.time_management.get_current_datetime',
                    return_value=end):
        resp = client.post(f'/lotteries/{idx}/draw',
                           headers={'Authorization': f'Bearer {token}'})

    assert resp.status_code == 400
    assert 'already done' in resp.get_json()['message']


@pytest.mark.skip(reason='not implemented yet')
def test_draw_nobody_apply(client):
    """attempt to draw a lottery that nobody applying
        1. make sure any application is applied to the lottery
        2. attempt to draw it
        target_url: /lotteries/<id>/draw [POST]
    """

    idx = 1
    token = login(client, admin['secret_id'],
                  admin['g-recaptcha-response'])['token']

    with client.application.app_context():
        target_applications = Application.query.filter_by(lottery_id=idx).all()
        if target_applications is not None:
            db.session.delete(target_applications)
            db.session.commit()

    resp = client.post(f'/lotteries/{idx}/draw',
                       headers={'Authorization': f'Bearer {token}'})

    assert resp.status_code == 400
    assert 'nobody' in resp.get_json()['message']


def test_draw_all(client):
    """attempt to draw all lotteries
        1. make some applications to some lotteries
        2. draws all the lotteries in one time index
        3. test: status code
        4. test: DB is properly changed
        target_url: /draw_all [POST]
    """
    time_index = 1

    with client.application.app_context():
        target_lotteries = Lottery.query.filter_by(index=time_index)
        non_target_lotteries = Lottery.query.filter_by(index=time_index+1)
        users = (user for user in User.query.all()
                 if user.authority != "admin")
        for i, user in enumerate(users):
            target_lottery = target_lotteries[i % len(list(target_lotteries))]
            non_target_lottery = non_target_lotteries[i % len(
                list(non_target_lotteries))]
            application1 = Application(lottery=target_lottery, user_id=user.id)
            application2 = Application(
                lottery=non_target_lottery, user_id=user.id)
            db.session.add(application1)
            db.session.add(application2)
        db.session.commit()

    token = login(client,
                  admin['secret_id'],
                  admin['g-recaptcha-response'])['token']
    draw_time = client.application.config['TIMEPOINTS'][time_index][1]
    with mock.patch('api.time_management.get_current_datetime',
                    return_value=draw_time):
        resp = client.post('/draw_all',
                           headers={'Authorization': f'Bearer {token}'})

    assert resp.status_code == 200

    winners_id = [winner['id'] for winner in resp.get_json()]
    assert all(lottery.done for lottery in target_lotteries)
    assert all(not lottery.done for lottery in non_target_lotteries)

    with client.application.app_context():
        users = User.query.all()
        for user in users:
            for lottery in target_lotteries:
                application = Application.query.filter_by(
                    lottery=lottery, user_id=user.id).first()
                if application:
                    status = 'won' if user.id in winners_id else 'lose'
                    assert application.status == status

            for lottery in non_target_lotteries:
                application = Application.query.filter_by(
                    lottery=lottery, user_id=user.id).first()
                if application:
                    assert application.status == "pending"


def test_draw_all_noperm(client):
    """attempt to draw without proper permission.
        target_url: /draw_all [POST]
    """
    token = login(client, test_user['secret_id'],
                  test_user['g-recaptcha-response'])['token']
    resp = client.post('/draw_all',
                       headers={'Authorization': f'Bearer {token}'})

    assert resp.status_code == 403
    assert 'Forbidden' in resp.get_json()['message']


def test_draw_all_invalid(client):
    """attempt to draw in not acceptable time
        target_url: /draw_all [POST]
    """
    def try_with_datetime(t):
        with mock.patch('api.time_management.get_current_datetime',
                        return_value=t):
            resp = client.post('/draw_all',
                               headers={'Authorization': f'Bearer {token}'})

            assert resp.status_code == 400
            assert 'Not acceptable' in resp.get_json()['message']

    token = login(client, admin['secret_id'],
                  admin['g-recaptcha-response'])['token']
    outofhours1 = client.application.config['START_DATETIME'] - \
        datetime.timedelta.resolution
    try_with_datetime(outofhours1)
    outofhours2 = client.application.config['END_DATETIME'] + \
        datetime.timedelta.resolution
    try_with_datetime(outofhours2)

    timepoints = client.application.config['TIMEPOINTS']
    ext = client.application.config['DRAWING_TIME_EXTENSION']
    for i, (_, en) in enumerate(timepoints):
        res = datetime.timedelta.resolution
        try_with_datetime(mod_time(en, -res))
        try_with_datetime(mod_time(en, +ext+res))

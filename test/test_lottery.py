import pytest

from utils import (
    login,
    admin,
    test_user,
    invalid_classroom_id,
    invalid_lottery_id
)

from api.models import Lottery, Classroom, User, Application, db
from api.schemas import (
    classrooms_schema,
    classroom_schema,
    application_schema,
    lotteries_schema,
    lottery_schema
)


# ---------- Lottery API

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
    idx = '1'  # classroom id to test
    resp = client.get('/classrooms/'+idx)

    with client.application.app_context():
        db_status = Classroom.query.filter_by(id=idx).first()
        classroom = classroom_schema.dump(db_status)[0]

    assert resp.get_json() == classroom


def test_get_specific_classroom_invaild_id(client):
    """test proper errpr is returned from the API
        target_url: /classrooms/<id>
    """
    idx = invalid_classroom_id  # classroom id to test
    resp = client.get('/classrooms/'+idx)

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
    idx = '1'  # lottery id to test
    resp = client.get('/lotteries/'+idx)

    with client.application.app_context():
        db_status = Lottery.query.filter_by(id=idx).first()
        lottery = lottery_schema.dump(db_status)[0]

    assert resp.get_json() == lottery


def test_get_specific_lottery_invaild_id(client):
    """test proper errpr is returned from the API
        target_url: /classrooms/<id>
    """
    idx = invalid_lottery_id  # lottery id to test
    resp = client.get('/lotteries/'+idx)

    assert resp.status_code == 404
    assert 'Lottery could not be found.' in resp.get_json()['message']


def test_apply(client):
    """attempt to apply new application.
        1. test: error isn't returned
        2. test: DB is changed
        target_url: /lotteries/<id> [POST]
    """
    idx = '1'
    token = login(client, test_user['username'],
                  test_user['password'])['token']
    resp = client.post('/lotteries/'+idx,
                      headers={'Authorization': 'Bearer ' + token})

    with client.application.app_context():
        # get needed objects
        target_lottery = Lottery.query.filter_by(id=idx).first()
        user = User.query.filter_by(username=test_user['username']).first()
        # this application should be added by previous 'client.put'
        application = Application.query.filter_by(
            lottery=target_lottery, user_id=user.id).first()

        assert application is not None
        assert resp.get_json() ==  application_schema.dump(application)[0]


@pytest.mark.skip(reason='not implemented yet')
def test_apply_noperm(client):
    """attempt to apply without proper permission.
        target_url: /api/lotteries/<id>/apply [PUT]
    """
    idx = '1'
    token = login(client, admin['username'], admin['password'])['token']
    resp = client.put('/api/lotteries/'+idx+'/apply',
                      headers={'Authorization': 'Bearer ' + token})

    assert '' in resp.get_json().keys()  # not completed yet


def test_apply_invaild(client):
    """attempt to apply to non-exsit lottery
        target_url: /lotteries/<id> [PUT]
    """
    idx = invalid_lottery_id
    token = login(client, test_user['username'],
                  test_user['password'])['token']
    resp = client.post('/lotteries/'+idx,
                      headers={'Authorization': 'Bearer ' + token})

    assert resp.status_code == 404
    assert 'Lottery could not be found.' in resp.get_json()['message']


def test_apply_already_done(client):
    """attempt to apply previously drawn application.
        1. test: error is returned
        target_url: /lotteries/<id> [POST]
    """
    idx = '1'
    token = login(client, test_user['username'],
                  test_user['password'])['token']

    with client.application.app_context():
        target_lottery = Lottery.query.filter_by(id=idx).first()
        target_lottery.done = True
        db.session.add(target_lottery)
        db.session.commit()

    resp = client.post('/lotteries/'+idx,
                      headers={'Authorization': 'Bearer ' + token})

    assert resp.status_code == 400
    assert 'already done' in resp.get_json()['message']


def test_apply_same_period(client):
    """attempt to apply to the same period with the previous application
        1. test: error is returned
        target_url: /lotteries/<id> [POST]
    """
    idx = '1'
    token = login(client, test_user['username'],
                  test_user['password'])['token']

    with client.application.app_context():
        target_lottery = Lottery.query.filter_by(id=idx).first()
        booking_lottery = Lottery.query.filter_by(
            index=target_lottery.index).filter(Lottery.id != idx).first()
        user = User.query.filter_by(username=test_user['username']).first()
        application = Application(lottery=booking_lottery, user_id=user.id)
        db.session.add(application)
        db.session.commit()

    resp = client.post('/lotteries/'+idx,
                      headers={'Authorization': 'Bearer ' + token})

    message = resp.get_json()['message']

    assert resp.status_code == 400
    assert 'already applying to a lottery in this period' in message


@pytest.mark.skip(reason='will be repaced with "/application" endpoint')
def test_cancel(client):
    """test: cancel added application
        1. add new application to db
        2. send request to cancel
        3. check response's status_code and db status
        target_url: /lotteries/<id> [DELETE]
    """
    lottery_id = '1'
    token = login(client, test_user['username'],
                  test_user['password'])['token']
    user_resp = client.get('/status',
                           headers={'Authorization': 'Bearer ' + token})
    user_id = user_resp.get_json()['id']
    with client.application.app_context():
        newapplication = Application(
            lottery_id=lottery_id, user_id=user_id, status='pending')
        db.session.add(newapplication)
        db.session.commit()

        resp = client.delete('/applications/' + lottery_id,
                             headers={'Authorization': 'Bearer ' + token})
        application = Application.query.filter_by(
            lottery_id=lottery_id, user_id=user_id).first()

    assert resp.status_code == 200
    assert application is None


@pytest.mark.skip(reason='will be repaced with "/application" endpoint')
def test_cancel_invaild(client):
    """attempt to cancel non-applied application.
        target_url: /lotteries/<id> [DELETE]
    """

    lottery_id = '1'
    token = login(client, test_user['username'],
                  test_user['password'])['token']
    resp = client.delete('/applications/' + lottery_id,
                         headers={'Authorization': 'Bearer ' + token})

    assert resp.status_code == 400
    assert "You're not applying for this lottery" in resp.get_json()['message']


def test_cancel_already_done(client):
    """attempt to cancel application that already-done lottery
        1. create 'done' lottery
        2. add application to that lottery
        3. attempt to cancel that application
        target_url: /api/lotteries/<id>/apply [DELETE]
    """
    idx = '1'
    user = test_user
    token = login(client, user['username'], user['password'])['token']

    with client.application.app_context():
        target_lottery = Lottery.query.filter_by(id=idx).first()
        target_lottery.done = True
        db.session.add(target_lottery)
        db.session.commit()

    resp = client.delete('/api/lotteries/' + idx + '/apply',
                         headers={'Authorization': 'Bearer ' + token})

    assert resp.status_code == 400
    assert 'This lottery has already done' in resp.get_json()['message']


@pytest.mark.skip(reason='not implemented yet')
def test_cancel_noperm(client):
    """attempt to cancel without permission

    """
    idx = '1'
    user = {'username': 'hoge', 'password': 'hugo'}
    token = login(client, user['username'], user['password'])['token']

    with client.application.app_context():
        target_lottery = Lottery.query.filter_by(id=idx).first()
        target_lottery.done = True
        db.session.add(target_lottery)
        db.session.commit()

    resp = client.delete('/api/lotteries/' + idx + '/apply',
                         headers={'Authorization': 'Bearer ' + token})

    assert resp.status_code == 400
    assert 'insufficient_scope' in resp.headers['WWW-Authenticate']


def test_draw(client):
    """attempt to draw a lottery
        1. some users make application to one lottery
        2. admin draws a lottery
        3. test: error isn't returned
        4. drawn id is one of applicant
        5. test: DB is changed
        target_url: /api/lotteries/<id>/apply [PUT]
    """
    idx = '1'

    with client.application.app_context():
        target_lottery = Lottery.query.filter_by(id=idx).first()
        users = User.query.all()
        for user in users:
            application = Application(lottery=target_lottery, user_id=user.id)
            db.session.add(application)
        db.session.commit()

    token = login(client, admin['username'], admin['password'])['token']
    resp = client.get('/api/lotteries/'+idx+'/draw',
                      headers={'Authorization': 'Bearer ' + token})

    assert resp.status_code == 200
    assert 'chosen' in resp.get_json().keys()

    chosen_id = resp.get_json()['chosen']

    with client.application.app_context():
        user = User.query.filter_by(id=chosen_id).first()
        assert user is not None
        target_lottery = Lottery.query.filter_by(id=idx).first()
        assert target_lottery.done
        users = User.query.all()
        for user in users:
            application = Application.query.filter_by(
                lottery=target_lottery, user_id=user.id).first()
            is_won = user.id == chosen_id
            assert application.status == is_won


def test_draw_noperm(client):
    """attempt to draw without proper permission.
        target_url: /api/lotteries/<id>/draw [GET]
    """
    idx = '1'
    token = login(client, test_user['username'],
                  test_user['password'])['token']
    resp = client.get('/api/lotteries/'+idx+'/draw',
                      headers={'Authorization': 'Bearer ' + token})

    assert resp.status_code == 403
    assert 'Forbidden' in resp.get_json()['message']  # not completed yet


def test_draw_invaild(client):
    """attempt to draw non-exsit lottery
        target_url: /api/lotteries/<id>/draw [GET]
    """
    idx = invalid_lottery_id
    token = login(client, admin['username'], admin['password'])['token']
    resp = client.get('/api/lotteries/'+idx+'/draw',
                      headers={'Authorization': 'Bearer ' + token})

    assert resp.status_code == 400
    assert 'Lottery could not be found.' in resp.get_json()['message']


def test_draw_already_done(client):
    """attempt to draw previously drawn application.
        1. test: error is returned
        target_url: /api/lotteries/<id>/draw [GET]
    """
    idx = '1'
    token = login(client, admin['username'], admin['password'])['token']

    with client.application.app_context():
        target_lottery = Lottery.query.filter_by(id=idx).first()
        target_lottery.done = True
        db.session.add(target_lottery)
        db.session.commit()

    resp = client.get('/api/lotteries/'+idx+'/draw',
                      headers={'Authorization': 'Bearer ' + token})

    assert resp.status_code == 400
    assert 'already done' in resp.get_json()['message']

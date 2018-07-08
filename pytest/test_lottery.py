from utils import *
from api.models import Application, db
import pytest


# ---------- Lottery API

def test_get_allclassrooms(client):
    """test proper infomation is returned from the API
        target_url: /api/classrooms
    """
    resp = client.get('/api/classrooms')

    with client.application.app_context():
        db_status = Classroom.query.all()

        assert resp.get_json()['classrooms'] == classrooms_schema.dump(db_status)[0]


def test_get_specific_classroom(client):
    """test proper infomation is returned from the API
        target_url: /api/classrooms/<id>
    """
    idx = '1' # classroom id to test
    resp = client.get('/api/classrooms/'+idx)

    with client.application.app_context():
        db_status = Classroom.query.filter_by(id=idx).first()

        assert resp.get_json()['classroom'] == classroom_schema.dump(db_status)[0]

def test_get_specific_classroom_invaild_id(client):
    """test proper errpr is returned from the API
        target_url: /api/classrooms/<id>
    """
    idx = invaild_classroom_id # classroom id to test
    resp = client.get('/api/classrooms/'+idx)

    assert resp.status_code == 400 and resp.get_json()['message'] == 'Classroom could not be found.'


def test_get_alllotteries(client):
    """test proper infomation is returned from the API
        target_url: /api/lotteries
    """
    resp = client.get('/api/lotteries')

    with client.application.app_context():
        db_status = Lottery.query.all()

        assert resp.get_json()['lotteries'] == lotteries_schema.dump(db_status)[0]


def test_get_specific_lottery(client):
    """test proper infomation is returned from the API
        target_url: /api/lotteries/<id>
    """
    idx = '1' # lottery id to test
    resp = client.get('/api/lotteries/'+idx)

    with client.application.app_context():
        db_status = Lottery.query.filter_by(id=idx).first()

        assert resp.get_json()['lottery'] == lottery_schema.dump(db_status)[0]


def test_get_specific_lottery_invaild_id(client):
    """test proper errpr is returned from the API
        target_url: /api/classrooms/<id>
    """
    idx = invaild_lottery_id # lottery id to test
    resp = client.get('/api/lotteries/'+idx)

    assert resp.status_code == 400 and resp.get_json()['message'] == 'Lottery could not be found.'




def test_apply(client):
    """attempt to apply new application.
        1. test: error isn't returned
        2. test: DB is changed
        target_url: /api/lotteries/<id>/apply [PUT]
    """
    idx = '1'
    token = login(client, test_user['username'], test_user['password'])['token']
    resp = client.put('/api/lotteries/'+idx+'/apply', headers={'Authorization': 'Bearer '+ token})

    assert 'id' in resp.get_json().keys()

    with client.application.app_context():
        # get needed objects
        target_lottery = Lottery.query.filter_by(id=idx).first()
        user = User.query.filter_by(username=test_user['username']).first()
        application = Application.query.filter_by(lottery=target_lottery, user_id=user.id) # this application should be added by previous 'client.put'

        assert application is not None


@pytest.mark.skip(reason='not implemented yet')
def test_apply_noperm(client):
    """attempt to apply without proper permission.
        target_url: /api/lotteries/<id>/apply [PUT]
    """
    idx = '1'
    token = login(client, admin['username'], admin['password'])['token']
    resp = client.put('/api/lotteries/'+idx+'/apply', headers={'Authorization': 'Bearer '+ token})

    assert '' in resp.get_json().keys() # not completed yet


def test_apply_invaild(client):
    """attempt to apply to non-exsit lottery
        target_url: /api/lotteries/<id>/apply [PUT]
    """
    idx= invaild_lottery_id
    token = login(client, test_user['username'], test_user['password'])['token']
    resp = client.put('/api/lotteries/'+idx+'/apply', headers={'Authorization': 'Bearer '+ token})

    assert resp.status_code == 400 and resp.get_json()['message'] == 'Lottery could not be found.'


# ----------------- later -----------------------------------------------------------------------
@pytest.mark.skip(reason='not made yet')
def test_apply_already_done(client):
    assert 'a' == 'a'

@pytest.mark.skip(reason='not made yet')
def test_apply_same_period(client):
    assert 'b' == 'b'
# -----------------------------------------------------------------------------------------------


def test_cancel(client):
    """test: cancel added application
        1. add new application to db
        2. send request to cancel
        3. check response's status_code and db status
        target_url: /api/lotteries/<id>/apply [DELETE]
    """
    lottery_id = '1'

    with client.application.app_context():

        token = login(client, test_user['username'], test_user['password'])['token']
        user_id = client.get('/api/status', headers={'Authorization': 'Bearer '+ token}).get_json()['status']['id']
        newapplication = Application(
                        lottery_id=lottery_id, user_id=user_id, status=None)
        db.session.add(newapplication)

        resp = client.delete('/api/lotteries/' + lottery_id + '/apply', headers={'Authorization':'Bearer ' + token})

        print('application: '+  str(Application.query.filter_by(lottery_id=lottery_id, user_id=user_id).first)) # debug
        assert resp.status_code == 200 and Application.query.filter_by(lottery_id=lottery_id,user_id=user_id).first() is None


def test_cancel_invaild(client):
    """attempt to cancel non-applied application.
        target_url: /api/lotteries/<id>/apply [DELETE]
    """

    lottery_id = '1'
    token = login(client, test_user['username'], test_user['password'])['token']
    resp = client.delete('/api/lotteries/' + lottery_id + '/apply', headers={'Authorization':'Bearer ' + token})

    assert resp.status_code == 400 and resp.get_json()['message'] == "You're not applying for this lottery"

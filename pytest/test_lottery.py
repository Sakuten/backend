from utils import *
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

    with client.application.app_context():
        db_status = Classroom.query.filter_by(id=idx).first()

        assert resp.status_code == 400


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

    with client.application.app_context():
        db_status = Lottery.query.filter_by(id=idx).first()

        assert resp.status_code == 400




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

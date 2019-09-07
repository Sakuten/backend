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
    as_user_get,
    invalid_classroom_id,
    invalid_lottery_id,
    make_application,
    user2application,
    users2application,
    rep2application,
    get_application,
    add_db,
    get_token,
    post,
    draw,
    draw_all
)


from api.models import Lottery, Classroom, User, Application, GroupMember, db
from api.models import apps2members
from api.schemas import (
    classrooms_schema,
    classroom_schema,
    application_schema,
    applications_schema,
    lotteries_schema,
    lottery_schema
)
from api.time_management import (
    mod_time,
    OutOfHoursError,
    OutOfAcceptingHoursError
)
from itertools import chain


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
        db_status = Classroom.query.get(idx)
        classroom = classroom_schema.dump(db_status)[0]

    assert resp.get_json() == classroom


def test_get_specific_classroom_invalid_id(client):
    """test proper errpr is returned from the API
        target_url: /classrooms/<id>
    """
    idx = invalid_classroom_id  # classroom id to test
    resp = client.get(f'/classrooms/{idx}')

    assert resp.status_code == 404
    assert 'Not found' in resp.get_json()['message']


def test_get_alllotteries(client):
    """test proper infomation is returned from the API
        target_url: /lotteries
    """
    resp = client.get('/lotteries')

    with client.application.app_context():
        db_status = Lottery.query.all()
        lottery_list = lotteries_schema.dump(db_status)[0]

    assert resp.get_json() == lottery_list


def test_get_all_available_lotteries(client):
    """test proper infomation is returned from the API
        target_url: /lotteries/available
    """
    index = 1
    with client.application.app_context():
        lotteries = Lottery.query.filter_by(index=index)
        current_lotteries = lotteries_schema.dump(lotteries)[0]
    with mock.patch('api.routes.api.get_time_index',
                    return_value=index):
        resp = client.get('/lotteries/available')

    assert current_lotteries == resp.get_json()


def test_get_all_available_lotteries_out_of_time(client):
    """test proper infomation is returned from the API
        when it is out of time
        target_url: /lotteries/available
    """
    with mock.patch('api.routes.api.get_time_index',
                    side_effect=OutOfHoursError()):
        resp = client.get('/lotteries/available')

    assert [] == resp.get_json()

    with mock.patch('api.routes.api.get_time_index',
                    side_effect=OutOfAcceptingHoursError()):
        resp = client.get('/lotteries/available')

    assert [] == resp.get_json()


def test_get_specific_lottery(client):
    """test proper infomation is returned from the API
        target_url: /lotteries/<id>
    """
    idx = 1  # lottery id to test
    resp = client.get(f'/lotteries/{idx}')

    with client.application.app_context():
        db_status = Lottery.query.get(idx)
        lottery = lottery_schema.dump(db_status)[0]

    assert resp.get_json() == lottery


def test_get_specific_lottery_invalid_id(client):
    """test proper errpr is returned from the API
        target_url: /lotteries/<id>
    """
    idx = invalid_lottery_id  # lottery id to test
    resp = client.get(f'/lotteries/{idx}')

    assert resp.status_code == 404
    assert 'Not found' in resp.get_json()['message']


def test_apply_normal(client):
    """attempt to apply new application.
        1. test: error isn't returned
        2. test: DB is changed
        target_url: /lotteries/<id> [POST]
    """
    idx = 1
    user_info = test_user

    with client.application.app_context():
        target_lottery = Lottery.query.get(idx)
        index = target_lottery.index

    token = get_token(client, user_info)

    with mock.patch('api.routes.api.get_time_index',
                    return_value=index):
        resp = post(client, f'/lotteries/{idx}', token,
                    group_members=[])

    assert resp.status_code == 200

    with client.application.app_context():
        # get needed objects
        target_lottery = Lottery.query.get(idx)
        user = User.query.filter_by(secret_id=user_info['secret_id']).first()
        # this application should be added by previous 'client.put'
        application = get_application(user, target_lottery)
        assert application is not None

        assert resp.get_json() == application_schema.dump(application)[0]


def test_apply_admin(client):
    """attempt to apply new application as admin
        test: 403 is returned
        target_url: /lotteries/<id> [POST]
    """
    idx = 1
    token = get_token(client, admin)

    resp = post(client, f'/lotteries/{idx}', token, group_members=[])

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
                       json={'group_members': []})

    assert resp.status_code == 403
    assert 'no permission' in resp.get_json().keys()  # not completed yet


def test_apply_invalid(client):
    """attempt to apply to non-exsit lottery
        target_url: /lotteries/<id> [POST]
    """
    idx = invalid_lottery_id
    token = login(client, test_user['secret_id'],
                  test_user['g-recaptcha-response'])['token']
    resp = client.post(f'/lotteries/{idx}',
                       headers={'Authorization': f'Bearer {token}'},
                       json={'group_members': []})

    assert resp.status_code == 404
    assert 'Not found' in resp.get_json()['message']


def test_apply_same_period(client):
    """attempt to apply to the same period with the previous application
        1. test: error is returned
        target_url: /lotteries/<id> [POST]
    """
    idx = 1
    token = login(client, test_user['secret_id'],
                  test_user['g-recaptcha-response'])['token']

    with client.application.app_context():
        target_lottery = Lottery.query.get(idx)
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
                           json={'group_members': []})

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
        target_lottery = Lottery.query.get(idx)
        index = target_lottery.index
        user = User.query.filter_by(secret_id=test_user['secret_id']).first()
        application = Application(lottery=target_lottery, user_id=user.id)
        db.session.add(application)
        db.session.commit()

        with mock.patch('api.routes.api.get_time_index',
                        return_value=index):
            resp = post(client, f'/lotteries/{idx}', token, group_members=[])

    message = resp.get_json()['message']

    assert resp.status_code == 400
    assert 'already accepted' in message


def test_apply_consecutive(client):
    """attempt to apply after previous won / lose / waiting
        test: win -> refused (because he/she should be watching a show)
        test: lose / waiting -> accepted
        target_url: /lotteries/<id> [POST]
    """
    idx1 = 1
    token_admin = get_token(client, admin)

    with client.application.app_context():
        lottery1 = Lottery.query.get(idx1)
        index1 = lottery1.index
        lottery2 = Lottery.query.filter_by(
            classroom_id=lottery1.classroom_id,
            index=lottery1.index + 1).one()
        idx2 = lottery2.id
        index2 = lottery2.index

        # 5 won, 2 lose, 3 waiting
        users = User.query.filter_by(authority='normal').limit(10).all()
        apps = users2application(users, lottery1)
        add_db(apps)
        user_sids = [user.secret_id for user in users]
        app_ids = [app.id for app in apps]

        draw_all(client, token_admin, index=index1)

        for user_sid, app_id in zip(user_sids, app_ids):
            app_after = Application.query.get(app_id)

            token = login(client, user_sid, '')['token']
            with mock.patch('api.routes.api.get_time_index',
                            return_value=index2):
                resp = post(client, f'/lotteries/{idx2}', token=token,
                            group_members=[])

            if app_after.status == 'won':
                if resp.status_code != 403:
                    print(resp.get_json())
                    print(resp.headers.to_list())
                assert resp.status_code == 403
                assert 'while watching a show' in resp.get_json()['message']
            else:
                if resp.status_code != 200:
                    print(resp.get_json())
                    print(resp.headers.to_list())
                assert resp.status_code == 200


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
                           json={'group_members': []})
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
               test_user3['secret_id']
               ]
    with client.application.app_context():
        members_id = [User.query.filter_by(secret_id=member_secret).first().id
                      for member_secret in members]
    token = login(client, user['secret_id'],
                  user['g-recaptcha-response'])['token']

    with client.application.app_context():
        index = Lottery.query.get(idx).index
        user_id = User.query.filter_by(secret_id=user['secret_id']).first().id
        with mock.patch('api.routes.api.get_time_index',
                        return_value=index):
            resp = client.post(f'/lotteries/{idx}',
                               headers={'Authorization': f'Bearer {token}'},
                               json={'group_members': members})

        application = Application.query.filter_by(lottery_id=idx,
                                                  user_id=user_id).first()
        group_members = [gm.user_id for gm in GroupMember.query.filter_by(
                         rep_application=application).all()]
        assert application.is_rep is True
        members_id.sort()
        group_members.sort()
        assert group_members == members_id

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
                           json={'group_members': members})

    assert resp.status_code == 401
    assert 'Invalid group member secret id' in resp.get_json()['message']


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
               test_user3['secret_id']
               ]
    token = login(client, user['secret_id'],
                  user['g-recaptcha-response'])['token']

    with client.application.app_context():
        index = Lottery.query.get(idx).index
        lottery = Lottery.query.filter(Lottery.index == index,
                                       Lottery.id != idx).first()
        violation_user = User.query.filter_by(secret_id=members[0]).first()
        application = Application(lottery=lottery, user_id=violation_user.id)
        db.session.add(application)
        db.session.commit()

    with mock.patch('api.routes.api.get_time_index',
                    return_value=index):
        resp = client.post(f'/lotteries/{idx}',
                           headers={'Authorization': f'Bearer {token}'},
                           json={'group_members': members})

        assert resp.status_code == 400
        assert 'already applying to a lottery in this period' in \
            resp.get_json()['message']


def test_apply_group_same_lottery(client):
    """attempt to make application to the same lottery as member of group
        target_url: /lotteries/<id> [POST]

        1. make an application as member
        2. attempt to apply
    """
    idx = 1
    user = test_user
    members = [test_user1['secret_id'],
               test_user2['secret_id'],
               test_user3['secret_id']
               ]
    token = login(client, user['secret_id'],
                  user['g-recaptcha-response'])['token']

    with client.application.app_context():
        index = Lottery.query.get(idx).index
        lottery = Lottery.query.get(idx)
        violation_user = User.query.filter_by(secret_id=members[0]).first()
        application = Application(lottery=lottery, user_id=violation_user.id)
        db.session.add(application)
        db.session.commit()

    with mock.patch('api.routes.api.get_time_index',
                    return_value=index):
        resp = client.post(f'/lotteries/{idx}',
                           headers={'Authorization': f'Bearer {token}'},
                           json={'group_members': members})

        assert resp.status_code == 400
        assert 'Someone in the group is already applying to this lottery' in \
            resp.get_json()['message']


def test_apply_group_toomany(client):
    """attempt to apply as group which has too many peoples
        target_url: /lotteries/<id>/apply [POST]
    """
    lottery_id = 1
    user = test_user
    members = [test_user1['secret_id'],
               test_user2['secret_id'],
               test_user3['secret_id'],
               test_user4['secret_id']
               ]
    token = login(client, user['secret_id'],
                  user['g-recaptcha-response'])['token']

    with client.application.app_context():
        index = Lottery.query.get(lottery_id).index

    with mock.patch('api.routes.api.get_time_index',
                    return_value=index):
        resp = client.post(f'/lotteries/{lottery_id}',
                           headers={'Authorization': f'Bearer {token}'},
                           json={'group_members': members})

    assert resp.status_code == 400
    assert 'too many group members' in resp.get_json()['message']


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
    assert 'Not found' in resp.get_json()['message']


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


def test_cancel_group(client):
    """attempt to cancel group applications
        target_url: /lotteries/<id> [DELETE]
    """
    lottery_id = 1
    members = (test_user1, test_user2)
    rep = test_user

    token = login(client,
                  rep['secret_id'],
                  rep['g-recaptcha-response'])['token']

    with client.application.app_context():
        target_lottery = Lottery.query.get(lottery_id)
        index = target_lottery.index

        first_gm_len = len(GroupMember.query.all())

        members_app_id = [
            make_application(client, user['secret_id'], lottery_id)
            for user in members]
        rep_app_id = make_application(client, rep['secret_id'], lottery_id,
                                      group_member_apps=members_app_id)

        with mock.patch('api.routes.api.get_draw_time_index',
                        return_value=index):
            client.delete(f'/applications/{rep_app_id}',
                          headers={'Authorization': f'Bearer {token}'})

        app_ids = db.session.query(Application.id).all()
        assert rep_app_id not in app_ids
        assert all(member_app not in app_ids for member_app in members_app_id)

        after_gm_len = len(GroupMember.query.all())
        assert after_gm_len == first_gm_len


def test_cancel_duplicated_group(client):
    """attempt to cancel group applications
        target_url: /lotteries/<id> [DELETE]
    """
    lottery_id = 1
    members = (test_user1, test_user2, test_user2)
    rep = test_user

    token = login(client,
                  rep['secret_id'],
                  rep['g-recaptcha-response'])['token']

    with client.application.app_context():
        target_lottery = Lottery.query.get(lottery_id)
        index = target_lottery.index
        members_id = [user['secret_id'] for user in members]

        with mock.patch('api.routes.api.get_time_index',
                        return_value=index):
            resp = client.post(f'/lotteries/{lottery_id}',
                               headers={'Authorization': f'Bearer {token}'},
                               json={'group_members': members_id})
            assert resp.status_code == 400
            assert 'duplicated' in resp.get_json()['message']


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
        target_url: /lotteries/<id>/draw [POST]
    """
    idx = 1

    with client.application.app_context():
        target_lottery = Lottery.query.get(idx)
        index = target_lottery.index
        users = User.query.all()
        add_db(user2application(user, target_lottery) for user in users)

        token = get_token(client, admin)

        resp = draw(client, token, idx, index)

        assert resp.status_code == 200

        winners_id = [winner['id'] for winner in resp.get_json()]

        users = User.query.all()
        target_lottery = Lottery.query.get(idx)

        waiting_cnt = 0

        for user in users:
            application = get_application(user, target_lottery)

            if user.id in winners_id:
                assert application.status == 'won'
                assert user.win_count == 1
                assert user.lose_count == 0
                assert user.waiting_count == 0
            else:
                assert application.status in {'lose', 'waiting'}
                assert user.win_count == 0
                if application.status == 'waiting':
                    assert user.lose_count == 0
                    assert user.waiting_count == 1
                    waiting_cnt += 1
                else:
                    assert user.lose_count == 1
                    assert user.waiting_count == 0

        assert waiting_cnt == 3


def test_draw_group(client):
    """attempt to draw a lottery as a group
        1. make some applications to one lottery as a group
        2. draws the lottery
        3. test: status code
        4. test: DB is changed
        5. test: result of each member (win)
        target_url: /lotteries/<id>/draw [POST]
    """
    idx = 1
    group_size = 3

    with client.application.app_context():
        target_lottery = Lottery.query.get(idx)
        index = target_lottery.index
        users = User.query.all()

        members_app = [user2application(user, target_lottery)
                       for user in users[1:group_size]]
        add_db(members_app)

        rep_application = user2application(
                users[0], target_lottery,
                is_rep=True,
                group_members=apps2members(members_app))

        add_db((rep_application,))  # 1-element tuple

        token = get_token(client, admin)

        resp = draw(client, token, idx, index)

        assert resp.status_code == 200

        users = User.query.all()
        target_lottery = Lottery.query.get(idx)

        rep_status = get_application(users[0], target_lottery).status

        assert rep_status == "won"
        assert users[0].win_count == 1

        for user in users[1:group_size]:
            application = get_application(user, target_lottery)
            assert application.status == "won"
            assert user.win_count == 1


def test_draw_lots_of_groups(client):
    """attempt to draw a lottery as 3 groups of 2 members and
            2 group of 3 members
            while WINNERS_NUM is 5 and WAITING_NUM is 3
        1. make some applications to one lottery as groups
        2. draws the lottery
        3. test: status code
        4. test: DB is changed
        5. test: result of each member
        6. test: number of winners is 5 (*not 4*)
        7. test: size of waiting list < 3
        target_url: /lotteries/<id>/draw [POST]
    """
    idx = 1
    groups = {0: [1], 2: [3], 4: [5, 6], 7: [8, 9]}    # rep -> members

    with client.application.app_context():
        target_lottery = Lottery.query.get(idx)
        index = target_lottery.index
        users = User.query.all()

        for rep, members in groups.items():
            members_app = [user2application(users[i], target_lottery)
                           for i in members]
            add_db(members_app)

            rep_app = rep2application(users[rep], target_lottery,
                                      apps2members(members_app))
            add_db([rep_app])

        token = get_token(client, admin)

        resp = draw(client, token, idx, index)

        assert resp.status_code == 200

        winners = resp.get_json()
        assert len(winners) == 5

        users = User.query.all()
        target_lottery = Lottery.query.get(idx)

        won_cnt = 0
        lose_cnt = 0
        waiting_cnt = 0
        for rep, members in groups.items():
            rep_status = get_application(users[rep], target_lottery).status
            members_status = (get_application(users[i], target_lottery).status
                              for i in members)

            assert all(status == rep_status for status in members_status)

            if rep_status == "won":
                won_cnt += 1 + len(members)
            elif rep_status == "lose":
                lose_cnt += 1 + len(members)
            else:
                # make sure "waiting-pending" does not leak out
                assert rep_status == "waiting"
                waiting_cnt += 1 + len(members)

        assert won_cnt == 5
        assert lose_cnt in {2, 3}
        assert waiting_cnt in {3, 2}
        assert lose_cnt + waiting_cnt == 5


def test_draw_lots_of_groups_and_normal(client):
    """attempt to draw a lottery as 2 groups of 2 members and 2 normal
            while WINNERS_NUM is 5
        1. make some applications to one lottery as groups
        2. draws the lottery
        3. test: status code
        4. test: DB is changed
        5. test: result of each member
        6. test: number of winners is less than 3
        target_url: /lotteries/<id>/draw [POST]
    """
    idx = 1
    members = (0, 1)
    reps = (2, 3)
    normals = (4, 5)

    with client.application.app_context():
        target_lottery = Lottery.query.get(idx)
        index = target_lottery.index
        users = User.query.all()

        member_apps = [user2application(users[i], target_lottery)
                       for i in chain(members, normals)]
        add_db(member_apps)

        rep_apps = [rep2application(users[rep], target_lottery,
                                    [member_apps[member]])
                    for rep, member in zip(reps, members)]
        add_db(rep_apps)

        token = get_token(client, admin)

        resp = draw(client, token, idx, index)

        assert resp.status_code == 200

        winners = resp.get_json()
        assert len(winners) == 5    # client.application.config['WINNERS_NUM']

        users = User.query.all()
        target_lottery = Lottery.query.get(idx)

        for rep, member in zip(reps, members):
            rep_status = get_application(users[rep], target_lottery).status
            member_status = \
                get_application(users[member], target_lottery).status

            assert rep_status == member_status


def test_draw_noperm(client):
    """attempt to draw without proper permission.
        target_url: /lotteries/<id>/draw [POST]
    """
    idx = 1
    token = get_token(client, test_user)

    resp = draw(client, token, idx)

    assert resp.status_code == 403
    assert 'You have no permission to perform the action' in \
        resp.get_json()['message']


def test_draw_invalid(client):
    """attempt to draw non-exsit lottery
        target_url: /lotteries/<id>/draw [POST]
    """
    idx = invalid_lottery_id
    token = get_token(client, admin)

    resp = draw(client, token, idx)

    assert resp.status_code == 404
    assert 'Not found' in resp.get_json()['message']


def test_draw_time_invalid(client):
    """attempt to draw in not acceptable time
        target_url: /draw_all [POST]
    """
    idx = 1

    with client.application.app_context():
        target_lottery = Lottery.query.get(idx)

    token = login(client, admin['secret_id'],
                  admin['g-recaptcha-response'])['token']

    def try_with_datetime(t):
        resp = draw(client, token, idx, time=t)

        assert resp.status_code == 400
        assert 'Not acceptable' in resp.get_json()['message']

    res = datetime.timedelta.resolution

    outofhours1 = client.application.config['START_DATETIME'] - res
    try_with_datetime(outofhours1)

    outofhours2 = client.application.config['END_DATETIME'] + res
    try_with_datetime(outofhours2)

    timepoints = client.application.config['TIMEPOINTS']
    ext = client.application.config['DRAWING_TIME_EXTENSION']
    _, en = timepoints[target_lottery.index]
    try_with_datetime(mod_time(en, -res))
    try_with_datetime(mod_time(en, +ext+res))


def test_losers_advantage(client):
    """
        user with the lose_count of 3 and others with that of 0 attempt to
        apply a lottery
        test loser is more likely to win
        target_url: /lotteries/<id>/draw
    """
    users_num = 12

    idx = 1
    win_count = {i: 0 for i in range(1, users_num + 1)}     # user.id -> count

    with client.application.app_context():
        target_lottery = Lottery.query.get(idx)
        index = target_lottery.index

        users = User.query.order_by(User.id).all()[:users_num]
        users[0].lose_count = 3
        user0_id = users[0].id

        add_db(users2application(users, target_lottery))

        token = get_token(client, admin)

        resp = draw(client, token, idx, index)

        for winner_json in resp.get_json():
            winner_id = winner_json['id']
            win_count[winner_id] += 1

        # display info when this test fails
        print("final results of applications (1's lose_count == 3)")
        print(win_count)

        assert win_count[user0_id] > 0


def test_group_losers_advantage(client):
    """
        users with rep's lose_count of 6 and others with that of 0 attempt to
        apply a lottery
        test loser is more likely to win
        target_url: /lotteries/<id>/draw
    """
    users_num = 12

    idx = 1
    win_count = {i: 0 for i in range(1, users_num + 1)}     # user.id -> count

    with client.application.app_context():
        target_lottery = Lottery.query.get(idx)
        index = target_lottery.index

        users = User.query.order_by(User.id).all()[:users_num]
        users[0].lose_count = 6
        user0_id = users[0].id

        normal_apps = users2application(users[1:], target_lottery)
        add_db(normal_apps)

        rep_app = rep2application(users[0], target_lottery, [normal_apps[0]])
        add_db((rep_app,))

        token = get_token(client, admin)

        resp = draw(client, token, idx, index)

        for winner_json in resp.get_json():
            winner_id = winner_json['id']
            win_count[winner_id] += 1

        # display info when this test fails
        print("final results of applications (1's lose_count == 3)")
        print(win_count)

        assert win_count[user0_id] > 0


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
    _, en = client.application.config['TIMEPOINTS'][time_index]
    en_margin = client.application.config['TIMEPOINT_END_MARGIN']
    draw_time = mod_time(en, en_margin)

    resp = draw_all(client, token, time=draw_time)

    assert resp.status_code == 200

    winners_id = [winner['id'] for winner in resp.get_json()]

    with client.application.app_context():
        users = User.query.all()
        for user in users:
            for lottery in target_lotteries:
                application = Application.query.filter_by(
                    lottery=lottery, user_id=user.id).first()
                if application:
                    if user.id in winners_id:
                        assert application.status == "won"
                    else:
                        assert application.status in {"lose", "waiting"}

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
    resp = draw_all(client, token)

    assert resp.status_code == 403
    assert 'You have no permission to perform the action' in \
        resp.get_json()['message']


def test_draw_all_invalid(client):
    """attempt to draw in not acceptable time
        target_url: /draw_all [POST]
    """
    token = get_token(client, admin)

    def try_with_datetime(t):
        resp = draw_all(client, token, time=t)

        assert resp.status_code == 400
        assert 'Not acceptable' in resp.get_json()['message']

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


def test_draw_all_multiple(client):
    """hit /draw_all twice in one time index
        test: the result does not change
        target_url: /draw_all [POST]
    """
    idx = 1

    with client.application.app_context():
        target_lottery = Lottery.query.get(idx)
        index = target_lottery.index
        users = (user for user in User.query.all()
                 if user.authority == 'normal')
        for user in users:
            app = Application(lottery=target_lottery, user_id=user.id)
            db.session.add(app)
        db.session.commit()

        token = login(client,
                      admin['secret_id'],
                      admin['g-recaptcha-response'])['token']

        resp1 = draw_all(client, token, index=index)
        assert resp1.status_code == 200
        win1 = {
            app.id for app in Application.query.filter_by(status='won')}
        lose1 = {
            app.id for app in Application.query.filter_by(status='lose')}
        waiting1 = {
            app.id for app in Application.query.filter_by(status='waiting')}

        resp2 = draw_all(client, token, index=index)
        assert resp2.status_code == 200
        win2 = {
            app.id for app in Application.query.filter_by(status='won')}
        lose2 = {
            app.id for app in Application.query.filter_by(status='lose')}
        waiting2 = {
            app.id for app in Application.query.filter_by(status='waiting')}

        assert win1 == win2
        assert lose1 == lose2
        assert waiting1 == waiting2

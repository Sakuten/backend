from api.models import User, Application, db, group_members
from unittest import mock

# --- variables

# secret_id is to be set in the fixture
admin = {'secret_id': '',
         'g-recaptcha-response': ''}
checker = {'secret_id': '',
           'g-recaptcha-response': ''}
test_user = {'secret_id': '',
             'g-recaptcha-response': ''}
test_user1 = {'secret_id': '',
              'g-recaptcha-response': ''}
test_user2 = {'secret_id': '',
              'g-recaptcha-response': ''}
test_user3 = {'secret_id': '',
              'g-recaptcha-response': ''}
test_user4 = {'secret_id': '',
              'g-recaptcha-response': ''}
test_student = {'secret_id': '',
                'g-recaptcha-response': ''}

invalid_classroom_id = '999999999999'
invalid_lottery_id = '9999999999'

# --- methods


def login(client, secret_id, rresp):
    """logging in as 'secret_id' with 'g-recaptcha-response'
        client (class Flask.testing.FlaskClient): the client
        secret_id (str): the secret_id to login
        rresp (str): the recapctha response code. can be empty in testing
    """
    return client.post('/auth', json={
        'id': secret_id,
        'g-recaptcha-response': rresp
    }, follow_redirects=True).get_json()


def login_with_form(client, secret_id, rresp):
    """logging in as 'secret_id' with 'g-recaptcha-response',
            with Content-Type: application/x-www-form-urlencoded
        client (class Flask.testing.FlaskClient): the client
        secret_id (str): the secret_id to login
        rresp (str): the recapctha response code. can be empty in testing
    """
    return client.post('/auth', data={
        'id': secret_id,
        'g-recaptcha-response': rresp
    }, follow_redirects=True).get_json()


def as_user_get(client, secret_id, rresp, url):
    """make a response as logined user
         1. login as the user
         2. make GET request with 'token' made in 1.
         3. return response
         client (class Flask.testing.FlaskClient): the client
         secret_id (str): the secret_id to login
         rresp (str): the recapctha response code. can be empty in testing
   """
    login_data = login(client, secret_id, rresp)
    token = login_data['token']
    header = 'Bearer ' + token

    return client.get(url, headers={'Authorization': header})


def make_application(client, secret_id, lottery_id, group_member_apps=[]):
    """make an application with specified user and lottery id
         client (class Flask.testing.FlaskClient): the client
         secret_id (str): the secret_id to apply
         lottery_id (int): the lottery id to create application from.
         Return (int): The created application's id
   """
    with client.application.app_context():
        user = User.query.filter_by(secret_id=secret_id).first()
        group_member_apps = (Application.query.get(app_id)
                             for app_id in group_member_apps)
        newapplication = Application(
            lottery_id=lottery_id, user_id=user.id,
            group_members=[group_member(app)
                           for app in group_member_apps])
        db.session.add(newapplication)
        db.session.commit()
        return newapplication.id


def user2application(user, target_lottery, **kwargs):
    if isinstance(target_lottery, int):
        # when target_lottery is id
        if isinstance(user, int):
            # when user is id
            return Application(lottery_id=target_lottery, user_id=user,
                               **kwargs)
        else:
            return Application(lottery_id=target_lottery, user=user,
                               **kwargs)
    else:
        if isinstance(user, int):
            return Application(lottery=target_lottery, user_id=user,
                               **kwargs)
        else:
            return Application(lottery=target_lottery, user=user,
                               **kwargs)


def users2application(users, target_lottery, **kwargs):
    return [user2application(user, target_lottery, **kwargs)
            for user in users]


def rep2application(user, target_lottery, members):
    if isinstance(members[0], Application):
        members = group_members(members)
    return user2application(user, target_lottery,
                            is_rep=True,
                            group_members=members)


def get_application(user, target_lottery, **kwargs):
    if isinstance(target_lottery, int):
        # when target_lottery is id
        if isinstance(user, int):
            # when user is id
            return Application.query.filter_by(
                    lottery_id=target_lottery, user_id=user, **kwargs).first()
        else:
            return Application.query.filter_by(
                    lottery_id=target_lottery, user=user, **kwargs).first()
    else:
        if isinstance(user, int):
            return Application.query.filter_by(
                    lottery=target_lottery, user_id=user, **kwargs).first()
        else:
            return Application.query.filter_by(
                    lottery=target_lottery, user=user, **kwargs).first()


def add_db(args):
    for arg in args:
        db.session.add(arg)
    db.session.commit()


def get_token(client, login_user):
    return login(client,
                 login_user['secret_id'],
                 login_user['g-recaptcha-response'])['token']


def draw(client, token, idx, index=None, time=None):
    return post(client, f'lotteries/{idx}/draw', token, index, time)


def draw_all(client, token, index=None, time=None):
    return post(client, '/draw_all', token, index, time)


def post(client, url, token=None, index=None,
         time=None, group_members=None, **kwargs):
    if index is not None:
        with mock.patch('api.routes.api.get_draw_time_index',
                        return_value=index):
            return post(client, url, token, None, time, group_members,
                        **kwargs)
    if time is not None:
        with mock.patch('api.time_management.get_current_datetime',
                        return_value=time):
            return post(client, url, token, index, None, group_members,
                        **kwargs)

    if token is not None:
        return post(client, url, group_members=group_members,
                    headers={'Authorization': f'Bearer {token}'},
                    **kwargs)
    if group_members is not None:
        return post(client, url, json={'group_members': group_members},
                    **kwargs)

    return client.post(url, **kwargs)

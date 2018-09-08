from api.models import User, Application, db

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


def make_application(client, secret_id, lottery_id):
    """make an application with specified user and lottery id
         client (class Flask.testing.FlaskClient): the client
         secret_id (str): the secret_id to apply
         lottery_id (int): the lottery id to create application from.
         Return (int): The created application's id
   """
    with client.application.app_context():
        user = User.query.filter_by(secret_id=secret_id).first()
        newapplication = Application(
            lottery_id=lottery_id, user_id=user.id, status="pending")
        db.session.add(newapplication)
        db.session.commit()
        return newapplication.id

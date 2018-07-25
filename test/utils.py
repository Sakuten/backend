import datetime

from api.models import User, Application, db

# --- variables

admin = {'username': 'admin',
         'g-recaptcha-response': ''}
test_user = {'username': 'example1',
             'g-recaptcha-response': ''}

invalid_classroom_id = '999999999999'
invalid_lottery_id = '9999999999'

# --- methods
def mod_time(t, dt):
    """
        Modify the supplied time with timedelta
        Args:
            t(datetime.time|datetime.datetime): The Time to modify
            dt(datetime.timedelta): Difference
        Returns:
            time(datetime.time|datetime.datetime): The modified time
    """
    if isinstance(t, datetime.time):
        t = datetime.datetime.combine(datetime.date(2000, 1, 1), t)
        return (t + dt).time()
    else:
        return t + dt

def login(client, username, rresp):
    """logging in as 'username' with 'g-recaptcha-response'
        client (class Flask.testing.FlaskClient): the client
        username (str): the username to login
        rresp (str): the recapctha response code. can be empty in testing
    """
    return client.post('/auth', json={
        'username': username,
        'g-recaptcha-response': rresp
    }, follow_redirects=True).get_json()


def login_with_form(client, username, rresp):
    """logging in as 'username' with 'g-recaptcha-response',
            with Content-Type: application/x-www-form-urlencoded
        client (class Flask.testing.FlaskClient): the client
        username (str): the username to login
        rresp (str): the recapctha response code. can be empty in testing
    """
    return client.post('/auth', data={
        'username': username,
        'g-recaptcha-response': rresp
    }, follow_redirects=True).get_json()


def as_user_get(client, username, rresp, url):
    """make a response as logined user
         1. login as the user
         2. make GET request with 'token' made in 1.
         3. return response
         client (class Flask.testing.FlaskClient): the client
         username (str): the username to login
         rresp (str): the recapctha response code. can be empty in testing
   """
    login_data = login(client, username, rresp)
    token = login_data['token']
    header = 'Bearer ' + token

    return client.get(url, headers={'Authorization': header})


def make_application(client, username, lottery_id):
    """make an application with specified user and lottery id
         client (class Flask.testing.FlaskClient): the client
         username (str): the username to apply
         lottery_id (int): the lottery id to create application from.
         Return (int): The created application's id
   """
    with client.application.app_context():
        user = User.query.filter_by(username=username).first()
        newapplication = Application(
            lottery_id=lottery_id, user_id=user.id, status="pending")
        db.session.add(newapplication)
        db.session.commit()
        return newapplication.id

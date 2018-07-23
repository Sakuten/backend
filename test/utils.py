from api.models import User, Application, db

# --- variables

admin = {'username': 'admin',
         'password': 'admin'}
test_user = {'username': 'example1',
             'password': 'example1'}

invalid_classroom_id = '999999999999'
invalid_lottery_id = '9999999999'

# --- methods


def login(client, username, password):
    """logging in as 'username' with 'password'
        client (class Flask.testing.FlaskClient): the client
        username (str): the username to login
        password (str): the password for the 'username'
    """
    return client.post('/auth', json={
        'username': username,
        'password': password
    }, follow_redirects=True).get_json()


def login_with_form(client, username, password):
    """logging in as 'username' with 'password',
            with Content-Type: application/x-www-form-urlencoded
        client (class Flask.testing.FlaskClient): the client
        username (str): the username to login
        password (str): the password for the 'username'
    """
    return client.post('/auth', data={
        'username': username,
        'password': password
    }, follow_redirects=True).get_json()


def as_user_get(client, username, password, url):
    """make a response as logined user
         1. login as the user
         2. make GET request with 'token' made in 1.
         3. return response
         client (class Flask.testing.FlaskClient): the client
         username (str): the username to login
         password (str): the password for the 'username'
   """
    login_data = login(client, username, password)
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

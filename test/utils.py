# --- variables

admin = {'username': 'admin',
         'g-recaptcha-response': ''}
test_user = {'username': 'example1',
             'g-recaptcha-response': ''}

invalid_classroom_id = '999999999999'
invalid_lottery_id = '9999999999'

# --- methods


def login(client, username, rresp):
    """logging in as 'username' with 'g-recaptcha-response'
        client (class Flask.testing.FlaskClient): the client
        username (str): the username to login
        rresp (str): the recapctha response code. can be empty in testing
    """
    return client.post('/auth/', json={
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
    return client.post('/auth/', data={
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

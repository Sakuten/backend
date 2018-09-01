from flask import make_response, g, current_app, jsonify, request
from cryptography.fernet import Fernet, InvalidToken
from api.models import User, db
from datetime import datetime, date
from functools import wraps
import json
from api.time_management import get_current_datetime


def generate_token(obj):
    """
        generate token and expiration, return it.
        Args:
            obj (dict): the data to encrypt
        Return:
            token (bytes): encrypted token
    """
    fernet = Fernet(current_app.config['SECRET_KEY'])
    now = datetime.now().timestamp()
    data = {
        'issued_at': now,
        'data': obj
    }
    return fernet.encrypt(json.dumps(data).encode())


def decrypt_token(token):
    """
        decrypt the token.
        Args:
            token (str): encrypted token.
        Return:
            decrypted data (dict): decrypted contents
    """
    fernet = Fernet(current_app.config['SECRET_KEY'])
    try:
        decrypted = fernet.decrypt(token.encode())
    except InvalidToken:
        return None
    return json.loads(decrypted.decode())


def login_required(*required_authority):
    """
        a decorder to require login
        Args:
            *required_authority (str): required authorities
                if this is blank, no requirement of authority
    """
    def login_required_impl(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            def auth_error(code, headm=None):
                if code == 400:
                    message = 'Invalid Request'
                elif code == 401:
                    message = 'Unauthorized'
                elif code == 403:
                    message = 'Forbidden'
                else:
                    message = 'Unknown Error'
                resp = make_response(jsonify({"message": message}), code)
                if headm:
                    resp.headers['WWW-Authenticate'] = 'Bearer ' + headm
                return resp

            time = get_current_datetime()
            end = current_app.config['END_DATETIME']
            if end <= time:
                return auth_error(403, 'realm="not acceptable"')

            # check form of request header
            if 'Authorization' not in request.headers:
                return auth_error(401, 'realm="token_required"')
            auth = request.headers['Authorization'].split()
            if auth[0].lower() != 'bearer':
                return auth_error(400, 'error="invalid_request"')
            elif len(auth) == 1:
                return auth_error(400, 'error="invalid_request"')
            elif len(auth) > 2:
                return auth_error(400, 'error="invalid_request"')
            token = auth[1]
            data = decrypt_token(token)
            if not data:
                return auth_error(401, 'error="invalid_token"')
            user = todays_user(user_id=data['data']['user_id'])
            if user is None:
                return auth_error(401, 'realm="id_disabled"')
            if required_authority and \
                    (user.authority not in required_authority):
                return auth_error(403, 'error="insufficient_scope"')
            g.token_data = data['data']

            return f(*args, **kwargs)
        return decorated_function
    return login_required_impl


def todays_user(secret_id='', user_id=''):
    """confirm the user id isn't used in other day
        and return `User` object
        Args:
            secret_id (str): secret id of target user
        Return:
            User (api.models.User): the user object of 'secret_id'
            None : when given 'secret_id' is used in other day

        References are here:
            https://github.com/Sakuten/backend/issues/78#issuecomment-416609508
    """

    if secret_id:
        user = User.query.filter_by(secret_id=secret_id).first()
    elif user_id:
        user = User.query.get(user_id)

    if not user:
        return None
    if user.kind not in current_app.config['ONE_DAY_KIND']:
        return user

    if user.first_access is None:
        user.first_access = date.today()
        db.session.add(user)
        db.session.commit
        return user
    elif user.first_access == date.today():
        return user
    else:
        return None

from flask import make_response, g, current_app, jsonify, request
from cryptography.fernet import Fernet, InvalidToken
from api.models import User
from datetime import datetime
from functools import wraps
import json
from api.time_management import get_current_datetime
from api.error import error_response

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
                resp, http_code = error_response(code)
                if headm:
                    resp.headers['WWW-Authenticate'] = 'Bearer ' + headm
                return resp, http_code

            time = get_current_datetime()
            end = current_app.config['END_DATETIME']
            if end <= time:
                return auth_error(18, 'realm="not acceptable"')

            # check form of request header
            if 'Authorization' not in request.headers:
                return auth_error(0, 'realm="token_required"')
            auth = request.headers['Authorization'].split()
            if auth[0].lower() != 'bearer':
                return auth_error(4, 'error="invalid_request"')
            elif len(auth) == 1:
                return auth_error(4, 'error="invalid_request"')
            elif len(auth) > 2:
                return auth_error(4, 'error="invalid_request"')
            token = auth[1]
            data = decrypt_token(token)
            if not data:
                return auth_error(0, 'error="invalid_token"')
            user = User.query.filter_by(id=data['data']['user_id']).first()
            if required_authority and \
                    (user.authority not in required_authority):
                return auth_error(15, 'error="insufficient_scope"')
            g.token_data = data['data']

            return f(*args, **kwargs)
        return decorated_function
    return login_required_impl

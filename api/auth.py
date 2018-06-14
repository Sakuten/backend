from flask import make_response, g, current_app, jsonify, request
from cryptography.fernet import Fernet, InvalidToken
from api.models import User
from datetime import datetime
from functools import wraps
import json


def generate_token(obj):
    """
        generate token and expiration, return it.
        Args:
            obj (dictionary?): # more Info Needed
        Return:
            token (string): encrypted token
            expiration (string): expiration of the token # more info needed
    """
    fernet = Fernet(current_app.config['SECRET_KEY'])
    now = datetime.now().timestamp()
    expiration = current_app.config.get('TOKEN_EXPIRATION', 43200)  # 12 hours
    data = {
        'issued_at': now,
        'expiration_date': now + expiration,
        'data': obj
    }
    return fernet.encrypt(json.dumps(data).encode()), expiration


def decrypt_token(token):
    """
        decrypt the token.
        Args:
            token (string): encrypted token.
        Return:
            decrypted token (dictionary): decrypted token contents
    """
    fernet = Fernet(current_app.config['SECRET_KEY'])
    expiration = current_app.config.get('TOKEN_EXPIRATION', 43200)  # 12 hours
    try:
        decrypted = fernet.decrypt(token.encode(), expiration)
    except InvalidToken:
        return None
    return json.loads(decrypted.decode())


def login_required(required_name=None):
    """
        a decorder to require login
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
                resp = make_response(jsonify(message=message), code)
                if headm:
                    resp.headers['WWW-Authenticate'] = 'Bearer ' + headm
                return resp

            # check form of request header
            if 'Authorization' not in request.headers:
                return auth_error(401, 'realm="token_required"')
            auth = request.headers['Authorization'].split()
            if auth[0].lower() != 'bearer':
                return auth_error(401, 'error="token_required"')
            elif len(auth) == 1:
                return auth_error(400, 'error="invalid_request"')
            elif len(auth) > 2:
                return auth_error(400, 'error="invalid_request"')
            token = auth[1]
            data = decrypt_token(token)
            if not data:
                return auth_error(401, 'error="invalid_token"')
            user = User.query.filter_by(id=data['data']['user_id']).first()
            if required_name is not None and user.username != required_name:
                return auth_error(403, 'error="insufficient_scope"')
            g.token_data = data['data']

            return f(*args, **kwargs)
        return decorated_function
    return login_required_impl

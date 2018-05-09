from flask import make_response, g, current_app, jsonify, request
from cryptography.fernet import Fernet, InvalidToken
from datetime import datetime
from functools import wraps
import json


def generate_token(obj):
    fernet = Fernet(current_app.config['SECRET_KEY'])
    now = datetime.now().timestamp()
    expiration = current_app.config.get('TOKEN_EXPIRATION', 43200) # 12 hours
    data = {
            'issued_at': now,
            'expiration_date': now + expiration,
            'data': obj
            }
    return fernet.encrypt(json.dumps(data).encode()), expiration

def decrypt_token(token):
    fernet = Fernet(current_app.config['SECRET_KEY'])
    expiration = current_app.config.get('TOKEN_EXPIRATION', 43200) # 12 hours
    try:
        decrypted = fernet.decrypt(token.encode(), expiration)
    except InvalidToken:
        return None
    return json.loads(decrypted.decode())

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        def auth_error(msg, code, headm=None):
            resp = make_response(jsonify(message='Unauthorized'), code)
            if headm:
                resp.headers['WWW-Authenticate'] = 'Bearer ' + headm
            return resp

        if not 'Authorization' in request.headers:
            return auth_error('Unauthorized', 401, 'realm="token_required"')
        auth = request.headers['Authorization'].split()
        if auth[0].lower() != 'bearer':
            return auth_error('Unauthorized', 401, 'error="token_required"')
        elif len(auth) == 1:
            return auth_error('Invalid request', 400, 'error="invalid_request"')
        elif len(auth) > 2:
            return auth_error('Invalid request', 400, 'error="invalid_request"')
        token = auth[1]
        data = decrypt_token(token)
        if not data:
            return auth_error('Invalid token', 401, 'error="invalid_token"')
        g.token_data = data['data']

        return f(*args, **kwargs)
    return decorated_function

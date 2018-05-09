from flask import Blueprint, request, session, make_response, g
from flask import render_template, redirect, jsonify, current_app, url_for
from werkzeug.security import gen_salt, generate_password_hash
from api.models import db, User
from cryptography.fernet import Fernet, InvalidToken
from datetime import datetime
from functools import wraps
import json


bp = Blueprint(__name__, 'auth')

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

@bp.route('/', methods=['POST'])
def home():
    if not 'Content-Type' in request.headers or request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
        data = request.form
    elif request.headers['Content-Type'] == 'application/json':
        data = request.json
    else:
        return jsonify(message="Unsupported content type"), 400

    if not 'username' in data or not 'password' in data:
        return jsonify(message="Invalid request"), 400

    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user:
        if user.check_password(password):
            token, expiration = generate_token({'user_id': user.id})
            return jsonify(message="Login Successful", token=token.decode(), expires_in=expiration)
    return jsonify(message="Login Unsuccessful"), 400

@bp.route('/me')
@login_required
def me():
    user = g.token_data['user_id']
    if user:
        return jsonify(id=user)
    else:
        return jsonify(message="Not logged in"), 400

@bp.route('/logout')
def logout():
    user = current_user()
    if user:
        del session['id']
        return jsonify(id=user.id)
    else:
        return jsonify(message="Not logged in"), 400


from flask import Blueprint, request, session, make_response, g
from flask import render_template, redirect, jsonify, current_app, url_for
from werkzeug.security import gen_salt, generate_password_hash
from api.models import db, User
from api.auth import login_required, generate_token

bp = Blueprint(__name__, 'auth')

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


from flask import Blueprint, request, session
from flask import render_template, redirect, jsonify, current_app, url_for
from werkzeug.security import gen_salt, generate_password_hash
from api.models import db, User


bp = Blueprint(__name__, 'auth')


def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None


@bp.route('/', methods=['POST'])
def home():
    if not 'Content-Type' in request.headers or request.headers['Content-Type'] != 'application/json':
        return jsonify(message="Only application/json supported"), 400
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    if user:
        if user.check_password(password):
            session['id'] = user.id
            return jsonify(message="Login Successful", client_id=OAuth2Client.query.filter_by(user_id=user.id).first().client_id)
    return jsonify(message="Login Unsuccessful"), 400

@bp.route('/me')
def me():
    user = current_user()
    if user:
        return jsonify(id=user.id)
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


from flask import Blueprint, request, session
from flask import render_template, redirect, jsonify, current_app, url_for
from werkzeug.security import gen_salt, generate_password_hash
from authlib.flask.oauth2 import current_token
from authlib.specs.rfc6749 import OAuth2Error
from api.models import db, User, OAuth2Client
from api.oauth2 import authorization, require_oauth


bp = Blueprint(__name__, 'auth')


def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None


@bp.route('/', methods=['POST'])
def home():
    # if request.method == 'POST':
    print(request.headers)
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
    # user = current_user()
    # if user:
    #     clients = OAuth2Client.query.filter_by(user_id=user.id).all()
    # else:
    #     clients = []
    # return render_template('home.html', user=user, clients=clients)

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

@bp.route('/create_client', methods=('GET', 'POST'))
def create_client():
    user = current_user()
    if not user:
        return redirect(url_for('api.routes.auth.home'))
    if request.method == 'GET':
        return render_template('create_client.html')
    client = OAuth2Client(**request.json.to_dict(flat=True))
    client.user_id = user.id
    client.client_id = gen_salt(24)
    if client.token_endpoint_auth_method == 'none':
        client.client_secret = ''
    else:
        client.client_secret = gen_salt(48)
    db.session.add(client)
    db.session.commit()
    return redirect(url_for('api.routes.auth.home'))


@bp.route('/authorize', methods=['GET', 'POST'])
def authorize():
    user = current_user()
    # if request.method == 'GET':
    #     try:
    #         grant = authorization.validate_consent_request(end_user=user)
    #     except OAuth2Error as error:
    #         return error.error
    #     return render_template('authorize.html', user=user, grant=grant)
    if not user and 'username' in request.form:
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
    return authorization.create_authorization_response(grant_user=user)

@bp.route('/token', methods=['GET'])
def issue_token():
    return authorization.create_token_response()


@bp.route('/revoke', methods=['POST'])
def revoke_token():
    return authorization.create_endpoint_response('revocation')


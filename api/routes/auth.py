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
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user:
        if user.check_password(password):
            session['id'] = user.id
    elif 'ENABLE_SIGNUP' in current_app.config and current_app.config['ENABLE_SIGNUP']:
        user = User(username=username, passhash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        session['id'] = user.id
    return redirect(request.args.get('to', url_for('api.routes.auth.home')))
    # user = current_user()
    # if user:
    #     clients = OAuth2Client.query.filter_by(user_id=user.id).all()
    # else:
    #     clients = []
    # return render_template('home.html', user=user, clients=clients)


@bp.route('/logout')
def logout():
    del session['id']
    return redirect(request.args.get('to', url_for('api.routes.auth.home')))


@bp.route('/create_client', methods=('GET', 'POST'))
def create_client():
    user = current_user()
    if not user:
        return redirect(url_for('api.routes.auth.home'))
    if request.method == 'GET':
        return render_template('create_client.html')
    client = OAuth2Client(**request.form.to_dict(flat=True))
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
    if request.method == 'GET':
        try:
            grant = authorization.validate_consent_request(end_user=user)
        except OAuth2Error as error:
            return error.error
        return render_template('authorize.html', user=user, grant=grant)
    if not user and 'username' in request.form:
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
    # if request.form['confirm']:
    grant_user = user
    # else:
    #     grant_user = None
    return authorization.create_authorization_response(grant_user=grant_user)

@bp.route('/token', methods=['GET'])
def issue_token():
    return authorization.create_token_response()


@bp.route('/revoke', methods=['POST'])
def revoke_token():
    return authorization.create_endpoint_response('revocation')


from flask import Blueprint, jsonify, request, current_app
from urllib.request import urlopen
import json
from api.models import User
from api.auth import generate_token

bp = Blueprint(__name__, 'auth')


@bp.route('/', methods=['POST'])
def home():
    """
        top page. Require/Check Login
    """
    if 'Content-Type' not in request.headers or \
        request.headers['Content-Type'] == \
            'application/x-www-form-urlencoded':
        data = request.form
    elif request.headers['Content-Type'] == 'application/json':
        data = request.json
    else:
        return jsonify({"message": "Unsupported content type"}), 400

    if 'username' not in data or 'g-recaptcha-response' not in data:
        return jsonify({"message": "Invalid request"}), 400

    # login flow
    username = data.get('username')
    recaptcha_code = data.get('g-recaptcha-response')
    user = User.query.filter_by(username=username).first()
    if user:
        secret_key = current_app.config['RECAPTCHA_SECRET_KEY']
        request_uri = f'https://www.google.com/recaptcha/api/siteverify?secret={secret_key}&response={recaptcha_code}'
        recaptcha_auth = urlopen(request_uri).read()
        if json.loads(recaptcha_auth)['success']:
            token = generate_token({'user_id': user.id})
            return jsonify({"message": "Login Successful",
                            "token": token.decode()})
    return jsonify({"message": "Login Unsuccessful"}), 400

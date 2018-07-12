from flask import Blueprint, jsonify, request
from urllib.request import urlopen
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
        recaptcha_auth = urlopen(f'https://www.google.com/recaptcha/api/siteverify?secret={secret_key}&response={recaptcha_code}').read()
        if recaptcha_auth['success'] == True: # i'm not sure this thing work
            token = generate_token({'user_id': user.id})
            return jsonify({"message": "Login Successful",
                            "token": token.decode()})
    return jsonify({"message": "Login Unsuccessful"}), 400

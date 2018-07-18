from flask import Blueprint, jsonify, request
from api.models import User
from api.auth import generate_token
from api.swagger import spec

bp = Blueprint(__name__, 'auth')


@bp.route('/auth', methods=['POST'])
@spec('auth.yml')
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

    if 'username' not in data or 'password' not in data:
        return jsonify({"message": "Invalid request"}), 400

    # login flow
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user:
        if user.check_password(password):
            token = generate_token({'user_id': user.id})
            return jsonify({"message": "Login Successful",
                            "token": token.decode()})
    return jsonify({"message": "Login Unsuccessful"}), 400

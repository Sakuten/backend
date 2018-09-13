from flask import Blueprint, jsonify, request, current_app
from urllib.request import urlopen
import json
from ipaddress import ip_address
from api.auth import generate_token, todays_user
from api.swagger import spec
from api.error import error_response

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
        # Unsupported content type
        return error_response(13)

    if 'id' not in data or 'g-recaptcha-response' not in data:
        return error_response(2)  # Invalid request

    # login flow
    secret_id = data.get('id')
    recaptcha_code = data.get('g-recaptcha-response')
    (user, err_num) = todays_user(secret_id=secret_id)
    if not user:
        return error_response(err_num)
    if not ip_address(request.remote_addr).is_private:
        secret_key = current_app.config['RECAPTCHA_SECRET_KEY']
        request_uri = f'https://www.google.com/recaptcha/api/siteverify?secret={secret_key}&response={recaptcha_code}'  # noqa: E501
        recaptcha_auth = urlopen(request_uri).read()
        auth_resp = json.loads(recaptcha_auth)
        success = auth_resp['success'] and \
            auth_resp['score'] > current_app.config['RECAPTCHA_THRESHOLD']
    else:
        current_app.logger.warning(
            f'Skipping request from {request.remote_addr}')
        success = True

    if success or user.authority == 'admin':
        token = generate_token({'user_id': user.id})
        return jsonify({"message": "Login Successful",
                        "token": token.decode()})

    return error_response(3)  # Login unsuccessful

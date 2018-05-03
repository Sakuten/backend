from flask import Blueprint, jsonify
from authlib.flask.oauth2 import current_token
from api.oauth2 import require_oauth

bp = Blueprint(__name__, 'api')

@bp.route('/me')
@require_oauth('profile')
def api_me():
    user = current_token.user
    return jsonify(id=user.id, username=user.username)

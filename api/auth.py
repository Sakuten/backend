from flask import g, current_app, request
from cryptography.fernet import Fernet, InvalidToken
from api.models import User, db
from datetime import datetime, date
from functools import wraps
import json
from api.time_management import get_current_datetime
from api.error import error_response
# typehints imports {{{
from typing import Optional, Tuple, Callable, Dict
from flask import Response
# }}}


class UserNotFoundError(Exception):
    """
        The Exception that indicates the user was not found
    """
    pass


class UserDisabledError(Exception):
    """
        The Exception that indicates the user was not found
    """
    pass


def generate_token(obj: dict) -> bytes:
    """
        generate token and expiration, return it.
        Args:
            obj (dict): the data to encrypt
        Return:
            token (bytes): encrypted token
    """
    fernet = Fernet(current_app.config['SECRET_KEY'])
    now = datetime.now().timestamp()
    data = {
        'issued_at': now,
        'data': obj
    }
    return fernet.encrypt(json.dumps(data).encode())


def decrypt_token(token: str) -> Optional[Dict]:
    """
        decrypt the token.
        Args:
            token (str): encrypted token.
        Return:
            decrypted data (dict): decrypted contents
    """
    fernet = Fernet(current_app.config['SECRET_KEY'])
    try:
        decrypted = fernet.decrypt(token.encode())
    except InvalidToken:
        return None
    return json.loads(decrypted.decode())


def login_required(*required_authority: str) -> Callable:
    """
        a decorder to require login
        Args:
            *required_authority (str): required authorities
                if this is blank, no requirement of authority
    """
    def login_required_impl(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Tuple, **kwargs: Dict) -> Callable:
            def auth_error(code: int, headm: Optional[str]=None) -> Tuple[Response , int]:
                resp, http_code = error_response(code)
                if headm:
                    resp.headers['WWW-Authenticate'] = 'Bearer ' + headm
                return resp, http_code

            time = get_current_datetime()
            end = current_app.config['END_DATETIME']
            if end <= time:
                return auth_error(18, 'realm="not acceptable"')

            # check form of request header
            if 'Authorization' not in request.headers:
                return auth_error(0, 'realm="token_required"')
            auth = request.headers['Authorization'].split()
            if auth[0].lower() != 'bearer':
                return auth_error(4, 'error="invalid_request"')
            elif len(auth) == 1:
                return auth_error(4, 'error="invalid_request"')
            elif len(auth) > 2:
                return auth_error(4, 'error="invalid_request"')
            token = auth[1]
            data = decrypt_token(token)
            if not data:
                return auth_error(0, 'error="invalid_token"')
            try:
                user = todays_user(user_id=data['data']['user_id'])
            except UserNotFoundError:
                return auth_error(0, 'realm="invalid_token"')
            except UserDisabledError:
                return auth_error(0, 'realm="id_disabled"')
            if required_authority and \
                    (user.authority not in required_authority):
                return auth_error(15, 'error="insufficient_scope"')
            g.token_data = data['data']

            return f(*args, **kwargs)
        return decorated_function
    return login_required_impl


def todays_user(secret_id: str='', user_id: str='') -> User:
    """confirm the user id isn't used in other day
        and return `User` object
        Args:
            secret_id (str): secret id of target user
        Return:
            User (api.models.User): the user object of 'secret_id'
        Exceptions:
            UserNotFoundError : when user was not found in DB
            UserDisabledError : when user was diabled

        References are here:
            https://github.com/Sakuten/backend/issues/78#issuecomment-416609508
    """

    if secret_id:
        user = User.query.filter_by(secret_id=secret_id).first()
    elif user_id:
        user = User.query.get(user_id)

    if not user:
        raise UserNotFoundError()
    if user.kind not in current_app.config['ONE_DAY_KIND']:
        return user
    if user.first_access is None:
        user.first_access = date.today()
        db.session.add(user)
        db.session.commit
        return user
    elif user.first_access == date.today():
        return user
    else:
        raise UserDisabledError()

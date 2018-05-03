from flask import Blueprint, jsonify
from authlib.flask.oauth2 import current_token
from api.oauth2 import require_oauth
from api.models import Lottery, Classroom, db
from api.schemas import classrooms_schema, lotteries_schema

bp = Blueprint(__name__, 'api')

@bp.route('/classrooms')
def list_classrooms():
    classrooms = Classroom.query.all()
    result = classrooms_schema.dump(classrooms)[0]
    return jsonify(classrooms=result)

@bp.route('/lotteries')
def list_lotteries():
    lotteries = Lottery.query.all()
    result = lotteries_schema.dump(lotteries)[0]
    return jsonify(lotteries=result)


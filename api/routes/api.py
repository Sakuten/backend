import random
from flask import Blueprint, session, jsonify, request, g
from api.models import Lottery, Classroom, User, db
from api.schemas import user_schema, classrooms_schema, classroom_schema, lotteries_schema, lottery_schema
from api.auth import login_required

bp = Blueprint(__name__, 'api')

@bp.route('/classrooms')
def list_classrooms():
    classrooms = Classroom.query.all()
    result = classrooms_schema.dump(classrooms)[0]
    return jsonify(classrooms=result)

@bp.route('/classrooms/<int:idx>')
def list_classroom(idx):
    classroom = Classroom.query.get(idx)
    if classroom is None:
        return jsonify({"message": "Classroom could not be found."}), 400
    result = classroom_schema.dump(classroom)[0]
    return jsonify(classroom=result)

@bp.route('/lotteries')
def list_lotteries():
    lotteries = Lottery.query.all()
    result = lotteries_schema.dump(lotteries)[0]
    return jsonify(lotteries=result)

@bp.route('/lotteries/<int:idx>')
def list_lottery(idx):
    lottery = Lottery.query.get(idx)
    if lottery is None:
        return jsonify({"message": "Lottery could not be found."}), 400
    lottery_result = lottery_schema.dump(lottery)[0]
    classroom_result = classroom_schema.dump(lottery.classroom)[0]
    return jsonify(lottery=lottery_result, classroom=classroom_result)

@bp.route('/lotteries/<int:idx>/apply', methods=['PUT', 'DELETE'])
@login_required
def apply_lottery(idx):
    lottery = Lottery.query.get(idx)
    if lottery is None:
        return jsonify({"message": "Lottery could not be found."}), 400
    user = User.query.filter_by(id=g.token_data['user_id']).first()
    if request.method == 'PUT':
        user.applying_lottery_id = idx
    else:
        if user.applying_lottery_id == idx:
            user.applying_lottery_id = None
        else:
            return jsonify({"message": "You're not applying for this lottery"}), 400
    db.session.add(user)
    db.session.commit()
    return jsonify({})

# EXTRA AUTHENICAION REQUIRED
@bp.route('/lottery/<int:idx>/draw')
def draw_lottery(idx):
    lottery = Lottery.query.get(idx)
    if lottery is None:
        return jsonify({"message": "Lottery could not be found."}), 400
    users_applying = User.query.filter_by(applying_lottery_id=idx).all()
    if len(users_applying) == 0:
        return jsonify({"message": "Nobody is applying to this lottery"}), 400
    chosen = random.choice(users_applying)
    chosen.application_status = True
    db.session.add(chosen)
    for user in users_applying:
        user.applying_lottery_id = None
        db.session.add(user)
    db.session.commit()
    return jsonify(chosen=chosen.id)

@bp.route('/status', methods=['GET'])
@login_required
def get_status():
    user = User.query.filter_by(id=g.token_data['user_id']).first()
    result = user_schema.dump(user)[0]
    return jsonify(status=result)

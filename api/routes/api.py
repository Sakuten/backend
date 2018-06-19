import random
from flask import Blueprint, jsonify, request, g
from api.models import Lottery, Classroom, User, Application, db
from api.schemas import (
    user_schema,
    classrooms_schema,
    classroom_schema,
    lotteries_schema,
    lottery_schema
)
from api.auth import login_required

bp = Blueprint(__name__, 'api')


@bp.route('/classrooms')
def list_classrooms():
    classrooms = Classroom.query.all()
    result = classrooms_schema.dump(classrooms)[0]
    return jsonify({"classrooms": result})


@bp.route('/classrooms/<int:idx>')
def list_classroom(idx):
    classroom = Classroom.query.get(idx)
    if classroom is None:
        return jsonify({"message": "Classroom could not be found."}), 400
    result = classroom_schema.dump(classroom)[0]
    return jsonify({"classroom": result})


@bp.route('/lotteries')
def list_lotteries():
    lotteries = Lottery.query.all()
    result = lotteries_schema.dump(lotteries)[0]
    return jsonify({"lotteries": result})


@bp.route('/lotteries/<int:idx>')
def list_lottery(idx):
    lottery = Lottery.query.get(idx)
    if lottery is None:
        return jsonify({"message": "Lottery could not be found."}), 400
    lottery_result = lottery_schema.dump(lottery)[0]
    classroom_result = classroom_schema.dump(lottery.classroom)[0]
    return jsonify({"lottery": lottery_result, "classroom": classroom_result})


@bp.route('/lotteries/<int:idx>/apply', methods=['PUT', 'DELETE'])
@login_required()
def apply_lottery(idx):
    lottery = Lottery.query.get(idx)
    if lottery is None:
        return jsonify({"message": "Lottery could not be found."}), 400
    if lottery.done:
        return jsonify({"message": "This lottery has already done"}), 400
    user = User.query.filter_by(id=g.token_data['user_id']).first()
    previous = Application.query.filter_by(user_id=user.id)
    if any(app.lottery.index == lottery.index and
            app.lottery.id != lottery.id
            for app in previous.all()):
        msg = "You're already applying to a lottery in this period"
        return jsonify({"message": msg}), 400
    application = previous.filter_by(lottery_id=lottery.id).first()
    if request.method == 'PUT':
        if not application:
            newapplication = Application(
                lottery_id=lottery.id, user_id=user.id, status=None)
            db.session.add(newapplication)
    else:
        if application:
            db.session.delete(application)
        else:
            return jsonify({"message": "You're not applying for this lottery"}), 400
    db.session.commit()
    return jsonify({"id": application.id if application
                    else newapplication.id})


@bp.route('/lotteries/<int:idx>/draw')
@login_required('admin')
def draw_lottery(idx):
    lottery = Lottery.query.get(idx)
    if lottery is None:
        return jsonify({"message": "Lottery could not be found."}), 400
    if lottery.done:
        return jsonify({"message": "This lottery is already done and cannot be undone"}), 400
    applications = Application.query.filter_by(lottery_id=idx).all()
    if len(applications) == 0:
        return jsonify({"message": "Nobody is applying to this lottery"}), 400
    chosen = random.choice(applications)
    for application in applications:
        application.status = application.id == chosen.id
        db.session.add(application)
    lottery.done = True
    db.session.commit()
    return jsonify({"chosen": chosen.user.id})


@bp.route('/status', methods=['GET'])
@login_required()
def get_status():
    user = User.query.filter_by(id=g.token_data['user_id']).first()
    result = user_schema.dump(user)[0]
    return jsonify({"status": result})

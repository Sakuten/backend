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
    """
        return classroom list
        Auth: no need
        Response like:
            {
                "classrooms": [
                {
                    "grade": 5,
                    "id": 1,
                    "index": 0,
                    "name": "A"
                }
                ...
                ]
            }
    """
    classrooms = Classroom.query.all()
    result = classrooms_schema.dump(classrooms)[0]
    return jsonify(classrooms=result)


@bp.route('/classrooms/<int:idx>')
def list_classroom(idx):
    """
        return infomation about specified classroom
        Auth: no need
        Response like:
            {
                "classroom": [
                {
                    "grade": 5,
                    "id": 1,
                    "index": 0,
                    "name": "A"
                }
                ]
            }
    """
    classroom = Classroom.query.get(idx)
    if classroom is None:
        return jsonify({"message": "Classroom could not be found."}), 400
    result = classroom_schema.dump(classroom)[0]
    return jsonify(classroom=result)


@bp.route('/lotteries')
def list_lotteries():
    """
        return lotteries list.
        Auth: no need
        Response like:
            {
                "lotteries": [
                 {
                    "classroom_id": 1,
                    "done": false,
                    "id": 1,
                    "index": 0,
                    "name": "5A.0"
                 }]
            }
    """
    lotteries = Lottery.query.all()
    result = lotteries_schema.dump(lotteries)[0]
    return jsonify(lotteries=result)


@bp.route('/lotteries/<int:idx>')
def list_lottery(idx):
    """
        return infomation about specified lottery.
        Auth: no need
        Response like:
            {
                "lotterie": [
                 {
                    "classroom_id": 1,
                    "done": false,
                    "id": 1,
                    "index": 0,
                    "name": "5A.0"
                 }]
            }
    """
    lottery = Lottery.query.get(idx)
    if lottery is None:
        return jsonify({"message": "Lottery could not be found."}), 400
    lottery_result = lottery_schema.dump(lottery)[0]
    classroom_result = classroom_schema.dump(lottery.classroom)[0]
    return jsonify(lottery=lottery_result, classroom=classroom_result)


@bp.route('/lotteries/<int:idx>/apply', methods=['PUT', 'DELETE'])
@login_required()
def apply_lottery(idx):
    """
        add/delete applications.
        specify the lottery id in the URL.
        Response like:
            {
                "id": 1
            }
        "id" is the nuber of application(if user has 2 applications, id is 2, if 3, then id is 3...)
    """
    lottery = Lottery.query.get(idx)
    if lottery is None:
        return jsonify({"message": "Lottery could not be found."}), 400
    if lottery.done:
        return jsonify({"message": "This lottery has already done"}), 400
    user = User.query.filter_by(id=g.token_data['user_id']).first()
    previous = Application.query.filter_by(user_id=user.id)
    # I'm not sure whats goin' on here
    if any([app.lottery.index == lottery.index and app.lottery.id != lottery.id for app in previous.all()]):
        return jsonify(message="You're already applying to a lottery in this period"), 400
    application = previous.filter_by(lottery_id=lottery.id).first()
    # access DB
    if request.method == 'PUT':
        if not application:
            newapplication = Application(lottery_id=lottery.id, user_id=user.id, status=None)
            db.session.add(newapplication)
    else:
        if application:
            db.session.delete(application)
        else:
            return jsonify(message="You're not applying for this lottery"), 400
    db.session.commit()
    return jsonify(id=application.id if application else newapplication.id)

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
    return jsonify(chosen=chosen.user.id)


@bp.route('/status', methods=['GET'])
@login_required()
def get_status():
    """
        return user's id, applications
        Response like:
            {
                "status": {
                    "applications": [
                        {
                            "id": 1,
                            "lottery_id": 1,
                            "status": null,
                            "user_id": 3
                        }
                    ],
                "id": 3,
                "username": "example1"
                }
            }
    """
    user = User.query.filter_by(id=g.token_data['user_id']).first()
    result = user_schema.dump(user)[0]
    return jsonify(status=result)

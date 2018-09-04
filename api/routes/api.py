from itertools import chain

from flask import Blueprint, jsonify, g, request, current_app
from api.models import Lottery, Classroom, User, Application, db, GroupMember
from api.schemas import (
    user_schema,
    users_schema,
    classrooms_schema,
    classroom_schema,
    application_schema,
    applications_schema,
    lotteries_schema,
    lottery_schema
)
from api.auth import login_required
from api.swagger import spec
from api.time_management import (
    get_draw_time_index,
    OutOfHoursError,
    OutOfAcceptingHoursError,
    get_time_index
)
from api.draw import (
    draw_one,
    draw_all_at_index,
)
from api.utils import calc_sha256

bp = Blueprint(__name__, 'api')


@bp.route('/classrooms')
@spec('api/classrooms.yml')
def list_classrooms():
    """
        return classroom list
    """
# those two values will be used in the future. now, not used. see issue #59 #60
#     filter = request.args.get('filter')
#     sort = request.args.get('sort')

    classrooms = Classroom.query.all()
    result = classrooms_schema.dump(classrooms)[0]
    return jsonify(result)


@bp.route('/classrooms/<int:idx>')
@spec('api/classrooms/idx.yml')
def list_classroom(idx):
    """
        return infomation about specified classroom
    """
    classroom = Classroom.query.get(idx)
    if classroom is None:
        return jsonify({"message": "Classroom could not be found."}), 404
    result = classroom_schema.dump(classroom)[0]
    return jsonify(result)


@bp.route('/lotteries')
@spec('api/lotteries.yml')
def list_lotteries():
    """
        return lotteries list.
    """
# those two values will be used in the future. now, not used. see issue #62 #63
#     filter = request.args.get('filter')
#     sort = request.args.get('sort')

    lotteries = Lottery.query.all()
    result = lotteries_schema.dump(lotteries)[0]
    return jsonify(result)


@bp.route('/lotteries/<int:idx>', methods=['GET'])
@spec('api/lotteries/idx.yml')
def list_lottery(idx):
    """
        return infomation about specified lottery.
    """
    lottery = Lottery.query.get(idx)
    if lottery is None:
        return jsonify({"message": "Lottery could not be found."}), 404
    result = lottery_schema.dump(lottery)[0]
    return jsonify(result)


@bp.route('/lotteries/<int:idx>', methods=['POST'])
@spec('api/lotteries/apply.yml')
@login_required('normal')
def apply_lottery(idx):
    """
        apply to the lottery.
        specify the lottery id in the URL.
        1. check request errors
        2. check whether all group_member's secret_id are correct
        3. check wehter nobody in members made application to the same period
        4. get all `user_id` of members
        5. make application of token's owner
        6. if length of 'group_members' list is 0, goto *8.*
        7. set 'is_rep' to True,
           add 'user_id's got in *3.* to 'group_members' list
        8. make members application based on 'user_id' got in *3.*
        9. return application_id as result
        Variables:
            group_members_secret_id (list of str): list of members' secret_id
            lottery: (Lottery): specified Lottery object
            rep_user (User): token's owner's user object
            group_members (list of User): list of group members' User object
    """
    # 1.
    group_members_secret_id = request.get_json()['group_members']
    lottery = Lottery.query.get(idx)
    if lottery is None:
        return jsonify({"message": "Lottery could not be found."}), 404
    try:
        current_index = get_time_index()
    except (OutOfHoursError, OutOfAcceptingHoursError):
        return jsonify({"message":
                        "We're not accepting any application in this hours."}
                       ), 400
    if lottery.index != current_index:
        return jsonify({"message":
                        "This lottery is not acceptable now."}), 400

    # 2. 3. 4.
    group_members = []
    if len(group_members_secret_id) != 0:
        for sec_id in group_members_secret_id:
            user = User.query.filter_by(secret_id=sec_id).first()
            if user is not None:
                group_members.append(user)
            else:
                return jsonify({"message":
                                "Invalid group member secret id"}), 401

        for user in group_members:
            previous = Application.query.filter_by(user_id=user.id)
            if any(app.lottery.index == lottery.index and
                   app.lottery.id != lottery.id
                   for app in previous.all()):
                msg = "someone in the group is already " \
                      "applying to a lottery in this period"
                return jsonify({"message": msg}), 400
            if any(app.lottery.index == lottery.index and
                   app.lottery.id == lottery.id
                   for app in previous.all()):
                msg = "someone in the group is already " \
                      "applying to this lottery"
                return jsonify({"message": msg}), 400

    # 5.
    rep_user = User.query.filter_by(id=g.token_data['user_id']).first()
    previous = Application.query.filter_by(user_id=rep_user.id)
    if any(app.lottery.index == lottery.index and
            app.lottery.id != lottery.id
            for app in previous.all()):
        msg = "You're already applying to a lottery in this period"
        return jsonify({"message": msg}), 400
    if any(app.lottery.index == lottery.index and
            app.lottery.id == lottery.id
            for app in previous.all()):
        msg = "Your application is already accepted"
        return jsonify({"message": msg}), 400
    application = previous.filter_by(lottery_id=lottery.id).first()
    # access DB
    # 6. 7.
    if application:
        result = application_schema.dump(application)[0]
        return jsonify(result)
    else:
        if len(group_members) == 0:
            newapplication = Application(
                lottery_id=lottery.id, user_id=rep_user.id, status="pending")
            db.session.add(newapplication)
            db.session.commit()
            result = application_schema.dump(newapplication)[0]
            return jsonify(result)
        else:
            rep_application = Application(
                lottery_id=lottery.id, user_id=rep_user.id, status="pending",
                is_rep=True,
                group_members=[GroupMember(user_id=member.id)
                               for member in group_members])
            db.session.add(rep_application)
    # 8.
    for member in group_members:
        newapplication = Application(
            lottery_id=lottery.id, user_id=member.id, status="pending")
        db.session.add(newapplication)

    # 9.
    db.session.commit()
    result = application_schema.dump(rep_application)[0]
    return jsonify(result)


@bp.route('/applications')
@spec('api/applications.yml')
@login_required('normal')
def list_applications():
    """
        return applications list.
    """
# those two values will be used in the future. now, not used. see issue #62 #63
#     filter = request.args.get('filter')
#     sort = request.args.get('sort')

    user = User.query.filter_by(id=g.token_data['user_id']).first()
    applications = Application.query.filter_by(user_id=user.id)
    result = applications_schema.dump(applications)[0]
    return jsonify(result)


@bp.route('/applications/<int:idx>', methods=['GET'])
@spec('api/applications/idx.yml')
@login_required('normal')
def list_application(idx):
    """
        return infomation about specified application.
    """
    user = User.query.filter_by(id=g.token_data['user_id']).first()
    application = Application.query.filter_by(
        user_id=user.id).filter_by(id=idx).first()
    if application is None:
        return jsonify({"message": "Application could not be found."}), 404
    result = application_schema.dump(application)[0]
    return jsonify(result)


@bp.route('/applications/<int:idx>', methods=['DELETE'])
@spec('api/applications/cancel.yml')
@login_required('normal')
def cancel_application(idx):
    """
        cancel the application.
        specify the application id in the URL.
    """
    application = Application.query.get(idx)
    if application is None:
        return jsonify({"message": "Application could not be found."}), 404
    if application.status != "pending":
        resp = {"message": "The Application has already fullfilled"}
        return jsonify(resp), 400
    db.session.delete(application)
    db.session.commit()
    return jsonify({"message": "Successful Operation"})


@bp.route('/lotteries/<int:idx>/draw', methods=['POST'])
@spec('api/lotteries/draw.yml')
@login_required('admin')
def draw_lottery(idx):
    """
        draw lottery as adminstrator
    """
    lottery = Lottery.query.get(idx)
    if lottery is None:
        return jsonify({"message": "Lottery could not be found."}), 404

    not_acceptable_resp = jsonify({"message": "Not acceptable time"})
    try:
        # Get time index with current datetime
        index = get_draw_time_index()
    except (OutOfHoursError, OutOfAcceptingHoursError):
        return not_acceptable_resp, 400

    if index != lottery.index:
        return not_acceptable_resp, 400

    winners = draw_one(lottery)

    result = users_schema.dump(winners)
    return jsonify(result[0])


@bp.route('/draw_all', methods=['POST'])
@spec('api/draw_all.yml')
@login_required('admin')
def draw_all_lotteries():
    """
        draw all available lotteries as adminstrator
    """
    try:
        # Get time index with current datetime
        index = get_draw_time_index()
    except (OutOfHoursError, OutOfAcceptingHoursError):
        return jsonify({"message": "Not acceptable time"}), 400

    winners = draw_all_at_index(index)

    flattened = list(chain.from_iterable(winners))
    result = users_schema.dump(flattened)
    return jsonify(result[0])


@bp.route('/lotteries/<int:idx>/winners')
@spec('api/lotteries/winners.yml')
def get_winners_id(idx):
    """
        Return winners' public_id for 'idx' lottery
    """
    lottery = Lottery.query.get(idx)
    if lottery is None:
        return jsonify({"message": "Lottery could not be found."}), 400
    if not lottery.done:
        return jsonify({"message": "This lottery is not done yet."}), 400

    def public_id_generator():
        for app in lottery.application:
            if app.status == 'won':
                yield app.user.public_id
    return jsonify(list(public_id_generator()))


@bp.route('/status', methods=['GET'])
@spec('api/status.yml')
@login_required('normal')
def get_status():
    """
        return user's id and applications
    """
    user = User.query.filter_by(id=g.token_data['user_id']).first()
    result = user_schema.dump(user)[0]
    return jsonify(result)


@bp.route('/public_id/<string:secret_id>', methods=['GET'])
@spec('api/translate_secret_to_public.yml')
@login_required('normal', 'checker', 'admin')
def translate_secret_to_public(secret_id):
    """translate secret_id into public_id
        This will used for checking the guests at each classes
    """
    user = User.query.filter_by(secret_id=secret_id).first()
    if not user:
        return jsonify({"message": "no such user found"}), 404
    else:
        return jsonify({"public_id": user.public_id})


@bp.route('/ids_hash', methods=['GET'])
@spec('api/ids_hash.yml')
def ids_hash():
    """return sha256 hash of `ids.json` used in background
    """
    try:
        checksum = calc_sha256(current_app.config['ID_LIST_FILE'])
    except FileNotFoundError:
        checksum = ""
    return jsonify({"sha256": checksum})

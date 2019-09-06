from itertools import chain
from datetime import date
from jinja2 import Environment, FileSystemLoader

from flask import Blueprint, jsonify, g, request, current_app
from api.models import Lottery, Classroom, User, Application, db, apps2members
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
from api.auth import (
        login_required,
        todays_user,
        UserNotFoundError,
        UserDisabledError
)
from api.swagger import spec
from api.time_management import (
    get_draw_time_index,
    OutOfHoursError,
    OutOfAcceptingHoursError,
    get_time_index,
    get_prev_time_index
)
from api.draw import (
    draw_one,
    draw_all_at_index,
)
from api.error import error_response
from api.utils import calc_sha256

from cards.id import encode_public_id

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
        return error_response(7)  # Not found
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


@bp.route('/lotteries/available')
@spec('api/lotteries/available.yml')
def list_available_lotteries():
    """
        return available lotteries list.
    """
# those two values will be used in the future. now, not used. see issue #62 #63
#     filter = request.args.get('filter')
#     sort = request.args.get('sort')

    try:
        index = get_time_index()
    except (OutOfAcceptingHoursError, OutOfHoursError):
        return jsonify([])
    lotteries = Lottery.query.filter_by(index=index)

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
        return error_response(7)  # Not found
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
        return error_response(7)  # Not found
    try:
        current_index = get_time_index()
    except (OutOfHoursError, OutOfAcceptingHoursError):
        # We're not accepting any application in this hours.
        return error_response(14)
    if lottery.index != current_index:
        return error_response(11)  # This lottery is not acceptable now.

    # 2. 3. 4.
    group_members = set()
    if len(group_members_secret_id) != 0:
        if len(group_members_secret_id) > 3:
            return error_response(21)
        for sec_id in group_members_secret_id:
            try:
                user = todays_user(secret_id=sec_id)
            except (UserNotFoundError, UserDisabledError):
                return error_response(1)  # Invalid group member secret id
            group_members.add(user)
        if len(group_members) != len(group_members_secret_id):
            # Group members duplicated
            return error_response(23)
        for user in group_members:
            previous = Application.query.filter_by(user_id=user.id,
                                                   created_on=date.today())
            if any(app.lottery.index == lottery.index and
                   app.lottery.id != lottery.id
                   for app in previous.all()):
                # Someone in the group is
                # already applying to a lottery in this period
                return error_response(8)
            if any(app.lottery.index == lottery.index and
                   app.lottery.id == lottery.id
                   for app in previous.all()):

                # someone in the group is already
                # applying to this lottery
                return error_response(9)

    # 5.
    rep_user = User.query.filter_by(id=g.token_data['user_id']).first()
    previous = Application.query.filter_by(user_id=rep_user.id,
                                           created_on=date.today())
    if any(app.lottery.index == lottery.index and
            app.lottery.id != lottery.id
            for app in previous.all()):
        # You're already applying to a lottery in this period
        return error_response(17)
    if any(app.lottery.index == lottery.index and
            app.lottery.id == lottery.id
            for app in previous.all()):
        # Your application is already accepted
        return error_response(16)
    # access DB
    # 6. 7.
    if len(group_members) == 0:
        new_application = Application(
            lottery_id=lottery.id, user_id=rep_user.id, status="pending")
        db.session.add(new_application)
        db.session.commit()
        result = application_schema.dump(new_application)[0]
        return jsonify(result)
    # 8.
    members_app = [Application(
            lottery_id=lottery.id, user_id=member.id, status="pending")
            for member in group_members]

    for application in members_app:
        db.session.add(application)
    db.session.commit()
    rep_application = Application(
        lottery_id=lottery.id, user_id=rep_user.id, status="pending",
        is_rep=True,
        group_members=apps2members(members_app))
    db.session.add(rep_application)

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
    applications = Application.query.filter_by(user_id=user.id,
                                               created_on=date.today())
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
        user_id=user.id, created_on=date.today()).filter_by(id=idx).first()
    if application is None:
        return error_response(7)  # Not found
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
        return error_response(7)  # Not found
    if application.status != "pending":
        # The Application has already fullfilled
        return error_response(10)
    for member in application.group_members:
        db.session.delete(member.own_application)
        db.session.delete(member)
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
        return error_response(7)  # Not found

    try:
        # Get time index with current datetime
        index = get_draw_time_index()
    except (OutOfHoursError, OutOfAcceptingHoursError):
        return error_response(6)  # Not acceptable time

    if index != lottery.index:
        return error_response(6)  # Not acceptable time

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
        return error_response(6)  # Not acceptable time

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
        return error_response(7)  # Not found
    if not lottery.done:
        return error_response(12)  # This lottery is not done yet.

    def public_id_generator():
        for app in lottery.application:
            if app.created_on == date.today() and app.status == 'won':
                yield app.user.public_id
    return jsonify(list(public_id_generator()))


@bp.route('/status', methods=['GET'])
@spec('api/status.yml')
@login_required('normal', 'checker')
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
        return error_response(5)  # no such user found
    else:
        return jsonify({"public_id": encode_public_id(user.public_id)})


@bp.route('/ids_hash', methods=['GET'])
@spec('api/ids_hash.yml')
def ids_hash():
    """return sha256 hash of `ids.json` used in background
    """
    try:
        checksum = calc_sha256(current_app.config['ID_LIST_FILE'])
    except FileNotFoundError:
        return error_response(20)  # ID_LIST_FILE not found
    return jsonify({"sha256": checksum})


@bp.route('/checker/<int:classroom_id>/<string:secret_id>', methods=['GET'])
@spec('api/checker.yml')
@login_required('checker')
def check_id(classroom_id, secret_id):
    """return result of application of the user of given classroom
        Args:
            classroom_id (int): target classroom
            secret_id (string): secret id of target user
    """
    user = User.query.filter_by(secret_id=secret_id).first()
    if not user:
        return error_response(5)  # no such user found
    try:
        index = get_prev_time_index()
    except (OutOfHoursError, OutOfAcceptingHoursError):
        return error_response(6)  # not acceptable time
    lottery = Lottery.query.filter_by(classroom_id=classroom_id,
                                      index=index).first()
    application = Application.query.filter_by(
                    user=user, lottery=lottery, created_on=date.today()).first()
    if not application:
        return error_response(19)  # no application found

    return jsonify({"status": application.status})


@bp.route('/render_results', methods=['GET'])
@spec('api/results.yml')
def results():
    """return HTML file that contains the results of previous lotteries
        This endpoint will be used for printing PDF
        which will be put on the wall.
        whoever access here can get the file. This is not a problem because
        those infomations are public.
    """
    #  1. Get previous time index
    #  2. Get previous lotteries using index
    #  3. Search for caches for those lotteries
    #  4. If cache was found, return it
    #  5. Make 2 public_id lists, based on user's 'kind'('student', 'visitor')
    #  6. Send them to the jinja template
    #  8. Caches that file locally
    #  9. Return file

    def public_id_generator(lottery, kind):
        """return list of winners' public_id for selected 'kind'
            original at: L.336, written by @tamazasa
        """
        for app in lottery.application:
            if app.created_on == date.today() and \
               app.status == 'won' and app.user.kind == kind:
                yield encode_public_id(app.user.public_id)

    # 1.
    try:
        index = get_prev_time_index()
    except (OutOfHoursError, OutOfAcceptingHoursError):
        return error_response(6)  # not acceptable time
    # 2.
    lotteries = Lottery.query.filter_by(index=index)

    kinds = ('visitor', 'student')

    # 5.
    data = []

    for lottery in lotteries:
        cl = Classroom.query.get(lottery.classroom_id)

        lottery_result = []
        for kind in kinds:
            public_ids = list(sorted(public_id_generator(lottery, kind)))
            result = {'kind': kind,
                      'winners': public_ids}
            lottery_result.append(result)

        data.append({'classroom': str(cl),
                     'kinds': lottery_result})

    # 6.
    env = Environment(loader=FileSystemLoader('api/templates'))
    template = env.get_template('results.html')
    return template.render(lotteries=data)


@bp.route('/health')
@spec('api/health.yml')
def health():
    return jsonify({'message': 'good to go'})

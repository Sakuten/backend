from marshmallow import Schema, fields
from flask import current_app
from api.models import Application, Lottery
from cards.id import encode_public_id
from api.time_management import mod_time
import base64


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    secret_id = fields.Str()
    public_id = fields.Method("get_public_id_str", dump_only=True)
    win_count = fields.Int()
    lose_count = fields.Int()
    kind = fields.Str()

    def get_public_id_str(self, user):
        return encode_public_id(user.public_id)


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class GroupMemberSchema(Schema):
    id = fields.Int(dump_only=True)
    public_id = fields.Method("get_public_id_str", dump_only=True)

    def get_public_id_str(self, group_member):
        return encode_public_id(group_member.user.public_id)


group_member_schema = GroupMemberSchema()
group_members_schema = GroupMemberSchema(many=True)


class ApplicationSchema(Schema):
    id = fields.Int(dump_only=True)
    status = fields.Str()
    lottery = fields.Method("get_lottery", dump_only=True)
    is_rep = fields.Boolean()
    group_members = fields.Nested(GroupMemberSchema, many=True)
    is_member = fields.Method("get_is_member", dump_only=True)

    def get_lottery(self, application):
        lottery = Lottery.query.get(application.lottery_id)
        return lottery_schema.dump(lottery)[0]

    def get_is_member(self, application):
        index = application.lottery.index
        reps = (app for app in Application.query.all()
                if app.is_rep and app.lottery.index == index)
        return any(application.id == member.own_application.id
                   for rep in reps
                   for member in rep.group_members)


application_schema = ApplicationSchema()
applications_schema = ApplicationSchema(many=True)


class ClassroomSchema(Schema):
    id = fields.Int(dump_only=True)
    grade = fields.Int()
    index = fields.Int()
    title = fields.Method("classroom_title", dump_only=True)
    name = fields.Method("classroom_name", dump_only=True)

    def classroom_name(self, classroom):
        return classroom.get_classroom_name()

    def classroom_title(self, classroom):
        return base64.b64decode(classroom.title).decode('utf-8')


classroom_schema = ClassroomSchema()
classrooms_schema = ClassroomSchema(many=True)


class LotterySchema(Schema):
    id = fields.Int(dump_only=True)
    classroom_id = fields.Int()
    index = fields.Int()
    done = fields.Boolean()
    name = fields.Method("format_name", dump_only=True)
    winners = fields.Method("get_winners", dump_only=True)
    end_of_drawing = fields.Method("calc_end_of_drawing")

    def format_name(self, lottery):
        grade = lottery.classroom.grade
        name = lottery.classroom.get_classroom_name()
        index = lottery.index
        return f"{grade}{name}.{index}"

    def get_winners(self, lottery):
        winners = Application.query.filter_by(
            lottery_id=lottery.id, status="win").all()
        return [winner.public_id for winner in winners]

    def calc_end_of_drawing(self, lottery):
        index = lottery.index
        drawing_ext = current_app.config['DRAWING_TIME_EXTENSION']
        time_ponit = current_app.config['TIMEPOINTS'][index][1]
        return str(mod_time(time_ponit, drawing_ext))


lottery_schema = LotterySchema()
lotteries_schema = LotterySchema(many=True)


class ErrorSchema(Schema):
    code = fields.Int()
    message = fields.Str()


error_schema = ErrorSchema()

from marshmallow import Schema, fields
from api.models import Application, Lottery
from cards.id import encode_public_id


class ApplicationSchema(Schema):
    id = fields.Int(dump_only=True)
    status = fields.Str()
    lottery = fields.Method("get_lottery", dump_only=True)
    is_rep = fields.Boolean()
    group_members = fields.List(fields.Int)

    def get_lottery(self, application):
        lottery = Lottery.query.get(application.lottery_id)
        return lottery_schema.dump(lottery)[0]


application_schema = ApplicationSchema()
applications_schema = ApplicationSchema(many=True)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    secret_id = fields.Str()
    public_id = fields.Method("get_public_id_str", dump_only=True)
    application_history = fields.Method("get_applications", dump_only=True)

    def get_applications(self, user):
        lotteries = Application.query.filter_by(user_id=user.id).all()
        return applications_schema.dump(lotteries)[0]

    def get_public_id_str(self, user):
        return encode_public_id(user.public_id)


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class ClassroomSchema(Schema):
    id = fields.Int(dump_only=True)
    grade = fields.Int()
    index = fields.Int()
    name = fields.Method("classroom_name", dump_only=True)

    def classroom_name(self, classroom):
        return classroom.get_classroom_name()


classroom_schema = ClassroomSchema()
classrooms_schema = ClassroomSchema(many=True)


class LotterySchema(Schema):
    id = fields.Int(dump_only=True)
    classroom_id = fields.Int()
    index = fields.Int()
    done = fields.Boolean()
    name = fields.Method("format_name", dump_only=True)
    winners = fields.Method("get_winners", dump_only=True)

    def format_name(self, lottery):
        grade = lottery.classroom.grade
        name = lottery.classroom.get_classroom_name()
        index = lottery.index
        return f"{grade}{name}.{index}"

    def get_winners(self, lottery):
        winners = Application.query.filter_by(
            lottery_id=lottery.id, status="won").all()
        return [winner.public_id for winner in winners]


lottery_schema = LotterySchema()
lotteries_schema = LotterySchema(many=True)

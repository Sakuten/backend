from marshmallow import Schema, fields
from api.models import Application, Lottery


class ApplicationSchema(Schema):
    id = fields.Int(dump_only=True)
    status = fields.Str()
    lottery = fields.Method("get_lottery", dump_only=True)

    def get_lottery(self, application):
        lottery = Lottery.query.get(application.lottery_id)
        return lottery_schema.dump(lottery)[0]

application_schema = ApplicationSchema()
applications_schema = ApplicationSchema(many=True)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()
    application_history = fields.Method("get_applications", dump_only=True)

    def get_applications(self, user):
        lotteries = Application.query.filter_by(user_id=user.id).all()
        return applications_schema.dump(lotteries)[0]


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
        winners = Application.query.filter_by(lottery_id=lottery.id, status="won").all()
        winners_id = []
        for winner in winners:
            winners_id.append(winner.user_id)
        return winners_id



lottery_schema = LotterySchema()
lotteries_schema = LotterySchema(many=True)

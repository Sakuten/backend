from marshmallow import Schema, fields
from api.models import Lottery, Classroom, User, Application, db

class ApplicationSchema(Schema):
    id = fields.Int(dump_only=True)
    lottery_id = fields.Int()
    user_id = fields.Int()
    status = fields.Boolean()

application_schema = ApplicationSchema()
applications_schema = ApplicationSchema(many=True)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()
    applications = fields.Method("get_applications", dump_only=True)

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

    def format_name(self, lottery):
        grade = lottery.classroom.grade
        name = lottery.classroom.get_classroom_name()
        index = lottery.index
        return f"{grade}{name}.{index}"

lottery_schema = LotterySchema()
lotteries_schema = LotterySchema(many=True)

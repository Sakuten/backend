from marshmallow import Schema, fields
from api.models import Lottery, Classroom, User, Application, db

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()

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
    name = fields.Method("format_name", dump_only=True)
    applicants = fields.Method("get_applicants", dump_only=True)

    def format_name(self, lottery):
        grade = lottery.classroom.grade
        name = lottery.classroom.get_classroom_name()
        index = lottery.index
        return f"{grade}{name}.{index}"

    def get_applicants(self, lottery):
        apps = Application.query.filter_by(lottery_id=lottery.id).all()
        return users_schema.dump([app.user for app in apps])[0]

lottery_schema = LotterySchema()
lotteries_schema = LotterySchema(many=True)

from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()
    applying_lottery_id = fields.Int()
    application_status = fields.Boolean()

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

    def format_name(self, lottery):
        grade = lottery.classroom.grade
        name = lottery.classroom.get_classroom_name()
        index = lottery.index
        return f"{grade}{name}.{index}"


lottery_schema = LotterySchema()
lotteries_schema = LotterySchema(many=True)

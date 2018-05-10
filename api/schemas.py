from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()
    applying_lottery_id = fields.Int()
    application_status = fields.Boolean()


class ClassroomSchema(Schema):
    id = fields.Int(dump_only=True)
    grade = fields.Int()
    index = fields.Int()
    name = fields.Method("classroom_name", dump_only=True)

    def classroom_name(self, classroom):
        return classroom.get_classroom_name()


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


user_schema = UserSchema()
lottery_schema = LotterySchema()
classroom_schema = ClassroomSchema()
users_schema = UserSchema(many=True)
lotteries_schema = LotterySchema(many=True)
classrooms_schema = ClassroomSchema(many=True)

from marshmallow import Schema, fields

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
        return "{}{}.{}".format(lottery.classroom.grade, lottery.classroom.get_classroom_name(), lottery.index)

lottery_schema = LotterySchema()
classroom_schema = ClassroomSchema()
lotteries_schema = LotterySchema(many=True)
classrooms_schema = ClassroomSchema(many=True)

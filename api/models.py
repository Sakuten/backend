from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import UniqueConstraint
from werkzeug.security import check_password_hash

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    passhash = db.Column(db.String(64))

    def __repr__(self):
        return '<User %r>' % self.username

    def get_user_id(self):
        return self.id

    def check_password(self, password):
        return check_password_hash(self.passhash, password)


class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Integer)
    index = db.Column(db.Integer)

    def __repr__(self):
        return "<Classroom %r%r>".format(self.grade, self.get_classroom_name)

    def get_classroom_name(self):
        names = ['A', 'B', 'C', 'D', 'E']
        return names[self.index]


class Lottery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey(
        'classroom.id', ondelete='CASCADE'))
    classroom = db.relationship('Classroom')
    index = db.Column(db.Integer)

    def __repr__(self):

        return "<Lottery {}.{}>".format(self.classroom, self.index)

class Application(db.Model):
    __table_args__ = (UniqueConstraint("lottery_id", "user_id", name="unique_idx_lottery_user"),)

    id = db.Column(db.Integer, primary_key=True)
    lottery_id = db.Column(db.Integer, db.ForeignKey(
        'lottery.id', ondelete='CASCADE'))
    lottery = db.relationship('Lottery')
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete='CASCADE'))
    user = db.relationship('User')
    status = db.Column(db.Boolean)

    def __repr__(self):
        return "<Application {}{}>".format(self.lottery, self.user)

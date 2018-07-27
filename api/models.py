from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import UniqueConstraint
from cards.id import encode_public_id

db = SQLAlchemy()


class User(db.Model):
    """
        User model for DB
        Args:
            public_id (int): public id.
            secret_id (int): secret id.
        DB contents:
            public_id (int): public id.
            secret_id (int): secret id.
    """
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Integer, unique=True)
    secret_id = db.Column(db.String(40), unique=True)
    authority = db.Column(db.String(20))

    def __repr__(self):
        authority_str = f'({self.authority})' if self.authority else ''
        return f'<User {encode_public_id(self.public_id)} {authority_str}>'


class Classroom(db.Model):
    """
        Classroom model for DB
        Args:
            grade (int): grade of the classroom
            index (int): class number(0->A,1->B,2->C,3->D)
        DB contents:
            id (int): classroom unique id
            grade (int): grade of the classroom
            index (int): class number(0->A,1->B,2->C,3->D)
    """
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Integer)
    index = db.Column(db.Integer)

    def __repr__(self):
        return "<Classroom %r%r>".format(self.grade, self.get_classroom_name)

    def get_classroom_name(self):
        """
            return class  number in Alphabet
        """
        names = ['A', 'B', 'C', 'D', 'E']
        return names[self.index]


class Lottery(db.Model):
    """
        Lottery model for DB
        Args:
            classroom_id (int): classroom id(unique id)
            index (int): class number(0->A,1->B,2->C,3->D)
            done (bool): whether the lottery is done or not
        DB contents:
            id (int): lottery unique id
            classroom_id (int): associated classroom id
            classroom (relationship): associated classroom
            index (int): class number(0->A,1->B,2->C,3->D)
            done (bool): whether it's done or not
    """
    id = db.Column(db.Integer, primary_key=True)  # 'id' should be defined,
    classroom_id = db.Column(db.Integer, db.ForeignKey(
        'classroom.id', ondelete='CASCADE'))
    classroom = db.relationship('Classroom')
    index = db.Column(db.Integer)
    done = db.Column(db.Boolean)

    def __repr__(self):

        return "<Lottery {}.{}>".format(self.classroom, self.index)


class Application(db.Model):
    """application model for DB
        DB contents:
            id (int): application unique id
            lottery_id (int): lottery id this application linked to
            user_id (int): user id of this application
            status (Boolen): whether chosen or not. initalized with None
    """
    __table_args__ = (UniqueConstraint(
        "lottery_id", "user_id", name="unique_idx_lottery_user"),)

    id = db.Column(db.Integer, primary_key=True)
    lottery_id = db.Column(db.Integer, db.ForeignKey(
        'lottery.id', ondelete='CASCADE'))
    lottery = db.relationship('Lottery')
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete='CASCADE'))
    user = db.relationship('User')
    # status: [ pending, won, lose ]
    status = db.Column(db.String,
                       default="pending",
                       nullable=False)

    def __repr__(self):
        return "<Application {}{}>".format(self.lottery, self.user)

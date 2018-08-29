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
            lose_count (int): how many times the user lost
    """
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Integer, unique=True)
    secret_id = db.Column(db.String(40), unique=True)
    authority = db.Column(db.String(20))
    lose_count = db.Column(db.Integer)

    def __repr__(self):
        authority_str = f'({self.authority})' if self.authority else ''
        return f'<User ({self.lose_count}) ' \
               f'{encode_public_id(self.public_id)} {authority_str}>'


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
            index (int): number of peformance. {0..4}
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
            is_rep (bool): whether rep of a group or not
    """
    __tablename__ = 'application'
    __table_args__ = (UniqueConstraint(
        "lottery_id", "user_id", name="unique_idx_lottery_user"),)

    id = db.Column(db.Integer, primary_key=True)
    lottery_id = db.Column(db.Integer, db.ForeignKey(
        'lottery.id', ondelete='CASCADE'))
    lottery = db.relationship('Lottery', backref='application')
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete='CASCADE'))
    user = db.relationship('User')
    # status: [ pending, won, lose ]
    status = db.Column(db.String,
                       default="pending",
                       nullable=False)
    is_rep = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "<Application {}{}{} {}>".format(
                                            self.lottery, self.user,
                                            " (rep)" if self.is_rep else "",
                                            self.status)


class GroupMember(db.Model):
    """group-member model for DB
        DB contents:
            id (int): group member unique id
            user_id (int): user id of this member
            rep_application_id (int): rep application id
    """
    __tablename__ = 'group_members'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
            db.Integer,
            db.ForeignKey('user.id', ondelete='CASCADE'),
            db.ForeignKey('application.user_id', ondelete='CASCADE'))
    user = db.relationship('User')
    own_application = db.relationship('Application',
                                      foreign_keys=[user_id],
                                      viewonly=True)

    rep_application_id = db.Column(db.Integer, db.ForeignKey(
        'application.id', ondelete='CASCADE'))
    rep_application = db.relationship('Application',
                                      foreign_keys=[rep_application_id],
                                      backref='group_members')

    def __repr__(self):
        return f"<GroupMember {self.user}>"

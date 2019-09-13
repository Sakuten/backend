from flask_sqlalchemy import SQLAlchemy
from cards.id import encode_public_id
from datetime import date

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
            win_count (int): how many times the user won
            lose_count (int): how many times the user lost
    """
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Integer, unique=True)
    secret_id = db.Column(db.String(40), unique=True)
    authority = db.Column(db.String(20))
    win_count = db.Column(db.Integer, default=0)
    lose_count = db.Column(db.Integer, default=0)
    waiting_count = db.Column(db.Integer, default=0)
    kind = db.Column(db.String(30))
    first_access = db.Column(db.Date, default=None)

    def __repr__(self):
        authority_str = f'({self.authority})' if self.authority else ''
        return f'<User {encode_public_id(self.public_id)} {authority_str} ' + \
               f'{self.win_count}-{self.lose_count}/{self.waiting_count}>'


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
    title = db.Column(db.String(300))

    def __repr__(self):
        return "<Classroom %r%r>".format(self.grade, self.get_classroom_name)

    def __str__(self):
        return f'{self.grade}{self.get_classroom_name()}'

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
        DB contents:
            id (int): lottery unique id
            classroom_id (int): associated classroom id
            classroom (relationship): associated classroom
            index (int): number of peformance. {0..4}
    """
    id = db.Column(db.Integer, primary_key=True)  # 'id' should be defined,
    classroom_id = db.Column(db.Integer, db.ForeignKey(
        'classroom.id', ondelete='CASCADE'))
    classroom = db.relationship('Classroom')
    index = db.Column(db.Integer)

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
            advantage (int): how much advantage does user have
            created_on (date): when applciation is made
    """
    __tablename__ = 'application'

    id = db.Column(db.Integer, primary_key=True)
    lottery_id = db.Column(db.Integer, db.ForeignKey(
        'lottery.id', ondelete='CASCADE'))
    lottery = db.relationship('Lottery', backref='application')
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete='CASCADE'))
    user = db.relationship('User')
    # status: [ pending, won, lose, waiting, waiting-pending(internal) ]
    status = db.Column(db.String,
                       default="pending",
                       nullable=False)
    is_rep = db.Column(db.Boolean, default=False)
    created_on = db.Column(db.Date, nullable=False)
    advantage = None
    group_members_not_rep = db.relationship(
        'GroupMember',
        backref='own_application',
        cascade='all, delete-orphan',
        foreign_keys="GroupMember.own_application_id")
    group_members = db.relationship(
        'GroupMember',
        backref='rep_application',
        cascade='all, delete-orphan',
        foreign_keys="GroupMember.rep_application_id")
    # groupmember_id = db.Column(db.Integer, db.ForeignKey(
    #     'group_members.id', ondelete='CASCADE'))
    # me_group_member = db.relationship('GroupMember', backref='application')

    def __init__(self, **kwargs):
        """
            construct object with column `created_on` automatically set
        """
        super().__init__(created_on=date.today(), **kwargs)

    def __repr__(self):
        return "<Application {}{}{} {}>".format(
            self.lottery, self.user,
            " (rep)" if self.is_rep else "",
            self.status)

    def get_advantage(self):
        """
            returns multiplier indicating how more likely
            the application is to win
        """
        if self.advantage:
            return self.advantage
        elif self.user.lose_count == 0:
            return 1
        else:
            return 3 ** max(0, (                # at least 3^0 (= 1)
                self.user.lose_count            # increase exponentially
                + self.user.waiting_count / 2   # 2 waiting == 1 lose
                - self.user.win_count
                ))

    def set_advantage(self, advantage):
        self.advantage = advantage

    def set_status(self, new_status):
        if new_status not in {"pending", "waiting-pending",
                              "won", "lose", "waiting"}:
            raise ValueError

        if self.status == "won":
            self.user.win_count -= 1
        elif self.status == "lose":
            self.user.lose_count -= 1
        elif self.status == "waiting":
            self.user.waiting_count -= 1

        if new_status == "won":
            self.user.win_count += 1
        elif new_status == "lose":
            self.user.lose_count += 1
        elif new_status == "waiting":
            self.user.waiting_count += 1

        self.status = new_status

        db.session.add(self.user)
        db.session.add(self)
        db.session.commit()


class GroupMember(db.Model):
    """group-member model for DB
        DB contents:
            id (int): group member unique id
            user_id (int): user id of this member
            rep_application_id (int): rep application id
    """
    __tablename__ = 'group_members'
    __mapper_args__ = {'confirm_deleted_rows': False}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')

    own_application_id = db.Column(db.Integer, db.ForeignKey(
        'application.id', ondelete='CASCADE'))

    rep_application_id = db.Column(db.Integer, db.ForeignKey(
        'application.id', ondelete='CASCADE'))

    def __repr__(self):
        return f"<GroupMember {self.user}>"


class Error(db.Model):
    """
        Error model
        DB contents:
            code (int): identical error code, which has a common meaning
                                    between frontend and backend
            http_code (int): the HTTP status code
            message (str): the description message
    """
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, unique=True)
    http_code = db.Column(db.Integer)
    message = db.Column(db.String(200))

    def __repr__(self):
        return f'<Error {self.code}: "{self.message}">'


def app2member(application):
    return GroupMember(user_id=application.user_id,
                       own_application=application)


def apps2members(applications):
    return [app2member(app) for app in applications]

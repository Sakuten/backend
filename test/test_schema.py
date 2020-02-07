from api.models import User, Lottery, Application, app2member, db
from api.schemas import application_schema


def test_application_is_member(client):
    with client.application.app_context():
        target_lot = Lottery.query.first()

        users = User.query.all()
        member = users[0]

        member_app = Application(lottery=target_lot, user=member)
        rep = users[1]
        rep_app = Application(lottery=target_lot, user=rep, is_rep=True,
                              group_members=[app2member(member_app)])

        db.session.add(member_app)
        db.session.add(rep_app)
        db.session.commit()

        dumpdata = application_schema.dump(member_app)[0]
        assert dumpdata['is_member']


def test_application_not_member(client):
    with client.application.app_context():
        target_lot = Lottery.query.first()

        member = User.query.first()

        member_app = Application(lottery=target_lot, user=member)

        db.session.add(member_app)
        db.session.commit()

        dumpdata = application_schema.dump(member_app)[0]
        assert not dumpdata['is_member']


def test_classroom_time(client):
    with client.application.app_context():
        target_classroom = Classroom.query.first()
	
        dumpdata = classroom_schema.dump(target_classroom)
        assert 'begin_time' in dumpdata
        assert 'end_time' in dumpdata

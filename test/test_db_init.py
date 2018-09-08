from api.models import db, Classroom
from api.app import create_app, init_and_generate

def test_db_not_force_init(client):
    with client.application.app_context():
        dummy = Classroom(grade=0, index=0)
        db.session.add(dummy)
        db.session.commit()
        dummy_id = dummy.id
        assert Classroom.query.get(dummy_id) is not None

        client.application.config['DB_FORCE_INIT'] = False
        init_and_generate()
        assert Classroom.query.get(dummy_id) is not None

def test_db_force_init(client):
    with client.application.app_context():
        dummy = Classroom(grade=0, index=0)
        db.session.add(dummy)
        db.session.commit()
        dummy_id = dummy.id
        assert Classroom.query.get(dummy_id) is not None

        client.application.config['DB_FORCE_INIT'] = True
        init_and_generate()
        assert Classroom.query.get(dummy_id) is None

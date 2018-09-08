import pytest

from api.models import db, Classroom
from api.app import create_app, init_and_generate

@pytest.mark.parametrize("force_init", [True, False])
def test_db_init(client, force_init):
    with client.application.app_context():
        dummy = Classroom(grade=0, index=0)
        db.session.add(dummy)
        db.session.commit()
        dummy_id = dummy.id

        client.application.config['DB_FORCE_INIT'] = force_init
        init_and_generate()
        if force_init:
            assert Classroom.query.get(dummy_id) is None
        else:
            assert Classroom.query.get(dummy_id) is not None

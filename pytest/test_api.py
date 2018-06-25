import os
import tempfile

import pytest

from api.app import create_app, generate
from cryptography.fernet import Fernet

@pytest.fixture
def app():
    db_fd, database = tempfile.mkstemp()
    app = create_app({
        'SECRET_KEY': Fernet.generate_key(),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_DATABASE_URI': database,
        'TESTING': True,
    })

    yield app

    os.close(db_fd)
    os.unlink(app.config['SQLALCHEMY_DATABASE_URI'])

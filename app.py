from api.app import create_app, initdb, generate
from cryptography.fernet import Fernet

app = create_app({
    'SECRET_KEY': Fernet.generate_key(),
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': 'mysql+mysqlconnector://root:password@mysql/db',
})


@app.cli.command("initdb")
def initdb_():
    initdb()


@app.cli.command("generate")
def generate_():
    generate()

from api.app import create_app

app = create_app({
    'SECRET_KEY': 'secret',
    'ENABLE_SIGNUP': False,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite',
})


@app.cli.command()
def initdb():
    from api.models import db
    db.create_all()

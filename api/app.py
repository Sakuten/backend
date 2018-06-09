from flask import Flask
from flask_cors import CORS
from .routes import auth, api
from .models import db


def create_app(config=None):
    app = Flask(__name__)
    # load app sepcified configuration
    CORS(app, supports_credentials=True)
    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)

    db.init_app(app)

    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(api.bp, url_prefix='/api')

    with app.app_context():
        if app.config['ENV'] == 'development':
            app.logger.warning('Regenerating test data for development (because FLASK_ENV == development)')
            clear_data(db)
            initdb()
            generate()

    return app

def clear_data(db):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        db.session.execute(table.delete())
        db.session.commit()

def initdb():
    from api.models import db
    db.create_all()

def generate():
    from api.models import Lottery, Classroom, User, db
    from werkzeug.security import generate_password_hash

    total_index = 4
    grades = [5, 6]

    def classloop(f):
        for grade in grades:
            for class_index in range(4):  # 0->A 1->B 2->C 3->D
                f(grade, class_index)

    def create_classrooms(grade, class_index):
        room = Classroom(grade=grade, index=class_index)
        db.session.add(room)

    def create_lotteries(grade, class_index):
        room = Classroom.query.filter_by(
            grade=grade, index=class_index).first()
        for perf_index in range(total_index):
            lottery = Lottery(classroom_id=room.id, index=perf_index, done=False)
            db.session.add(lottery)

    classloop(create_classrooms)
    db.session.commit()
    classloop(create_lotteries)
    db.session.commit()

    def make_debug_user(name):
        user = User(username=name, passhash=generate_password_hash(name))
        db.session.add(user)
        db.session.commit()
        return user

    make_debug_user('admin')
    for i in range(5):
        make_debug_user(f"example{i}")

    db.session.commit()


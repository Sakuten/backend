from flask import Flask
from flask_cors import CORS
from sqlalchemy.exc import ProgrammingError
from .routes import auth, api
from .models import db
import os
import sys

config = {
    "development": "api.config.DevelopmentConfig",
    "testing": "api.config.TestingConfig",
    "preview": "api.config.PreviewDeploymentConfig",
    "deployment": "api.config.DeploymentConfig",
    "default": "api.config.DevelopmentConfig"
}


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    # load app sepcified configuration
    CORS(app, supports_credentials=True)

    config_name = os.getenv('FLASK_CONFIGURATION', 'default')

    app.config.from_object(config[config_name])
    app.config.from_pyfile('config.cfg', silent=True)

    if app.config.get('SQLALCHEMY_DATABASE_URI', None) is None:
        app.logger.error("SQLALCHEMY_DATABASE_URI is not set. Didn't you forget to set it in instance/config.cfg?")
        sys.exit(4) # Return 4 to exit gunicorn

    if app.config.get('SECRET_KEY', None) is None:
        app.logger.error("SECRET_KEY is not set Didn't you forget to set it in instance/config.cfg?")
        sys.exit(4) # Return 4 to exit gunicorn

    db.init_app(app)

    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(api.bp, url_prefix='/api')

    with app.app_context():
        if app.config['ENV'] == 'development':
            app.logger.warning(
                'Regenerating test data for development '
                '(because FLASK_ENV == development)')
            try:
                db.drop_all()
            except ProgrammingError:
                app.logger.warning('Good luck with this ;)')
            try:
                db.create_all()
            except ProgrammingError:
                app.logger.warning('Good luck with this ;)')
            # initdb(app, db)
            generate()

    return app


def initdb(app, db):
    from api.models import db
    db.create_all()


def generate():
    from .models import Lottery, Classroom, User, db
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
            lottery = Lottery(classroom_id=room.id,
                              index=perf_index, done=False)
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

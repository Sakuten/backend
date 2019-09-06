from flask import Flask, current_app
from flask_cors import CORS
import sqlalchemy
from .routes import auth, api
from .swagger import swag
from .models import db, User
from cards.id import load_id_json_file, decode_public_id
import os
import sys
import json
import base64

config = {
    "development": "api.config.DevelopmentConfig",
    "testing": "api.config.TestingConfig",
    "preview": "api.config.PreviewDeploymentConfig",
    "deployment": "api.config.DeploymentConfig",
    "default": "api.config.DevelopmentConfig"
}


def create_app():
    """create base flask application
        1. generate flask application
        2. set config based on 'FLASK_CONFIGURATION'
        3. initialize DB
        4. some other settings

        Args:
            no-args needed

        ENVIRONMENT_VALIABLES:
            FLASK_CONFIGURATION (str): define config type.
                ('defalut'|'development'|'testing'|'preview'|'deployment')
        Return:
            app (Flask): generated flask application
        Exit Status:
            4 : SQLALCHEMY_DATABASE_URI or SECRET_KEY is not set.

    """
    app = Flask(__name__, instance_relative_config=True)

    # Allow to access with or without trailing slash
    app.url_map.strict_slashes = False

    CORS(app, supports_credentials=True)

    # load app sepcified configuration
    config_name = os.getenv('FLASK_CONFIGURATION', 'default')

    app.config.from_object(config[config_name])
    app.config.from_pyfile('config.cfg', silent=True)

    if app.config.get('SQLALCHEMY_DATABASE_URI', None) is None:
        app.logger.error(
            "SQLALCHEMY_DATABASE_URI is not set."
            "Didn't you forget to set it in "
            "DATABASE_URL environmental variable?")
        sys.exit(4)  # Return 4 to exit gunicorn

    if app.config.get('SECRET_KEY', None) is None:
        app.logger.error(
            "SECRET_KEY is not set."
            "Didn't you forget to set it in "
            "SECRET_KEY environmental variable?")
        sys.exit(4)  # Return 4 to exit gunicorn

    db.init_app(app)
    swag.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(api.bp)

    app.before_first_request(init_and_generate)

    return app


def init_and_generate():
    """
        Intialize and generate DB if needed,
        depends on DB_GEN_POLICY and DB_FORCE_INIT.

        application context is required.

        * DB_GEN_POLICY=[always|first_time|never]
          * always: Generates initial data every time.
                    (existing User, Classroom, Lottery, Error is deleted)
          * first_time: When initial data is not generated yes, generates.
          * never: Never generates initial data (for deployments)

        * DB_FORCE_INIT=[true|false]
          * true: Deletes all tables and re-creates
          * false: If there is no tables, creates them

        Args:
        Return:
    """
    policy = current_app.config['DB_GEN_POLICY']
    force_init = current_app.config['DB_FORCE_INIT']
    is_empty = len(sqlalchemy.inspect(db.engine).get_table_names()) == 0
    if force_init and not is_empty:
        current_app.logger.warning('Dropping all tables because '
                                   'DB_FORCE_INIT == true')
        db.drop_all()
    if force_init or is_empty:
        current_app.logger.warning('Creating all tables')
        db.create_all()
    if policy == 'always' or \
            (policy == 'first_time' and len(User.query.all()) == 0):
        current_app.logger.warning(
            'Generating Initial Data for Database '
            f'(DB_GEN_POLICY: {policy})')
        generate()
    elif policy != 'never' and policy != 'first_time':
        current_app.logger.warning(
            f'Unknown DB_GEN_POLICY: {policy}. Treated as \'never\'.')


def initdb(app, db):
    from api.models import db
    db.create_all()


def generate():
    """generate DB contents
        1. generate classrooms
        2. generate lotteries
        3. generate users

        Args:
            no-args needed
        Return:
            no-return given
    """
    from .models import Lottery, Classroom, User, Error, db
    total_index = 4

    Classroom.query.delete()
    Lottery.query.delete()
    cl_list_path = current_app.config['CLASSROOM_TABLE_FILE']
    classroom_list = load_id_json_file(cl_list_path)
    for class_data in classroom_list:
        # add classroom
        title_enc = base64.b64encode(class_data['title'].encode('utf-8'))
        room = Classroom(grade=class_data['grade'],
                         index=class_data['index'],
                         title=title_enc.decode('utf-8'))
        db.session.add(room)

        # add lotteries
        # `room` has no id yet. so, get new_classroom from DB
        new_room = Classroom.query.filter_by(grade=class_data['grade'],
                                             index=class_data['index']).first()
        for perf_index in range(total_index):
            lottery = Lottery(classroom_id=new_room.id,
                              index=perf_index, previous_on=None)
            db.session.add(lottery)

    User.query.delete()
    json_path = current_app.config['ID_LIST_FILE']
    id_list = load_id_json_file(json_path)
    for ids in id_list:
        user = User(secret_id=ids['secret_id'],
                    public_id=decode_public_id(ids['public_id']),
                    authority=ids['authority'],
                    kind=ids['kind'])
        db.session.add(user)

    db.session.commit()

    Error.query.delete()
    json_path = current_app.config['ERROR_TABLE_FILE']
    with open(json_path, 'r') as f:
        error_list = json.load(f)
    for (code, desc) in error_list.items():
        error = Error(code=int(code, 10),
                      message=desc['message'], http_code=desc['status'])
        db.session.add(error)

    db.session.commit()

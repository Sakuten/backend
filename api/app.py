from flask import Flask
from flask_cors import CORS
from .routes import auth, api
from .models import db


def create_app(config=None):
    """
        create Flask app and initialize DB.
        Args:
            config (): # more info needed
    """
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
    return app

from flask import Flask
from .routes import bp
from .models import db
from .oauth2 import config_oauth


def create_app(config=None):
    app = Flask(__name__)
    # load app sepcified configuration
    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)

    db.init_app(app)
    config_oauth(app)
    app.register_blueprint(bp, url_prefix='')
    return app

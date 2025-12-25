"""
                            *************************************

                                    creates the app once

                            *************************************
"""
from flask import Flask
from config import Config


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    from .models import db
    db.init_app(app)

    with app.app_context():
        db.create_all()

    from .routes import main
    app.register_blueprint(main)

    return app


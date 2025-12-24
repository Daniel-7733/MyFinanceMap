"""
                            *************************************

                                    creates the app once

                            *************************************
"""
from flask import Flask


def create_app() -> Flask:
    app: Flask = Flask(__name__)

    app.config["SECRET_KEY"] = "dev-secret-key-change-later"

    from .routes import main
    app.register_blueprint(main)

    return app

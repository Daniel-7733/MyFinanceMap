"""
                            *************************************

                                    creates the app once

                            *************************************
"""
from __future__ import annotations

import os
from flask import Flask
from config import DevConfig, ProdConfig
from .models import db


def create_app() -> Flask:
    """
    This function creates the app instance
    :return: returns the app instance
    :rtype: flask.Flask
    """
    app: Flask = Flask(__name__, instance_relative_config=True)

    # Choose environment: DEV or PROD
    env: str = os.getenv("FLASK_ENV", "dev").lower()
    config_obj: ProdConfig | DevConfig = ProdConfig() if env == "prod" else DevConfig()

    app.config.from_object(config_obj)
    if env == "prod":
        app.logger.info("MyFinanceMap started with ProdConfig")
    else:
        app.logger.info("MyFinanceMap started with DevConfig")

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main, url_prefix="/")

    return app



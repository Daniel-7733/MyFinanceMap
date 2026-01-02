"""
                            *************************************

                                    creates the app once
                                    More precise:
                                        1. creates the Flask app (create_app)
                                        2. loads config
                                        3. initializes extensions (SQLAlchemy)
                                        4. registers blueprints

                            *************************************
"""
from __future__ import annotations

from os import getenv, makedirs
from pathlib import Path
from flask import Flask
from config import DevConfig, ProdConfig
from .models import db


def create_app() -> Flask:
    app: Flask = Flask(__name__, instance_relative_config=True)
    makedirs(app.instance_path, exist_ok=True)

    env: str = getenv("FLASK_ENV", "dev").lower()
    config_obj: ProdConfig | DevConfig = ProdConfig() if env == "prod" else DevConfig()
    app.config.from_object(config_obj)

    # ✅ Bulletproof SQLite path (Windows-safe)
    db_path: Path = Path(app.instance_path) / "myfinancemap.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path.as_posix()}"

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from .routes import main
    app.register_blueprint(main, url_prefix="/")

    return app




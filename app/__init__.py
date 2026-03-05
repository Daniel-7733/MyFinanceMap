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
from flask_login import LoginManager
from flask_migrate import Migrate

from config import DevConfig, ProdConfig
from .models import db, User


migrate = Migrate()
login_manager = LoginManager()


def create_app() -> Flask:
    """
    This function creates the app instance.
    :return: Flask app
    """
    app: Flask = Flask(__name__, instance_relative_config=True)
    makedirs(app.instance_path, exist_ok=True)

    env: str = getenv("FLASK_ENV", "dev").lower()
    config_obj: ProdConfig | DevConfig = ProdConfig() if env == "prod" else DevConfig()
    app.config.from_object(config_obj)

    # ✅ Bulletproof SQLite path (Windows-safe)
    db_path: Path = Path(app.instance_path) / "myfinancemap.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path.as_posix()}"

    db.init_app(app)
    migrate.init_app(app, db)

    # ✅ Flask-Login init
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "error"

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    # ❗ If you're using migrations, DO NOT keep create_all long-term
    with app.app_context():
        db.create_all()

    from .routes import main
    app.register_blueprint(main, url_prefix="/")

    from .auth_routes import auth
    app.register_blueprint(auth, url_prefix="/auth")

    # ------ For debug ------ #
    # print("SECRET_KEY loaded:", bool(app.config.get("SECRET_KEY")))
    # print("SECRET_KEY preview:", str(app.config.get("SECRET_KEY"))[:8])
    # ------ For debug ------ #

    return app

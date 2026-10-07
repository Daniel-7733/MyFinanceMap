from flask import Flask

from app.models import db


def test_database_fixture(app: Flask) -> None:
    with app.app_context():
        assert db.engine.url.database == ":memory:"
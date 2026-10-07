"""
        shared test infrastructure

---------------- plan ----------------

Create test Flask app
        ↓
Configure temporary test database
        ↓
Create tables
        ↓
Provide test fixtures
        ↓
Run test
        ↓
Clean everything up

---------------- architecture ----------------

                 conftest.py
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
    temporary DB            real User
          │
          └──────────┬──────────┘
                     ▼
              test_account.py
                     │
                     ▼
              real Account model
"""
import pytest
from flask import Flask

from app import create_app
from app.models import User, db
from config import TestConfig


@pytest.fixture
def app() -> Flask:
    app = create_app(TestConfig())

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def user(app: Flask) -> User:
    with app.app_context():
        user = User(
            username="test_user",
            email="test@example.com",
            password_hash="test-hash",
            home_currency="TRY",
            location="Test",
        )

        db.session.add(user)
        db.session.commit()

        yield user
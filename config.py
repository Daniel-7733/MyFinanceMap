from os import getenv
from dotenv import load_dotenv

load_dotenv()  # load .env into environment


class Config:
    SECRET_KEY: str = getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI: str = getenv(
        "DATABASE_URL", "sqlite:///myfinancemap.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

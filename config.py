from __future__ import annotations

from os import getenv
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _required(name: str) -> str:
    """Get an environment variable or crash with a clear error."""
    value: str | None = getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@dataclass(frozen=True)
class BaseConfig:
    """Common settings for all environments"""
    DEBUG: bool = False
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False


@dataclass(frozen=True)
class DevConfig(BaseConfig):
    """Common settings for development environments"""
    DEBUG: bool = True
    SECRET_KEY: str = getenv("SECRET_KEY", "dev-only-change-me")  # OK for local dev



@dataclass(frozen=True)
class ProdConfig(BaseConfig):
    """Common settings for production environments"""
    DEBUG: bool = False
    SECRET_KEY: str = _required("SECRET_KEY")          # must exist in production

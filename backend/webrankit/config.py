from __future__ import annotations

"""
Application configuration helpers.

The defaults favour local development while allowing overrides through
environment variables so deployments do not have to patch code.
"""

import os
from pathlib import Path

# Repository root (…/pwrank)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
# Default SQLite database lives at the project root to keep behaviour stable
# for existing deployments.
DEFAULT_DB_PATH = PROJECT_ROOT / "db"


class Config:
    """Base configuration shared by all environments."""

    JWT_SECRET_KEY = os.getenv("PWRANK_JWT_SECRET", "change-me")

    # Peewee understands database URLs through playhouse.db_url.connect.
    DATABASE_URL = os.getenv(
        "PWRANK_DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"
    )

    JSON_SORT_KEYS = False


class TestConfig(Config):
    """Configuration shortcuts for unit tests."""

    TESTING = True
    DATABASE_URL = os.getenv("PWRANK_TEST_DATABASE_URL", "sqlite:///:memory:")


__all__ = ["Config", "TestConfig", "DEFAULT_DB_PATH", "PROJECT_ROOT"]

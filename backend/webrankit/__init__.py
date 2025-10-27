from __future__ import annotations

from flask import Flask

from .app import create_app
from .database import db_proxy


def reset_db(app: Flask | None = None) -> None:
    """Utility to recreate all tables – handy for local development."""
    from .model import Comparison, Item, Ranking, User

    app = app or create_app()
    database = db_proxy.obj
    with app.app_context():
        database.drop_tables([Comparison, Item, Ranking, User], safe=True)
        database.create_tables([Comparison, Item, Ranking, User], safe=True)


__all__ = ["create_app", "reset_db"]

from __future__ import annotations

"""
Database bootstrap helpers built around Peewee's DatabaseProxy.

We connect on demand for each request so connection state stays healthy in
long-lived processes (Gunicorn, poetry run, etc.).
"""

from typing import Any, Dict

from flask import Flask
from peewee import Database, DatabaseProxy
from playhouse.db_url import connect

db_proxy: DatabaseProxy = DatabaseProxy()


def init_app(app: Flask) -> Database:
    """Initialise the Peewee database for the given Flask app."""
    database_url = app.config["DATABASE_URL"]
    database = connect(database_url)
    db_proxy.initialize(database)

    @app.before_request
    def _open_connection() -> None:
        if database.is_closed():
            database.connect(reuse_if_open=True)

    @app.teardown_request
    def _close_connection(exc: BaseException | None) -> None:
        if not database.is_closed():
            database.close()

    @app.shell_context_processor
    def _shell_context() -> Dict[str, Any]:
        return {"db": database}

    return database


__all__ = ["db_proxy", "init_app"]

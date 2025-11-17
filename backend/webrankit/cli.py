from __future__ import annotations

import click
from flask.cli import FlaskGroup

from .app import create_app


def _create_app() -> object:
    return create_app()


@click.group(cls=FlaskGroup, create_app=_create_app)
def cli() -> None:
    """Management CLI for the pwRank backend."""


@cli.command("run")
@click.option("--host", default="127.0.0.1", help="Bind interface.")
@click.option("--port", default=5000, type=int, help="Port to listen on.")
@click.option("--debug/--no-debug", default=False, help="Enable Flask debug mode.")
def runserver(host: str, port: int, debug: bool) -> None:
    """Start the development server."""
    app = create_app({"DEBUG": debug})
    app.run(host=host, port=port, debug=debug)


@cli.command("init-db")
def init_db() -> None:
    """Initialize the database schema."""
    from .database import db_proxy
    from .model import Comparison, Item, Ranking, User

    click.echo("Creating database tables...")
    db_proxy.create_tables([User, Ranking, Item, Comparison])
    click.echo("Database tables created successfully!")


def main() -> None:
    cli(auto_envvar_prefix="PWRANK")


if __name__ == "__main__":
    main()

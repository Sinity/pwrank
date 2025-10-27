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
@click.option("--debug/--no-debug", default=True, help="Enable Flask debug mode.")
def runserver(host: str, port: int, debug: bool) -> None:
    """Start the development server."""
    app = create_app({"DEBUG": debug})
    app.run(host=host, port=port, debug=debug)


def main() -> None:
    cli(auto_envvar_prefix="PWRANK")


if __name__ == "__main__":
    main()

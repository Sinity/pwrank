from __future__ import annotations

from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from .config import Config
from .database import init_app as init_database
from .extensions import jwt
from .resource import register_resources


def create_app(config: dict | None = None) -> Flask:
    """Application factory used by Flask's CLI and tests."""
    app = Flask(__name__)
    app.config.from_object(Config)
    if config:
        app.config.update(config)

    CORS(app)
    jwt.init_app(app)
    init_database(app)

    api = Api(app)
    register_resources(api)

    return app


def main() -> None:
    """Convenience entry point for `python -m webrankit.app`."""
    app = create_app()
    app.run(debug=app.config.get("DEBUG", False))


if __name__ == "__main__":
    main()

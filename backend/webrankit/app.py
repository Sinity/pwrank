from __future__ import annotations

import logging

from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from .config import Config
from .database import init_app as init_database
from .extensions import jwt
from .logging_config import configure_logging
from .resource import register_resources

logger = logging.getLogger(__name__)


def create_app(config: dict | None = None) -> Flask:
    """Application factory used by Flask's CLI and tests."""
    # Configure logging first
    log_level = "DEBUG" if config and config.get("DEBUG") else "INFO"
    configure_logging(log_level)

    logger.info("Creating Flask application...")

    app = Flask(__name__)
    app.config.from_object(Config)
    if config:
        app.config.update(config)

    CORS(app)
    jwt.init_app(app)
    init_database(app)

    api = Api(app)
    register_resources(api)

    logger.info("Flask application created successfully")

    return app


def main() -> None:
    """Convenience entry point for `python -m webrankit.app`."""
    app = create_app()
    app.run(debug=app.config.get("DEBUG", False))


if __name__ == "__main__":
    main()

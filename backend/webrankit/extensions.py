from __future__ import annotations

"""Centralised extension instances."""

from flask_jwt_extended import JWTManager

jwt = JWTManager()

__all__ = ["jwt"]

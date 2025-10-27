from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Dict
from uuid import UUID

from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    jwt_required,
)
from flask_restful import Resource

from ..extensions import jwt
from ..model import User


@jwt.user_identity_loader
def user_identity_lookup(user: User) -> str:
    return str(user.id)


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header: Dict[str, Any], jwt_data: Dict[str, Any]) -> User | None:
    user_id_from_token = jwt_data["sub"]
    return User.get_or_none(id=UUID(user_id_from_token))


def admin_required(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    @jwt_required()
    def wrapper(*args: Any, **kwargs: Any):
        if not current_user.is_admin():
            return {"message": "Access denied, admin only"}, 403
        return func(*args, **kwargs)

    return wrapper


class AuthResource(Resource):
    @jwt_required(refresh=True)
    def get(self):
        token = create_access_token(identity=current_user)
        return jsonify(access_token=token)

    def post(self):
        payload = request.get_json(silent=True) or {}
        email = (payload.get("email") or "").strip()
        password = payload.get("password") or ""
        if not email or not password:
            return {"message": "Email and password are required."}, 400

        user = User.get_or_none(email=email)
        if user is None or not user.verify_password(password):
            return {"message": "Authentication failed."}, 401

        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)
        identity = {"email": user.email, "id": str(user.id)}
        return jsonify(identity=identity, access_token=access_token, refresh_token=refresh_token)


__all__ = ["AuthResource", "admin_required"]

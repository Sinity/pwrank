from __future__ import annotations

from typing import Any, Dict, List

from flask import jsonify, request
from flask_restful import Resource

from ..model import User
from .auth import admin_required


def _serialize_user(user: User) -> Dict[str, Any]:
    return {"id": str(user.id), "email": user.email}


class UserResource(Resource):
    @admin_required
    def get(self, uid: str):
        user = User.get_or_none(User.id == uid)
        if user is None:
            return {"message": f"User `{uid}` not found"}, 404
        return jsonify(user=_serialize_user(user))

    @admin_required
    def delete(self, uid: str):
        deleted_rows = User.delete().where(User.id == uid).execute()
        return jsonify(message=f"Deleted {deleted_rows} user(s).")

    @admin_required
    def put(self, uid: str):
        user = User.get_or_none(User.id == uid)
        if user is None:
            return {"message": f"User `{uid}` not found"}, 404

        payload = request.get_json(silent=True) or {}
        email = payload.get("email")
        password = payload.get("password")

        if email:
            user.email = email
        if password:
            user.set_password_hash(password)

        user.save()
        return jsonify(user=_serialize_user(user))


class UserCollectionResource(Resource):
    def post(self):
        payload = request.get_json(silent=True) or {}
        email = (payload.get("email") or "").strip()
        password = payload.get("password")
        if not email or not password:
            return {"message": "Email and password are required."}, 400

        if User.get_or_none(User.email == email):
            return {"message": f"User `{email}` already exists."}, 409

        user = User.create(email=email)
        user.set_password_hash(password)
        user.save()
        return jsonify(message=f"User {user.email} created.", user=_serialize_user(user))

    @admin_required
    def get(self):
        users = [_serialize_user(user) for user in User.select()]
        return jsonify(users=users)

    @admin_required
    def delete(self):
        deleted_rows = User.delete().execute()
        return jsonify(message=f"Deleted {deleted_rows} user(s).")


__all__ = ["UserResource", "UserCollectionResource"]

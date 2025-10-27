from __future__ import annotations

import os
from typing import Final

from passlib.hash import pbkdf2_sha256
from peewee import CharField

from .base import UUIDModel

ADMIN_EMAIL: Final[str | None] = os.getenv("PWRANK_ADMIN_EMAIL")


class User(UUIDModel):
    email = CharField(default="", unique=True)
    password = CharField(default="")

    def is_admin(self) -> bool:
        if ADMIN_EMAIL:
            return self.email.lower() == ADMIN_EMAIL.lower()
        return False

    def set_password_hash(self, password_plaintext: str) -> None:
        self.password = pbkdf2_sha256.hash(password_plaintext)

    def verify_password(self, password_candidate: str) -> bool:
        try:
            return pbkdf2_sha256.verify(password_candidate, self.password)
        except ValueError:
            return False


__all__ = ["User", "ADMIN_EMAIL"]

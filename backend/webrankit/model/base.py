from __future__ import annotations

import uuid

from peewee import BinaryUUIDField, Model

from ..database import db_proxy


class BaseModel(Model):
    class Meta:
        database = db_proxy


class UUIDModel(BaseModel):
    id = BinaryUUIDField(primary_key=True, default=uuid.uuid4)


__all__ = ["BaseModel", "UUIDModel"]

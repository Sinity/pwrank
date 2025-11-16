from __future__ import annotations

from flask_restful import Api

from .auth import AuthResource
from .compare import CompareResource
from .item import ItemCollectionResource, ItemResource
from .ranking import RankingCollectionResource, RankingResource
from .statistics import RankingStatisticsResource
from .user import UserCollectionResource, UserResource


def register_resources(api: Api) -> None:
    api.add_resource(AuthResource, "/auth")
    api.add_resource(UserResource, "/auth/user/<uuid:uid>")
    api.add_resource(UserCollectionResource, "/auth/user")
    api.add_resource(RankingResource, "/ranking/<uuid:uid>")
    api.add_resource(RankingCollectionResource, "/ranking")
    api.add_resource(RankingStatisticsResource, "/ranking/<uuid:uid>/statistics")
    api.add_resource(ItemCollectionResource, "/ranking/<uuid:ranking_uid>/items")
    api.add_resource(ItemResource, "/item/<uuid:uid>")
    api.add_resource(CompareResource, "/compare/<uuid:ranking_uid>")


__all__ = [
    "AuthResource",
    "UserResource",
    "UserCollectionResource",
    "RankingResource",
    "RankingCollectionResource",
    "RankingStatisticsResource",
    "ItemResource",
    "ItemCollectionResource",
    "CompareResource",
    "register_resources",
]

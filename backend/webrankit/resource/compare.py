from __future__ import annotations

from typing import Any, Dict
from uuid import UUID

from flask import jsonify, request
from flask_jwt_extended import current_user, jwt_required
from flask_restful import Resource

from ..model import Comparison, Item, Ranking


class CompareResource(Resource):
    @jwt_required()
    def get(self, ranking_uid: str):
        ranking = Ranking.get_or_none(Ranking.id == ranking_uid)
        if ranking is None:
            return {"message": f"Ranking `{ranking_uid}` not found."}, 404
        if ranking.user.id != current_user.id:
            return {"message": "Ranking belongs to another user."}, 403

        model = ranking.get_pairwise_model()
        if not getattr(model, "coefficients", None):
            return {"message": "Not enough comparisons to suggest a next item."}, 409

        item_ids = model.next_comparison()
        item1 = Item.get_or_none(Item.id == UUID(item_ids[0]))
        item2 = Item.get_or_none(Item.id == UUID(item_ids[1]))
        if item1 is None or item2 is None:
            return {"message": "Comparison items could not be found."}, 404

        comparison = [
            {"id": str(item1.id), "label": item1.label, "img_url": item1.img_url},
            {"id": str(item2.id), "label": item2.label, "img_url": item2.img_url},
        ]
        return jsonify(comparison=comparison)

    @jwt_required()
    def post(self, ranking_uid: str):
        ranking = Ranking.get_or_none(Ranking.id == ranking_uid)
        if ranking is None:
            return {"message": f"Ranking `{ranking_uid}` not found"}, 404
        if ranking.user.id != current_user.id:
            return {"message": "Ranking belongs to another user."}, 403

        payload = request.get_json(silent=True) or {}
        winitem = payload.get("winitem")
        loseitem = payload.get("loseitem")
        if not winitem or not loseitem:
            return {"message": "Both winitem and loseitem are required."}, 400

        item1 = Item.get_or_none(Item.id == UUID(winitem))
        item2 = Item.get_or_none(Item.id == UUID(loseitem))
        if item1 is None or item2 is None:
            return {"message": "One or more comparison items were not found."}, 404
        if item1.id == item2.id:
            return {"message": "Cannot compare an item against itself."}, 400
        if item1.ranking.id != ranking.id or item2.ranking.id != ranking.id:
            return {"message": "Items must belong to the specified ranking."}, 400

        comp = Comparison.compare(item1, item2, str(item1.id))
        model = ranking.get_pairwise_model()
        return jsonify(
            comparison_count=ranking.comparisons.count(),
            comparison={
                "item1": str(comp.item1.id),
                "item2": str(comp.item2.id),
                "win1_count": comp.win1_count,
                "win2_count": comp.win2_count,
                "draw_count": comp.draw_count,
            },
            coefficients=str(getattr(model, "coefficients", "")),
        )


__all__ = ["CompareResource"]

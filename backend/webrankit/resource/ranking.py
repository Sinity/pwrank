from __future__ import annotations

import math
from typing import Any, Dict

from flask import jsonify, request
from flask_jwt_extended import current_user, jwt_required
from flask_restful import Resource

from ..model import Comparison, Item, Ranking


def _serialize_ranking_summary(ranking: Ranking) -> Dict[str, Any]:
    return {
        "id": str(ranking.id),
        "name": ranking.name,
        "datasource": ranking.datasource,
        "item_count": ranking.items.count(),
        "comp_count": ranking.comparisons.count(),
    }


class RankingResource(Resource):
    @jwt_required()
    def get(self, uid: str):
        ranking = Ranking.get_or_none(Ranking.id == uid)
        if ranking is None:
            return {"message": f"Ranking `{uid}` not found."}, 404
        if ranking.user.id != current_user.id:
            return {"message": "Ranking belongs to another user."}, 403

        ranking_json = _serialize_ranking_summary(ranking)
        ranking_json["items"] = []

        model = ranking.get_pairwise_model()

        # Count comparisons per item
        item_comparison_counts = {}
        for comp in ranking.comparisons:
            item1_id = str(comp.item1.id)
            item2_id = str(comp.item2.id)
            total_comps = comp.win1_count + comp.win2_count + comp.draw_count
            item_comparison_counts[item1_id] = item_comparison_counts.get(item1_id, 0) + total_comps
            item_comparison_counts[item2_id] = item_comparison_counts.get(item2_id, 0) + total_comps

        for item in ranking.items:
            entry = {
                "id": str(item.id),
                "label": item.label,
                "img_url": item.img_url,
                "init_rating": item.init_rating,
                "curr_rating": None,
                "stderr": 0,
                "ability": None,
                "comparisons_count": 0,
            }
            if getattr(model, "coefficients", None):
                coeff = model.coeff_by_id(str(item.id))
                if coeff:
                    ability, stderr, _ = coeff
                    stderr_value = float(stderr)
                    if math.isnan(stderr_value):
                        stderr_value = 0.0
                    idx = model.coefficients.index(coeff)
                    total = max(len(model.coefficients), 1)
                    # Use percentile rank (0-10 scale), ensuring lowest item gets > 0
                    rating = ((idx + 1) / total) * 10
                    entry["curr_rating"] = round(rating, 2)
                    entry["stderr"] = round(stderr_value, 2)
                    entry["ability"] = round(float(ability), 3)

            entry["comparisons_count"] = item_comparison_counts.get(str(item.id), 0)
            ranking_json["items"].append(entry)

        return jsonify(ranking=ranking_json)

    @jwt_required()
    def post(self, uid: str):
        ranking = Ranking.get_or_none(Ranking.id == uid)
        if ranking is None:
            return {"message": f"Ranking `{uid}` not found."}, 404

        payload = request.get_json(silent=True) or {}
        datasource = ranking.datasource

        if datasource == "anilist":
            username = payload.get("anilist_username")
            statuses = payload.get("anilist_statuses") or []
            if not username:
                return {"message": "anilist_username is required."}, 400
            ranking.add_items_from_anilist(username, statuses)
        elif datasource == "steam":
            steam_id = payload.get("steam_id")
            if not steam_id:
                return {"message": "steam_id is required."}, 400
            ranking.add_items_from_steam(steam_id)
        else:
            return {"message": f"Unknown datasource `{datasource}`"}, 400

        return jsonify(message=f"Ranking now has {ranking.items.count()} items.")

    @jwt_required()
    def delete(self, uid: str):
        ranking = Ranking.get_or_none(Ranking.id == uid)
        if ranking is None:
            return {"message": f"Ranking `{uid}` not found."}, 404
        if ranking.user.id != current_user.id:
            return {"message": "Ranking belongs to another user."}, 403
        deleted_rows = ranking.delete_instance(recursive=True)
        return jsonify(message=f"Deleted {deleted_rows} ranking(s).")

    @jwt_required()
    def put(self, uid: str):
        ranking = Ranking.get_or_none(Ranking.id == uid)
        if ranking is None:
            return {"message": f"Ranking `{uid}` not found."}, 404
        if ranking.user.id != current_user.id:
            return {"message": "Ranking belongs to another user."}, 403

        payload = request.get_json(silent=True) or {}
        name = payload.get("name")
        if name:
            ranking.name = name
            ranking.save()
        return jsonify(message=f"Ranking {ranking.id} updated.", ranking=_serialize_ranking_summary(ranking))


class RankingCollectionResource(Resource):
    @jwt_required()
    def post(self):
        payload = request.get_json(silent=True) or {}
        name = (payload.get("name") or "").strip()
        datasource = (payload.get("source") or "").strip()
        if not name:
            return {"message": "Ranking name is required."}, 400
        if not datasource:
            return {"message": "Datasource is required."}, 400

        # Check for duplicate name per user, not globally
        if Ranking.get_or_none(
            (Ranking.name == name) & (Ranking.user == current_user.id)
        ):
            return {"message": "You already have a ranking with this name."}, 409

        ranking = Ranking.create(user=current_user, name=name, datasource=datasource)
        return jsonify(message=f"Ranking {ranking.name} created.", ranking=_serialize_ranking_summary(ranking))

    @jwt_required()
    def get(self):
        user_rankings = Ranking.select().where(Ranking.user == current_user.id)
        ranking_dicts = [_serialize_ranking_summary(ranking) for ranking in user_rankings]
        return jsonify(rankings=ranking_dicts)


__all__ = ["RankingResource", "RankingCollectionResource"]

"""Statistics and analytics endpoints."""

from __future__ import annotations

import logging
from typing import Any, Dict

from flask import jsonify
from flask_jwt_extended import current_user, jwt_required
from flask_restful import Resource

from ..model import Comparison, Item, Ranking

logger = logging.getLogger(__name__)


class RankingStatisticsResource(Resource):
    """Detailed statistics for a ranking."""

    @jwt_required()
    def get(self, uid: str) -> tuple[Dict[str, Any], int]:
        ranking = Ranking.get_or_none(Ranking.id == uid)
        if ranking is None:
            return {"message": f"Ranking `{uid}` not found"}, 404
        if ranking.user.id != current_user.id:
            return {"message": "Ranking belongs to another user."}, 403

        item_count = ranking.items.count()
        comp_count = ranking.comparisons.count()

        # Calculate possible comparisons
        max_comparisons = (item_count * (item_count - 1)) // 2 if item_count > 1 else 0
        completion_pct = (comp_count / max_comparisons * 100) if max_comparisons > 0 else 0

        # Get comparison distribution
        comparison_counts: Dict[int, int] = {}
        for item in ranking.items:
            item_comps = item.comparisons_i1.count() + item.comparisons_i2.count()
            comparison_counts[item_comps] = comparison_counts.get(item_comps, 0) + 1

        # Get recent comparisons
        recent = list(ranking.comparisons.order_by(Comparison.id.desc()).limit(10))
        recent_comparisons = [
            {
                "item1": comp.item1.label,
                "item2": comp.item2.label,
                "win1_count": comp.win1_count,
                "win2_count": comp.win2_count,
                "draw_count": comp.draw_count,
            }
            for comp in recent
        ]

        # Calculate statistics
        model = ranking.get_pairwise_model()
        uncertainties = []
        if model.coefficients:
            uncertainties = [float(stderr) for _, stderr, _ in model.coefficients]

        avg_uncertainty = sum(uncertainties) / len(uncertainties) if uncertainties else 0
        max_uncertainty = max(uncertainties) if uncertainties else 0
        min_uncertainty = min(uncertainties) if uncertainties else 0

        stats = {
            "ranking_id": str(ranking.id),
            "ranking_name": ranking.name,
            "item_count": item_count,
            "comparison_count": comp_count,
            "max_possible_comparisons": max_comparisons,
            "completion_percentage": round(completion_pct, 2),
            "comparison_distribution": comparison_counts,
            "recent_comparisons": recent_comparisons,
            "uncertainty_stats": {
                "average": round(avg_uncertainty, 3),
                "max": round(max_uncertainty, 3),
                "min": round(min_uncertainty, 3),
            },
            "needs_more_comparisons": max_uncertainty > 1.5 if max_uncertainty else False,
        }

        logger.info(
            f"Generated statistics for ranking {uid}: "
            f"{item_count} items, {comp_count} comparisons, {completion_pct:.1f}% complete"
        )

        return jsonify(statistics=stats)


__all__ = ["RankingStatisticsResource"]

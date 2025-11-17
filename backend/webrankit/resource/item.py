"""Item management endpoints."""

from __future__ import annotations

import logging
from typing import Any, Dict

from flask import jsonify, request
from flask_jwt_extended import current_user, jwt_required
from flask_restful import Resource

from ..model import Comparison, Item, Ranking

logger = logging.getLogger(__name__)


class ItemCollectionResource(Resource):
    """Operations on items within a ranking."""

    @jwt_required()
    def get(self, ranking_uid: str) -> tuple[Dict[str, Any], int]:
        """List all items in a ranking."""
        ranking = Ranking.get_or_none(Ranking.id == ranking_uid)
        if ranking is None:
            return {"message": f"Ranking `{ranking_uid}` not found"}, 404
        if ranking.user.id != current_user.id:
            return {"message": "Ranking belongs to another user."}, 403

        items = [
            {
                "id": str(item.id),
                "label": item.label,
                "img_url": item.img_url,
                "init_rating": item.init_rating,
            }
            for item in ranking.items
        ]

        return jsonify(items=items)

    @jwt_required()
    def post(self, ranking_uid: str) -> tuple[Dict[str, Any], int]:
        """Create a new item in a ranking."""
        ranking = Ranking.get_or_none(Ranking.id == ranking_uid)
        if ranking is None:
            return {"message": f"Ranking `{ranking_uid}` not found"}, 404
        if ranking.user.id != current_user.id:
            return {"message": "Ranking belongs to another user."}, 403

        payload = request.get_json(silent=True) or {}
        label = (payload.get("label") or "").strip()
        img_url = (payload.get("img_url") or "").strip()
        init_rating = payload.get("init_rating", 5)

        # Validation
        if not label:
            return {"message": "Item label is required."}, 400
        if len(label) > 200:
            return {"message": "Item label must be 200 characters or less."}, 400
        if len(img_url) > 500:
            return {"message": "Image URL must be 500 characters or less."}, 400

        # Check for duplicate label in same ranking
        existing_item = Item.get_or_none(
            (Item.ranking == ranking) & (Item.label == label)
        )
        if existing_item is not None:
            return {
                "message": f"An item with label '{label}' already exists in this ranking."
            }, 409

        # Validate init_rating
        try:
            init_rating = int(init_rating)
            if init_rating < 0 or init_rating > 10:
                return {"message": "Initial rating must be between 0 and 10."}, 400
        except (ValueError, TypeError):
            return {"message": "Initial rating must be a valid integer."}, 400

        # Create item
        item = Item.create(
            ranking=ranking,
            label=label,
            img_url=img_url,
            init_rating=init_rating,
        )
        # Seed comparisons to ensure new items enter the model
        ranking.compare_by_init_ratings()

        logger.info(
            f"Created item '{label}' in ranking {ranking_uid} by user {current_user.id}"
        )

        return jsonify(
            item={
                "id": str(item.id),
                "label": item.label,
                "img_url": item.img_url,
                "init_rating": item.init_rating,
            }
        ), 201


class ItemResource(Resource):
    """Operations on a specific item."""

    @jwt_required()
    def get(self, uid: str) -> tuple[Dict[str, Any], int]:
        """Get a specific item."""
        item = Item.get_or_none(Item.id == uid)
        if item is None:
            return {"message": f"Item `{uid}` not found"}, 404
        if item.ranking.user.id != current_user.id:
            return {"message": "Item belongs to another user's ranking."}, 403

        return jsonify(
            item={
                "id": str(item.id),
                "label": item.label,
                "img_url": item.img_url,
                "init_rating": item.init_rating,
                "ranking_id": str(item.ranking.id),
            }
        )

    @jwt_required()
    def put(self, uid: str) -> tuple[Dict[str, Any], int]:
        """Update an item."""
        item = Item.get_or_none(Item.id == uid)
        if item is None:
            return {"message": f"Item `{uid}` not found"}, 404
        if item.ranking.user.id != current_user.id:
            return {"message": "Item belongs to another user's ranking."}, 403

        payload = request.get_json(silent=True) or {}

        # Update label if provided
        if "label" in payload:
            label = (payload.get("label") or "").strip()
            if not label:
                return {"message": "Item label cannot be empty."}, 400
            if len(label) > 200:
                return {"message": "Item label must be 200 characters or less."}, 400

            # Check for duplicate label in same ranking (excluding current item)
            existing_item = Item.get_or_none(
                (Item.ranking == item.ranking)
                & (Item.label == label)
                & (Item.id != item.id)
            )
            if existing_item is not None:
                return {
                    "message": f"An item with label '{label}' already exists in this ranking."
                }, 409

            item.label = label

        # Update img_url if provided
        if "img_url" in payload:
            img_url = (payload.get("img_url") or "").strip()
            if len(img_url) > 500:
                return {"message": "Image URL must be 500 characters or less."}, 400
            item.img_url = img_url

        # Update init_rating if provided
        if "init_rating" in payload:
            try:
                init_rating = int(payload["init_rating"])
                if init_rating < 0 or init_rating > 10:
                    return {"message": "Initial rating must be between 0 and 10."}, 400
                item.init_rating = init_rating
            except (ValueError, TypeError):
                return {"message": "Initial rating must be a valid integer."}, 400

        item.save()

        logger.info(f"Updated item {uid} by user {current_user.id}")

        return jsonify(
            item={
                "id": str(item.id),
                "label": item.label,
                "img_url": item.img_url,
                "init_rating": item.init_rating,
            }
        )

    @jwt_required()
    def delete(self, uid: str) -> tuple[Dict[str, Any], int]:
        """Delete an item."""
        item = Item.get_or_none(Item.id == uid)
        if item is None:
            return {"message": f"Item `{uid}` not found"}, 404
        if item.ranking.user.id != current_user.id:
            return {"message": "Item belongs to another user's ranking."}, 403

        label = item.label
        ranking_id = str(item.ranking.id)

        # Delete all comparisons involving this item
        Comparison.delete().where(
            (Comparison.item1 == item) | (Comparison.item2 == item)
        ).execute()

        # Delete the item
        item.delete_instance()

        logger.info(
            f"Deleted item '{label}' from ranking {ranking_id} by user {current_user.id}"
        )

        return {"message": f"Item '{label}' deleted successfully."}, 200


__all__ = ["ItemResource", "ItemCollectionResource"]

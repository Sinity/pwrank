from __future__ import annotations

from typing import Sequence

from peewee import (
    CharField,
    CompositeKey,
    ForeignKeyField,
    IntegerField,
)

from ..extract import extract_items_from_anilist, extract_items_from_steam
from ..pairwise import PairwiseModel
from .base import BaseModel, UUIDModel
from .user import User


class Ranking(UUIDModel):
    user = ForeignKeyField(User, backref="rankings")
    name = CharField()
    datasource = CharField(default="")

    def compare_by_init_ratings(self) -> None:
        items_by_rating = list(self.items.order_by(Item.init_rating))
        for item1, item2 in zip(items_by_rating, items_by_rating[1:]):
            if not (item1.has_comparisons() and item2.has_comparisons()):
                Comparison.compare_by_init_rating(item1, item2)

    def get_pairwise_model(self) -> PairwiseModel:
        model = PairwiseModel()
        for comp in self.comparisons:
            id1, id2 = str(comp.item1.id), str(comp.item2.id)
            model.draw(id1, id2, comp.draw_count)
            model.win(id1, id2, comp.win1_count)
            model.win(id2, id1, comp.win2_count)
        if self.comparisons.count():
            model.update_model()
        return model

    def add_items_from_anilist(self, username: str, statuses: Sequence[str]) -> None:
        medialist = extract_items_from_anilist(username, statuses)
        if not medialist:
            return
        for media in medialist:
            score = media.get("score") or 0
            title = media["media"]["title"]["userPreferred"]
            img = media["media"]["coverImage"]["extraLarge"]
            existing_item = Item.get_or_none(ranking=self, label=title)
            if existing_item is not None:
                existing_item.init_rating = score
                existing_item.img_url = img
                existing_item.save()
            else:
                Item.create(
                    ranking=self,
                    init_rating=score,
                    label=title,
                    img_url=img,
                )
        self.compare_by_init_ratings()

    def add_items_from_steam(self, steam_id: str) -> None:
        medialist = extract_items_from_steam(steam_id)
        if not medialist:
            return
        total = len(medialist) or 1
        for idx, media in enumerate(medialist):
            score = ((total - idx) / total) * 10
            title = media["label"]
            img = media["img_url"]
            existing_item = Item.get_or_none(ranking=self, label=title)
            if existing_item is not None:
                existing_item.init_rating = score
                existing_item.img_url = img
                existing_item.save()
            else:
                Item.create(
                    ranking=self,
                    init_rating=score,
                    label=title,
                    img_url=img,
                )
        self.compare_by_init_ratings()


class Item(UUIDModel):
    ranking = ForeignKeyField(Ranking, backref="items")
    label = CharField(default="")
    img_url = CharField(default="")
    init_rating = IntegerField(default=0)  # TODO: Change to FloatField in migration

    def has_comparisons(self) -> bool:
        return bool(self.comparisons_i1.count() or self.comparisons_i2.count())


class Comparison(BaseModel):
    class Meta:
        primary_key = CompositeKey("item1", "item2")

    ranking = ForeignKeyField(Ranking, backref="comparisons")
    item1 = ForeignKeyField(Item, backref="comparisons_i1")
    item2 = ForeignKeyField(Item, backref="comparisons_i2")
    win1_count = IntegerField(default=0)
    win2_count = IntegerField(default=0)
    draw_count = IntegerField(default=0)

    @classmethod
    def compare(cls, item1: Item, item2: Item, winner_id: str) -> "Comparison":
        item1, item2 = sorted([item1, item2], key=lambda item: str(item.id))
        comp, _ = cls.get_or_create(item1=item1, item2=item2, ranking=item1.ranking)
        if str(item1.id) == str(winner_id):
            comp.win1_count += 1
        elif str(item2.id) == str(winner_id):
            comp.win2_count += 1
        else:
            comp.draw_count += 1
        comp.save()
        return comp

    @classmethod
    def compare_by_init_rating(cls, item1: Item, item2: Item) -> "Comparison":
        item1, item2 = sorted([item1, item2], key=lambda item: str(item.id))
        comp, _ = cls.get_or_create(item1=item1, item2=item2, ranking=item1.ranking)
        if item1.init_rating > item2.init_rating:
            comp.win1_count += 1
        elif item1.init_rating < item2.init_rating:
            comp.win2_count += 1
        else:
            comp.draw_count += 1
        comp.save()
        return comp


__all__ = ["Comparison", "Item", "Ranking"]

from peewee import *
from .base import *
from .user import User
from pairwise import PairwiseModel
from extract import *

class Ranking(UUIDModel):
    user = ForeignKeyField(User, backref='rankings')
    name = CharField()
    datasource = CharField(default='')

    # def add_init_items(self, new_items):
    #     for item in new_items:
    #         Item.create(ranking=self, label=item[0], init_rating=item[1])

    def compare_by_init_ratings(self):
        items_by_rating = self.items.order_by(Item.init_rating)
        for item1, item2 in zip(items_by_rating, items_by_rating[1:]):
            Comparison.compare_by_init_rating(item1, item2)

    def get_pairwise_model(self):
        model = PairwiseModel()
        for comp in self.comparisons:
            id1, id2 = str(comp.item1.id), str(comp.item2.id)
            model.draw(id1, id2, comp.draw_count)
            model.win(id1, id2, comp.win1_count)
            model.win(id2, id1, comp.win2_count)
        model.update_model()
        return model

    def add_items_from_anilist(self, username, status):
        medialist = extract_items_from_anilist(username, status)
        if media == {}:
            return
        for media in medialist:
            score = media['score']
            title = media['media']['title']['userPreferred']
            img = media['media']['coverImage']['extraLarge']
            Item.create(ranking=self, init_rating=score, label=title, img_url=img)


class Item(UUIDModel):
    ranking = ForeignKeyField(Ranking, backref='items')
    label = CharField(default='')
    img_url = CharField(default='')
    #description = CharField(default='')
    init_rating = IntegerField(default=0)

class Comparison(BaseModel):
    class Meta:
        primary_key = CompositeKey('item1', 'item2')
    ranking = ForeignKeyField(Ranking, backref='comparisons')
    item1 = ForeignKeyField(Item, backref='comparisons_i1')
    item2 = ForeignKeyField(Item, backref='comparisons_i2')
    win1_count = IntegerField(default=0)
    win2_count = IntegerField(default=0)
    draw_count = IntegerField(default=0)

    def compare_by_init_rating(item1, item2):
        if str(item1.id) > str(item2.id):
            item1, item2 = item2, item1
        comp, res = Comparison.get_or_create(item1=item1, item2=item2, ranking=item1.ranking)
        if item1.init_rating > item2.init_rating:
            comp.win1_count += 1
        elif item1.init_rating < item2.init_rating:
            comp.win2_count += 1
        else:
            comp.draw_count += 1
        comp.save()
        return comp

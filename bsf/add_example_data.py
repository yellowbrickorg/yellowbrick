from django.contrib.auth.models import User
from .models import Color, Brick, LegoSet, UserCollection, BrickInSetQuantity, BrickInCollectionQuantity, SetInCollectionQuantity

def add_example_data():
    user_collection = UserCollection.objects.create({'userid': 1})
    user_collection.bricks.add(brick1, through_defaults={'quantity': 20})
    user_collection.bricks.add(brick2, through_defaults={'quantity': 10})
    user_collection.sets.add(lego_set, through_defaults={'quantity': 1})
from django.contrib.auth.models import User
from .models import Color, Brick, LegoSet, UserCollection, BrickInSetQuantity, BrickInCollectionQuantity, \
    SetInCollectionQuantity


def add_example_data():
    # Example Color objects
    color0 = Color.objects.create(color_id=0, name='Black', rgb='05131D')
    color4 = Color.objects.create(color_id=4, name='Red', rgb='C91A09')

    # Example Brick objects
    brick1 = Brick.objects.create(brick_id=1, part_num='3024', color=color0,
                                  image_link="https://cdn.rebrickable.com/media/parts/elements/302426.jpg")
    brick2 = Brick.objects.create(brick_id=2, part_num='3020', color=color0,
                                  image_link="https://cdn.rebrickable.com/media/parts/elements/302026.jpg")
    brick3 = Brick.objects.create(brick_id=3, part_num='4070', color=color4,
                                  image_link="https://cdn.rebrickable.com/media/parts/ldraw/4/4070.png")

    # Example LegoSet object
    lego_set1 = LegoSet.objects.create(number='10290-1', name='Pickup Truck',
                                       image_link='https://cdn.rebrickable.com/media/sets/10290-1.jpg',
                                       inventory_id=1)
    lego_set1.bricks.add(brick1, through_defaults={'quantity': 10})
    lego_set1.bricks.add(brick2, through_defaults={'quantity': 5})
    lego_set1.bricks.add(brick3, through_defaults={'quantity': 5})
    lego_set2 = LegoSet.objects.create(number='10312-1', name='Jazz Club',
                                       image_link='https://cdn.rebrickable.com/media/sets/10312-1.jpg',
                                       inventory_id=2)
    lego_set2.bricks.add(brick1, through_defaults={'quantity': 100})
    lego_set2.bricks.add(brick2, through_defaults={'quantity': 20})
    lego_set2.bricks.add(brick3, through_defaults={'quantity': 5})

    # Example UserCollection object
    user = User.objects.create(username='example_user')
    user_collection = UserCollection.objects.create(user=user)
    user_collection.bricks.add(brick1, through_defaults={'quantity': 20})
    user_collection.bricks.add(brick2, through_defaults={'quantity': 10})
    user_collection.sets.add(lego_set1, through_defaults={'quantity': 1})

    # Example BrickInSetQuantity object
    # brick_in_set_quantity = BrickInSetQuantity.objects.create(brick_set=lego_set, brick=brick3, quantity=3)
    #
    # # Example BrickInCollectionQuantity object
    # brick_in_collection_quantity = BrickInCollectionQuantity.objects.create(brick=brick3, collection=user_collection,
    #                                                                         quantity=5)
    #
    # # Example SetInCollectionQuantity object
    # set_in_collection_quantity = SetInCollectionQuantity.objects.create(brick_set=lego_set, collection=user_collection,
    #                                                                     quantity=1)

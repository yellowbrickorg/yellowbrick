from django.contrib.auth.models import User
from .models import Color, Brick, LegoSet, UserCollection, BrickInSetQuantity, BrickInCollectionQuantity, SetInCollectionQuantity

def add_example_data():
    # Example Color objects
    color1 = Color.objects.create(color_id=1, name='Red', rgb='FF0000')
    color2 = Color.objects.create(color_id=2, name='Blue', rgb='0000FF')
    color3 = Color.objects.create(color_id=3, name='Green', rgb='00FF00')

    # Example Brick objects
    brick1 = Brick.objects.create(brick_id=1, part_num='1234', color=color1)
    brick2 = Brick.objects.create(brick_id=2, part_num='5678', color=color2)
    brick3 = Brick.objects.create(brick_id=3, part_num='9101', color=color3)

    # Example LegoSet object
    lego_set = LegoSet.objects.create(number='12345', name='Lego Set 1', imageLink='https://example.com/image.png')
    lego_set.bricks.add(brick1, through_defaults={'quantity': 10})
    lego_set.bricks.add(brick2, through_defaults={'quantity': 5})

    # Example UserCollection object
    user = User.objects.create(username='example_user')
    user_collection = UserCollection.objects.create(userid=user)
    user_collection.bricks.add(brick1, through_defaults={'quantity': 20})
    user_collection.bricks.add(brick2, through_defaults={'quantity': 10})
    user_collection.sets.add(lego_set, through_defaults={'quantity': 1})

    # Example BrickInSetQuantity object
    brick_in_set_quantity = BrickInSetQuantity.objects.create(brickset=lego_set, brick=brick3, quantity=3)

    # Example BrickInCollectionQuantity object
    brick_in_collection_quantity = BrickInCollectionQuantity.objects.create(brick=brick3, collection=user_collection, quantity=5)

    # Example SetInCollectionQuantity object
    set_in_collection_quantity = SetInCollectionQuantity.objects.create(brickset=lego_set, collection=user_collection, quantity=1)

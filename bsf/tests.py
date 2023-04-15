import django.db.utils
from django.contrib.auth.models import User
from django.test import TestCase

from bsf.models import Color, Brick, LegoSet, UserCollection, BrickInSetQuantity, \
    BrickInCollectionQuantity

from . import views


class CollectionFilterTestCase(TestCase):
    def setUp(self):
        Color.objects.create(color_id=0, name='Black', rgb='05131D', is_transparent='f')
        Color.objects.create(color_id=1, name='Blue', rgb='0055BF', is_transparent='f')

        brick1 = Brick.objects.create(brick_id=1, part_num='0001', color_id=0)
        brick2 = Brick.objects.create(brick_id=2, part_num='0002', color_id=1)

        lego_set1 = LegoSet.objects.create(number='11111', name='Lego Set 1',
                                           image_link='https://example.com/image.png',
                                           inventory_id=1)
        lego_set1.bricks.add(brick1, through_defaults={'quantity': 10})
        lego_set1.bricks.add(brick2, through_defaults={'quantity': 5})

        lego_set2 = LegoSet.objects.create(number='22222', name='Lego Set 2',
                                           image_link='https://example.com/image.png',
                                           inventory_id=2)
        lego_set2.bricks.add(brick1, through_defaults={'quantity': 2})
        lego_set2.bricks.add(brick2, through_defaults={'quantity': 5})

        user1 = User.objects.create(username='Janusz')
        user_collection = UserCollection.objects.create(user=user1)
        user_collection.bricks.add(brick1, through_defaults={'quantity': 2})
        user_collection.bricks.add(brick2, through_defaults={'quantity': 5})

        user2 = User.objects.create(username='Mariusz')
        user_collection = UserCollection.objects.create(user=user2)
        user_collection.bricks.add(brick1, through_defaults={'quantity': 1})
        user_collection.bricks.add(brick2, through_defaults={'quantity': 1})

    def test_user_can_have_only_one_collection(self):
        user1 = User.objects.get(username='Janusz')
        print(UserCollection.objects.all())
        self.assertRaises(django.db.utils.IntegrityError, UserCollection.objects.create,
                          user=user1)

    def test_users_bricks_collections(self):
        user1 = User.objects.get(username='Janusz')
        user2 = User.objects.get(username='Mariusz')

        user1_collection = UserCollection.objects.get(user=user1)
        bricks_of_user1 = BrickInCollectionQuantity.objects.filter(
            collection=user1_collection)

        brick1 = Brick.objects.get(brick_id=1)
        brick2 = Brick.objects.get(brick_id=2)

        self.assertEqual(bricks_of_user1.get(brick=brick1).quantity, 2)
        self.assertEqual(bricks_of_user1.get(brick=brick2).quantity, 5)

        user2_collection = UserCollection.objects.get(user=user2)
        bricks_of_user2 = BrickInCollectionQuantity.objects.filter(
            collection=user2_collection)

        self.assertEqual(bricks_of_user2.get(brick=brick1).quantity, 1)
        self.assertEqual(bricks_of_user2.get(brick=brick2).quantity, 1)

    def test_set1_set2_requirements(self):
        brick1 = Brick.objects.get(brick_id=1)
        brick2 = Brick.objects.get(brick_id=2)

        lego_set1 = LegoSet.objects.get(number='11111')
        lego_set2 = LegoSet.objects.get(number='22222')

        bricks_in_set1 = BrickInSetQuantity.objects.filter(brick_set=lego_set1).all()
        bricks_in_set2 = BrickInSetQuantity.objects.filter(brick_set=lego_set2).all()

        self.assertEqual(bricks_in_set1.get(brick=brick1).quantity, 10)
        self.assertEqual(bricks_in_set1.get(brick=brick2).quantity, 5)

        self.assertEqual(bricks_in_set2.get(brick=brick1).quantity, 2)
        self.assertEqual(bricks_in_set2.get(brick=brick2).quantity, 5)

    def test_user1_can_build_set2_but_not_set1(self):
        lego_set2 = LegoSet.objects.get(number='22222')

        user1 = User.objects.get(username='Janusz')

        self.assertEqual(views.get_viable_sets(user1), [lego_set2])

    def test_user2_cant_build_anything(self):
        user2 = User.objects.get(username='Mariusz')

        self.assertEqual(views.get_viable_sets(user2), [])

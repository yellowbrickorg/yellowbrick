import django.db.utils
from bsf.models import User
from django.test import TestCase
from django.db.models import Avg

from bsf.models import (
    Color,
    Brick,
    LegoSet,
    UserCollection,
    BrickInSetQuantity,
    BrickInCollectionQuantity,
    BrickStats,
)

from bsf import views
from bsf.views import (
    get_viable_sets,
    get_avg_likes,
    get_avg_age,
)


class CollectionFilterTestCase(TestCase):
    def setUp(self):
        Color.objects.create(color_id=0, name="Black", rgb="05131D", is_transparent="f")
        Color.objects.create(color_id=1, name="Blue", rgb="0055BF", is_transparent="f")

        self.brick1 = Brick.objects.create(brick_id=1, part_num="0001", color_id=0)
        self.brick2 = Brick.objects.create(brick_id=2, part_num="0002", color_id=1)

        self.lego_set1 = LegoSet.objects.create(
            number="11111",
            name="Lego Set 1",
            image_link="https://example.com/image.png",
            inventory_id=1,
            theme="aa",
            quantity_of_bricks=2,
        )
        self.lego_set1.bricks.add(self.brick1, through_defaults={"quantity": 10})
        self.lego_set1.bricks.add(self.brick2, through_defaults={"quantity": 5})

        self.lego_set2 = LegoSet.objects.create(
            number="22222",
            name="Lego Set 2",
            image_link="https://example.com/image.png",
            inventory_id=2,
            theme="aa",
            quantity_of_bricks=2,
        )
        self.lego_set2.bricks.add(self.brick1, through_defaults={"quantity": 2})
        self.lego_set2.bricks.add(self.brick2, through_defaults={"quantity": 5})

        self.lego_set3 = LegoSet.objects.create(
            number="33333",
            name="Lego Set 3",
            image_link="https://example.com/image.png",
            inventory_id=3,
            theme="aa",
            quantity_of_bricks=2,
        )
        self.lego_set3.bricks.add(self.brick1, through_defaults={"quantity": 4})
        self.lego_set3.bricks.add(self.brick2, through_defaults={"quantity": 10})

        self.user1 = User.objects.create(username="Janusz")
        self.user_collection = UserCollection.objects.create(user=self.user1)
        self.user_collection.bricks.add(self.brick1, through_defaults={"quantity": 2})
        self.user_collection.bricks.add(self.brick2, through_defaults={"quantity": 5})

        self.user2 = User.objects.create(username="Mariusz")
        self.user_collection = UserCollection.objects.create(user=self.user2)
        self.user_collection.bricks.add(self.brick1, through_defaults={"quantity": 1})
        self.user_collection.bricks.add(self.brick2, through_defaults={"quantity": 1})

        self.user3 = User.objects.create(username="Julia")
        self.user_collection = UserCollection.objects.create(user=self.user3)
        self.user_collection.sets.add(self.lego_set2, through_defaults={"quantity": 2})

        self.stat1 = BrickStats.objects.create(
            user=self.user1,
            brick_set=self.lego_set1,
            likes=7,
            min_recommended_age=15,
            build_time=1,
        )
        self.stat2 = BrickStats.objects.create(
            user=self.user2,
            brick_set=self.lego_set1,
            likes=5,
            min_recommended_age=20,
            build_time=2,
        )
        self.stat3 = BrickStats.objects.create(
            user=self.user3,
            brick_set=self.lego_set2,
            likes=10,
            min_recommended_age=8,
            build_time=3,
        )

    def test_user_can_have_only_one_collection(self):
        user1 = User.objects.get(username="Janusz")
        print(UserCollection.objects.all())
        self.assertRaises(
            django.db.utils.IntegrityError, UserCollection.objects.create, user=user1
        )

    def test_users_bricks_collections(self):
        user1 = User.objects.get(username="Janusz")
        user2 = User.objects.get(username="Mariusz")

        user1_collection = UserCollection.objects.get(user=user1)
        bricks_of_user1 = BrickInCollectionQuantity.objects.filter(
            collection=user1_collection
        )

        brick1 = Brick.objects.get(brick_id=1)
        brick2 = Brick.objects.get(brick_id=2)

        self.assertEqual(bricks_of_user1.get(brick=brick1).quantity, 2)
        self.assertEqual(bricks_of_user1.get(brick=brick2).quantity, 5)

        user2_collection = UserCollection.objects.get(user=user2)
        bricks_of_user2 = BrickInCollectionQuantity.objects.filter(
            collection=user2_collection
        )

        self.assertEqual(bricks_of_user2.get(brick=brick1).quantity, 1)
        self.assertEqual(bricks_of_user2.get(brick=brick2).quantity, 1)

    def test_set1_set2_requirements(self):
        brick1 = Brick.objects.get(brick_id=1)
        brick2 = Brick.objects.get(brick_id=2)

        lego_set1 = LegoSet.objects.get(number="11111")
        lego_set2 = LegoSet.objects.get(number="22222")

        bricks_in_set1 = BrickInSetQuantity.objects.filter(brick_set=lego_set1).all()
        bricks_in_set2 = BrickInSetQuantity.objects.filter(brick_set=lego_set2).all()

        self.assertEqual(bricks_in_set1.get(brick=brick1).quantity, 10)
        self.assertEqual(bricks_in_set1.get(brick=brick2).quantity, 5)

        self.assertEqual(bricks_in_set2.get(brick=brick1).quantity, 2)
        self.assertEqual(bricks_in_set2.get(brick=brick2).quantity, 5)

    def test_user1_can_build_set2_but_not_set1(self):
        lego_set2 = LegoSet.objects.get(number="22222")

        user1 = User.objects.get(username="Janusz")

        self.assertEqual(
            get_viable_sets(user1, 0, 0),
            [{"lego_set": lego_set2, "single_diff": 0, "general_diff": 0}],
        )

    def test_user2_cant_build_anything(self):
        user2 = User.objects.get(username="Mariusz")

        self.assertEqual(get_viable_sets(user2, 0, 0), [])

    def test_user3_has_two_copies_of_set3(self):
        for f in self.user3.usercollection.ownedlegoset_set.all():
            print(f)

    def test_user3_has_multiple_no_of_one_set(self):
        user3 = User.objects.get(username="Julia")

        lego_set1 = LegoSet.objects.get(number="11111")
        lego_set2 = LegoSet.objects.get(number="22222")
        lego_set3 = LegoSet.objects.get(number="33333")

        self.assertTrue(
            {"lego_set": lego_set1, "single_diff": 0, "general_diff": 0}
            not in get_viable_sets(user3, 0, 0)
        )
        self.assertTrue(
            {"lego_set": lego_set2, "single_diff": 0, "general_diff": 0}
            in get_viable_sets(user3, 0, 0)
        )
        self.assertTrue(
            {"lego_set": lego_set3, "single_diff": 0, "general_diff": 0}
            in get_viable_sets(user3, 0, 0)
        )

    def test_max_diffs(self):
        user2 = User.objects.get(username="Mariusz")

        lego_set1 = LegoSet.objects.get(number="11111")
        lego_set2 = LegoSet.objects.get(number="22222")
        lego_set3 = LegoSet.objects.get(number="33333")

        self.assertTrue(
            {"lego_set": lego_set1, "single_diff": "-", "general_diff": "-"}
            in get_viable_sets(user2)
        )
        self.assertTrue(
            {"lego_set": lego_set2, "single_diff": "-", "general_diff": "-"}
            in get_viable_sets(user2)
        )
        self.assertTrue(
            {"lego_set": lego_set3, "single_diff": "-", "general_diff": "-"}
            in get_viable_sets(user2)
        )

    def test_chosen_diffs(self):
        self.assertEqual([], get_viable_sets(self.user2, 4, 4))
        self.assertEqual([], get_viable_sets(self.user2, 5, 4))
        self.assertEqual(
            get_viable_sets(self.user2, 4, 5),
            [{"lego_set": self.lego_set2, "single_diff": 4, "general_diff": 5}],
        )

    def test_brick_stats(self):
        reviews1 = BrickStats.objects.filter(brick_set=self.lego_set1)
        reviews2 = BrickStats.objects.filter(brick_set=self.lego_set2)
        reviews3 = BrickStats.objects.filter(brick_set=self.lego_set3)

        self.assertEqual(get_avg_likes(reviews1), 6.0)
        self.assertEqual(get_avg_likes(reviews2), 10.0)
        self.assertEqual(get_avg_likes(reviews3), None)

        self.assertEqual(get_avg_age(reviews1), 17.5)
        self.assertEqual(get_avg_age(reviews2), 8.0)
        self.assertEqual(get_avg_age(reviews3), None)

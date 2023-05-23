from django.contrib.auth.models import User
from django.test import TestCase

from bsf.models import (
    Color,
    Brick,
    LegoSet, OwnedLegoSet, UserCollection,
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
        user_collection = UserCollection.objects.create(user=self.user1)
        user_collection.sets.add(self.lego_set1, through_defaults={"quantity": 2})
        user_collection.sets.add(self.lego_set2, through_defaults={"quantity": 3})

        user_collection.bricks.add(self.brick1, through_defaults={"quantity": 2})
        user_collection.bricks.add(self.brick2, through_defaults={"quantity": 5})

        self.owned_lego_set1 = OwnedLegoSet.initialize(self.lego_set1, self.user1)
        self.owned_lego_set2 = OwnedLegoSet.initialize(self.lego_set2, self.user1)

    def modify_quantities(self, brick1_qty, brick2_qty):
        self.owned_lego_set1.mark_as_missing(self.brick1, brick1_qty)
        self.owned_lego_set1.mark_as_missing(self.brick2, brick2_qty)

    def assert_quantities(self, brick1_diff, brick2_diff):
        query = self.owned_lego_set1.real_bricks_set()
        brick1 = query.get(brick=self.brick1)
        brick2 = query.get(brick=self.brick2)

        self.assertEqual(brick1.quantity - brick1.real_quantity, brick1_diff)
        self.assertEqual(brick2.quantity - brick2.real_quantity, brick2_diff)

    def test_no_bricks_should_be_missing(self):
        self.modify_quantities(0, 0)

    def test_bricks_should_be_missing(self):
        for i in range(1, 5):
            self.modify_quantities(2, 1)
            self.assert_quantities(2 * i, i)

    def test_no_bricks_should_be_missing_after_modification(self):
        self.modify_quantities(2, 1)
        self.modify_quantities(-2, -1)
        self.assert_quantities(0, 0)

    def test_owned_set_should_be_in_collection(self):
        self.assertEqual(
            self.user1.usercollection.setincollectionquantity_set.first().quantity, 1)
        self.assertTrue(
            self.user1.usercollection.ownedlegoset_set.contains(self.owned_lego_set1))

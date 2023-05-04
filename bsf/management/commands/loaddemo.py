from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from bsf.models import LegoSet, Color, Brick, UserCollection, Wishlist


class Command(BaseCommand):
    help = "Loads demo database"

    def handle(self, *args, **options):
        Color.objects.all().delete()
        Brick.objects.all().delete()
        LegoSet.objects.all().delete()
        UserCollection.objects.all().delete()
        User.objects.all().delete()
        Wishlist.objects.all().delete()

        color0 = Color.objects.create(color_id=0, name="Black", rgb="05131D")
        color2 = Color.objects.create(color_id=2, name="Green", rgb="237841")
        color4 = Color.objects.create(color_id=4, name="Red", rgb="C91A09")
        color14 = Color.objects.create(color_id=14, name="Yellow", rgb="F2CD37")
        color72 = Color.objects.create(
            color_id=72, name="Dark Bluish Gray", rgb="6C6E68"
        )

        # Example Brick objects
        brick1 = Brick.objects.create(
            brick_id=1,
            part_num="3024",
            color=color0,
            image_link="https://cdn.rebrickable.com/media/parts/elements/302426.jpg",
        )
        brick2 = Brick.objects.create(
            brick_id=2,
            part_num="3020",
            color=color0,
            image_link="https://cdn.rebrickable.com/media/parts/elements/302026.jpg",
        )
        brick3 = Brick.objects.create(
            brick_id=3,
            part_num="4070",
            color=color4,
            image_link="https://cdn.rebrickable.com/media/parts/ldraw/4/4070.png",
        )
        brick4 = Brick.objects.create(
            brick_id=4,
            part_num="3005",
            color=color2,
            image_link="https://cdn.rebrickable.com/media/parts/elements/300528.jpg",
        )
        brick5 = Brick.objects.create(
            brick_id=5,
            part_num="3005",
            color=color4,
            image_link="https://cdn.rebrickable.com/media/parts/elements/300521.jpg",
        )
        brick6 = Brick.objects.create(
            brick_id=6,
            part_num="3626cpr2463",
            color=color14,
            image_link="https://cdn.rebrickable.com/media/parts/elements/6211710.jpg",
        )
        brick7 = Brick.objects.create(
            brick_id=7,
            part_num="53401",
            color=color72,
            image_link="https://cdn.rebrickable.com/media/parts/elements/4279714.jpg",
        )

        # Example LegoSet object
        lego_set1 = LegoSet.objects.create(
            number="10290-1",
            name="Pickup Truck",
            image_link="https://cdn.rebrickable.com/media/sets/10290-1.jpg",
            inventory_id=1,
        )
        lego_set1.bricks.add(brick1, through_defaults={"quantity": 10})
        lego_set1.bricks.add(brick2, through_defaults={"quantity": 5})
        lego_set1.bricks.add(brick3, through_defaults={"quantity": 5})
        lego_set2 = LegoSet.objects.create(
            number="10312-1",
            name="Jazz Club",
            image_link="https://cdn.rebrickable.com/media/sets/10312-1.jpg",
            inventory_id=2,
        )
        lego_set2.bricks.add(brick1, through_defaults={"quantity": 100})
        lego_set2.bricks.add(brick2, through_defaults={"quantity": 20})
        lego_set2.bricks.add(brick3, through_defaults={"quantity": 5})
        lego_set3 = LegoSet.objects.create(
            number="75192-1",
            name="Millenium Falcon",
            image_link="https://cdn.rebrickable.com/media/sets/75192-1.jpg",
            inventory_id=3,
        )
        lego_set3.bricks.add(brick4, through_defaults={"quantity": 2000})
        lego_set3.bricks.add(brick5, through_defaults={"quantity": 5000})
        lego_set3.bricks.add(brick7, through_defaults={"quantity": 1})
        lego_set4 = LegoSet.objects.create(
            number="60118-1",
            name="Garbage Truck",
            image_link="https://cdn.rebrickable.com/media/sets/60118-1.jpg",
            inventory_id=4,
        )
        lego_set4.bricks.add(brick2, through_defaults={"quantity": 25})
        lego_set4.bricks.add(brick3, through_defaults={"quantity": 10})

        user1 = User.objects.create_user("marian", "marian@mimuw.edu.pl", "123456")
        user1_collection = UserCollection.objects.create(user=user1)
        user1_collection.bricks.add(brick1, through_defaults={"quantity": 20})
        user1_collection.bricks.add(brick2, through_defaults={"quantity": 10})
        user1_collection.sets.add(lego_set1, through_defaults={"quantity": 1})

        Wishlist.objects.create(user=user1)

        user2 = User.objects.create_user("marcin", "marcin@mimuw.edu.pl", "123456")
        user2_collection = UserCollection.objects.create(user=user2)
        user2_collection.bricks.add(brick3, through_defaults={"quantity": 20})
        user2_collection.bricks.add(brick4, through_defaults={"quantity": 10})
        user2_collection.sets.add(lego_set2, through_defaults={"quantity": 1})

        Wishlist.objects.create(user=user2)

        self.stdout.write(self.style.SUCCESS("Successfully created demo database"))

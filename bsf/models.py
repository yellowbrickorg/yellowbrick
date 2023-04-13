from django.db import models
from django.contrib.auth.models import User


class Color(models.Model):
    color_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=60)
    rgb = models.CharField(max_length=6)
    is_transparent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.color_id} - {self.name}"


class Brick(models.Model):
    brick_id = models.IntegerField(primary_key=True)
    part_num = models.CharField(max_length=30)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.brick_id}"


"""
Klasa reprezentująca zestaw.
Zestaw ma swój numer, nazwę i składa się z określonych klocków
w określonych ilościach.
Ponadto ma link do obrazka, na którym jest pokazany.
"""


class LegoSet(models.Model):
    number = models.CharField(max_length=20)
    name = models.CharField(max_length=256)
    image_link = models.CharField(max_length=256)
    bricks = models.ManyToManyField(Brick, through="BrickInSetQuantity")
    inventory_id = models.IntegerField(unique=True)

    def __str__(self):
        return f"{self.number} - {self.name}"


class UserCollection(models.Model):
    """
    Klasa reprezentująca kolekcję użytkownika.
    Użytkownik ma określone ilości klocków i zestawów.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bricks = models.ManyToManyField(Brick, through="BrickInCollectionQuantity")
    sets = models.ManyToManyField(LegoSet, through="SetInCollectionQuantity")

    def __str__(self):
        return f'Collection of {self.user.username}'


class BrickInSetQuantity(models.Model):
    brick_set = models.ForeignKey(LegoSet, on_delete=models.CASCADE)
    brick = models.ForeignKey(Brick, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.quantity} x {self.brick} in set {self.brick_set.number}'


class BrickInCollectionQuantity(models.Model):
    brick = models.ForeignKey(Brick, on_delete=models.CASCADE)
    collection = models.ForeignKey(UserCollection, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.brick} in {self.collection.user.username}'s collection"


class SetInCollectionQuantity(models.Model):
    brick_set = models.ForeignKey(LegoSet, on_delete=models.CASCADE)
    collection = models.ForeignKey(UserCollection, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.brick_set} in {self.collection.user.username}'s collection"


class CollectionFilter(models.Model):
    class Meta:
        abstract = True

    @staticmethod
    def get_viable_sets(user : User, single_diff=0, general_diff=0):
        """
        Args:
            user: nazwa uzytkowanika
            single_diff: różnica mówiąca, ile klocków każdego rodzaju może nam brakować w danym zestawie
            general_diff: różnica mówiąca, ile klocków w sumie może nam brakować w danym zestawie
        """

        all_users_bricks = {}
        all_users_bricks = CollectionFilter.get_dict_of_users_bricks(user, all_users_bricks)
        all_users_bricks = CollectionFilter.get_dict_of_users_bricks_from_sets(user, all_users_bricks)

        viable_sets = []
        for lego_set in LegoSet.objects.all():
            if CollectionFilter.check_set(all_users_bricks, lego_set, single_diff, general_diff):
                viable_sets.append(lego_set)

        return viable_sets

    @staticmethod
    def check_set(all_users_bricks, lego_set: LegoSet, single_diff=0, general_diff=0):
        for brick_data in BrickInSetQuantity.objects.filter(brick_set = lego_set):
            q_needed = brick_data.quantity
            q_collected = all_users_bricks[brick_data.brick]
            diff = q_needed - q_collected

            if diff > single_diff:
                return False

            general_diff -= max(0, diff)
            if general_diff < 0:
                return False
        return True

    @staticmethod
    def get_dict_of_users_bricks(user : User, all_users_bricks=None):
        users_collection = UserCollection.objects.get(user = user)

        for brick_data in BrickInCollectionQuantity.objects.filter(collection = users_collection):
            q = brick_data.quantity
            if brick_data.brick in all_users_bricks:
                all_users_bricks[brick_data.brick] += q
            else:
                all_users_bricks[brick_data.brick] = q
        return all_users_bricks

    @staticmethod
    def get_dict_of_users_bricks_from_sets(user : User, all_users_bricks=None):
        users_collection = UserCollection.objects.get(user = user)

        for set_data in SetInCollectionQuantity.objects.filter(collection = users_collection):
            users_set = set_data.brick_set
            for brick_data in BrickInSetQuantity.objects.filter(brick_set = users_set):
                q = brick_data.quantity
                if brick_data.brick in all_users_bricks:
                    all_users_bricks[brick_data.brick] += q
                else:
                    all_users_bricks[brick_data.brick] = q
        return all_users_bricks

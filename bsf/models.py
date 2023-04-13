from django.db import models
from django.contrib.auth.models import User


class Color(models.Model):
    color_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=60)
    rgb = models.CharField(max_length=6)
    is_transparent = models.BooleanField(default=False)

    def __str__(self):
        return str(self.color_id)


class Brick(models.Model):
    brick_id = models.IntegerField(primary_key=True)
    part_num = models.CharField(max_length=30)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.brick_id)


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

    def __str__(self):
        return f"{self.number} - {self.name}"


"""
Klasa reprezentująca kolekcję użytkownika.
Użytkownik ma określone ilości klocków i zestawów.
"""


class UserCollection(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bricks = models.ManyToManyField(Brick, through="BrickInCollectionQuantity")
    sets = models.ManyToManyField(LegoSet, through="SetInCollectionQuantity")

    def __str__(self):
        return f'Collection of {self.user.username}'

"""
Klasy realizujące zależność wiele-do-wielu.
"""


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
    def get_viable_sets(user_id, single_diff=0, general_diff=0):
        """
        Args:
            user_id: id użytkownika
            single_diff: różnica mówiąca, ile klocków każdego rodzaju może nam brakować w danym zestawie
            general_diff: różnica mówiąca, ile klocków w sumie może nam brakować w danym zestawie
        """
        all_users_bricks = {}
        all_users_bricks = CollectionFilter.get_dict_of_users_bricks(user_id, all_users_bricks)
        all_users_bricks = CollectionFilter.get_dict_of_users_bricks_from_sets(user_id, all_users_bricks)

        viable_sets = []
        for lego_set in LegoSet.objects.all():
            if CollectionFilter.check_set(all_users_bricks, lego_set, single_diff, general_diff):
                viable_sets.append(lego_set)

        return viable_sets

    @staticmethod
    def check_set(all_users_bricks, lego_set: LegoSet, single_diff=0, general_diff=0):
        for brick in lego_set.bricks.all():
            q_needed = BrickInSetQuantity.objects.get(brick_set=lego_set, brick=brick).quantity
            q_collected = all_users_bricks[brick]
            diff = q_needed - q_collected

            if diff > single_diff:
                return False

            general_diff -= max(0, diff)
            if general_diff < 0:
                return False
        return True

    @staticmethod
    def get_dict_of_users_bricks(user_id, all_users_bricks=None):
        users_collection = UserCollection.objects.get(userid=user_id)

        for users_brick in UserCollection.objects.get(user_id=user_id).bricks:
            q = BrickInCollectionQuantity.objects.get(collection=users_collection, brick=users_brick).quantity
            if users_brick in all_users_bricks:
                all_users_bricks[users_brick] += q
            else:
                all_users_bricks[users_brick] = q
        return all_users_bricks

    @staticmethod
    def get_dict_of_users_bricks_from_sets(user_id, all_users_bricks=None):
        users_collection = UserCollection.objects.create(userid=user_id)

        for set_id in users_collection.sets.all():
            users_set = LegoSet.objects.get(number=set_id)
            for users_brick in users_set.bricks.all():
                q = BrickInSetQuantity.objects.get(brick_set=users_set, brick=users_brick).quantity
                if users_brick in all_users_bricks:
                    all_users_bricks[users_brick] += q
                else:
                    all_users_bricks[users_brick] = q
        return all_users_bricks

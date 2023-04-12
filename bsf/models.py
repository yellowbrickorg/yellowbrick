from django.db import models
from django.contrib.auth.models import User


class Color(models.Model):
    color_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=60)
    rgb = models.CharField(max_length=6)
    is_transparent = models.BooleanField(default=False)

    def __str__(self):
        return self.color_id

class Brick(models.Model):
    brick_id = models.IntegerField(primary_key=True)
    part_num = models.CharField(max_length=30)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)

    def __str__(self):
        return self.brick_id

"""
Klasa reprezentująca zestaw.
Zestaw ma swój numer, nazwę i składa się z określonych klocków
w określonych ilościach.
Ponadto ma link do obrazka, na którym jest pokazany.
"""
class LegoSet(models.Model):
    number = models.CharField(max_length=20)
    name = models.CharField(max_length=256)
    imageLink = models.CharField(max_length=256)
    bricks = models.ManyToManyField(Brick, through="BrickInSetQuantity")
    def __str__(self):
        return self.number

"""
Klasa reprezentująca kolekcję użytkownika.
Użytkownik ma określone ilości klocków i zestawów.
"""
class UserCollection(models.Model):
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    bricks = models.ManyToManyField(Brick, through="BrickInCollectionQuantity")
    sets = models.ManyToManyField(LegoSet, through="SetInCollectionQuantity")
    def __str__(self):
        return self.userid

"""
Klasy realizujące zależność wiele-do-wielu.
"""
class BrickInSetQuantity(models.Model):
    brickset = models.ForeignKey(LegoSet, on_delete=models.CASCADE)
    brick = models.ForeignKey(Brick, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

class BrickInCollectionQuantity(models.Model):
    brick = models.ForeignKey(Brick, on_delete=models.CASCADE)
    collection = models.ForeignKey(UserCollection, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

class SetInCollectionQuantity(models.Model):
    brickset = models.ForeignKey(LegoSet, on_delete=models.CASCADE)
    collection = models.ForeignKey(UserCollection, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

from django.db import models

""" TODO: tymczasowe klasy """
class LegoBrick(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

class User(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

""" koniec tymczasowych klas """

"""
Klasa reprezentująca zestaw.
Zestaw ma swój numer, nazwę i składa się z określonych klocków
w określonych ilościach.
"""
class LegoSet(models.Model):
    number = models.CharField(max_length=20)
    name = models.CharField(max_length=256)
    bricks = models.ManyToManyField(LegoBrick, through="BrickInSetQuantity")
    def __str__(self):
        return self.number

"""
Klasa reprezentująca kolekcję użytkownika.
Użytkownik ma określone ilości klocków i zestawów.
"""
class UserCollection(models.Model):
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    bricks = models.ManyToManyField(LegoBrick, through="BrickInCollectionQuantity")
    sets = models.ManyToManyField(LegoSet, through="SetInCollectionQuantity")
    def __str__(self):
        return self.userid

"""
Klasy realizujące zależność wiele-do-wielu.
"""
class BrickInSetQuantity(models.Model):
    brickset = models.ForeignKey(LegoSet, on_delete=models.CASCADE)
    brick = models.ForeignKey(LegoBrick, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

class BrickInCollectionQuantity(models.Model):
    brick = models.ForeignKey(LegoBrick, on_delete=models.CASCADE)
    collection = models.ForeignKey(UserCollection, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

class SetInCollectionQuantity(models.Model):
    brickset = models.ForeignKey(LegoSet, on_delete=models.CASCADE)
    collection = models.ForeignKey(UserCollection, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
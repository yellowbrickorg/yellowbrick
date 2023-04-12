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

class CollectionFilter(models.Model):
    class Meta:
        abstract = True

    """
        --- UŻYWANE ZMIENNE DO OBSŁUGI FUNKCJI POMOCNICZYCH
        single_diff - roznica mowiaca ile klockow kazdego rodzaju moze nam brakowac w danym zestawie
        general_diff - roznica mowiaca ile klockow w sumie moze nam brakowac w danym zestawie
        TODO - może ignorowanie kolorów klocków? trzebaby mocno przenalizowac dane pod względem podobnych nazw / id
    """

    def getViableSets(user_id, single_diff = 0, general_diff = 0):
        all_users_bricks = {}
        all_users_bricks = CollectionFilter.getDictOfUsersBrix(user_id, all_users_bricks)
        all_users_bricks = CollectionFilter.getDictOfUsersBrixFromSets(user_id, all_users_bricks)

        viableSets =[]
        for set in LegoSet.objects.all():
            if CollectionFilter.checkSet(all_users_bricks, set, single_diff, general_diff):
                viableSets.append(set)
        
        print(viableSets) # debug
        return viableSets

    def checkSet(all_users_bricks, set: LegoSet, single_diff = 0, general_diff = 0):
        for brick in set.bricks.all():
            q_needed = BrickInSetQuantity.objects.get(brickset = set, brick = brick).quantity
            q_collected = all_users_bricks[brick]
            diff = q_needed - q_collected

            if(diff > single_diff):
                return False
            
            general_diff -= max(0, diff)
            if(general_diff < 0):
                return False
        return True
    
    def getDictOfUsersBrix(user_id, all_users_bricks = {}):
        for users_brick in UserCollection.bricks:
            q = BrickInCollectionQuantity.objects.get(collection = users_collection, brick = users_brick).quantity
            if(users_brick in all_users_bricks):
                all_users_bricks[users_brick] += q
            else:
                all_users_bricks[users_brick] = q
        return all_users_bricks
    
    def getDictOfUsersBrixFromSets(user_id, all_users_bricks ={}):
        users_collection = UserCollection.objects.create(userid=user_id)

        for set_id in users_collection.sets.all():
            users_set = LegoSet.objects.get(number = set_id)
            for users_brick in set.bricks.all():
                q = BrickInSetQuantity.objects.get(brickset = users_set, brick = users_brick).quantity
                if(users_brick in all_users_bricks):
                    all_users_bricks[users_brick] += q
                else:
                    all_users_bricks[users_brick] = q
        return all_users_bricks
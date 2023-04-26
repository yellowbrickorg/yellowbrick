from django.db import models
from django.contrib.auth.models import User


class Color(models.Model):
    """
    Represents a color of LEGO bricks.

    Attributes:
        color_id : color ID number, compliant with LEGO's color numeric identification
        name : color's name
        rgb : color's RGB value
        is_transparent : indication whether color is transparent
    """

    color_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=60)
    rgb = models.CharField(max_length=6)
    is_transparent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.color_id} - {self.name}"


class Brick(models.Model):
    """
    Represents a LEGO brick.

    Attributes:
        brick_id : internal brick ID
        part_num : part number compliant with LEGO's numeric identification
        color : brick color
        image_link : link to brick's image
    """

    brick_id = models.IntegerField(primary_key=True)
    part_num = models.CharField(max_length=30)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    image_link = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.brick_id}"


class LegoSet(models.Model):
    """
    Represents a LEGO set.

    Attributes:
        number : set number compliant with LEGO set identification
        name : set name
        image_link : link to an image of set
        bricks : set of bricks that forms a LEGO set
        inventory_id : id of corresponding Rebrickable's inventory
    """

    number = models.CharField(max_length=20)
    name = models.CharField(max_length=256)
    image_link = models.CharField(max_length=256)
    bricks = models.ManyToManyField(Brick, through="BrickInSetQuantity")
    inventory_id = models.IntegerField()
    theme = models.CharField(max_length=256)
    quantity_of_bricks = models.IntegerField()

    def __str__(self):
        return f"{self.number} - {self.name}"


class UserCollection(models.Model):
    """
    Represents User's LEGO collection. Can contain whole sets or individual bricks.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bricks = models.ManyToManyField(Brick, through="BrickInCollectionQuantity")
    sets = models.ManyToManyField(LegoSet, through="SetInCollectionQuantity")

    def __str__(self):
        return f"Collection of {self.user.username}"


class BrickInSetQuantity(models.Model):
    brick_set = models.ForeignKey(LegoSet, on_delete=models.CASCADE)
    brick = models.ForeignKey(Brick, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.brick} in set {self.brick_set.number}"


class BrickInCollectionQuantity(models.Model):
    brick = models.ForeignKey(Brick, on_delete=models.CASCADE)
    collection = models.ForeignKey(UserCollection, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return (
            f"{self.quantity} x {self.brick} "
            f"in {self.collection.user.username}'s collection"
        )


class SetInCollectionQuantity(models.Model):
    brick_set = models.ForeignKey(LegoSet, on_delete=models.CASCADE)
    collection = models.ForeignKey(UserCollection, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return (
            f"{self.quantity} x {self.brick_set} "
            f"in {self.collection.user.username}'s collection"
        )


class BrickStats(models.Model):
    brick_set = models.ForeignKey(LegoSet, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    likes = models.IntegerField()
    min_recommended_age = models.IntegerField()

    def __str__(self) -> str:
        return (
            f"Rated {self.brick_set}: {self.likes} likes, and {self.min_recommended_age} recommended age, "
            f"by user {self.user}"
        )

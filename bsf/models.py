from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


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

    def __str__(self):
        return f"{self.number} - {self.name}"

    def number_of_bricks(self):
        ret = 0
        for b in self.brickinsetquantity_set.all():
            ret += b.quantity
        return ret


class UserCollection(models.Model):
    """
    Represents User's LEGO collection. Can contain whole sets or individual bricks.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bricks = models.ManyToManyField(Brick, through="BrickInCollectionQuantity")
    sets = models.ManyToManyField(LegoSet, through="SetInCollectionQuantity")

    def modify_set_quantity(self, brick_set, quantity):
        set_collection = SetInCollectionQuantity.objects.filter(collection=self)
        if set_collection.filter(brick_set=brick_set).exists():
            set_collection.get(brick_set=brick_set).modify_quantity_or_delete(quantity)
        elif quantity > 0:
            set_collection.create(
                brick_set=brick_set, quantity=quantity, collection=self
            )

    def modify_brick_quantity(self, brick, quantity):
        brick_collection = BrickInCollectionQuantity.objects.filter(collection=self)
        if brick_collection.filter(brick=brick).exists():
            brick_collection.get(brick=brick).modify_quantity_or_delete(quantity)
        elif quantity > 0:
            brick_collection.create(brick=brick, quantity=quantity, collection=self)

    def __str__(self):
        return f"Collection of {self.user.username}"


class Countable(models.Model):
    quantity = models.PositiveIntegerField()

    class Meta:
        abstract = True

    def modify_quantity_or_delete(self, quantity):
        if self.quantity + quantity <= 0:
            self.delete()
        self.quantity += quantity


class BrickInSetQuantity(Countable):
    brick_set = models.ForeignKey(LegoSet, on_delete=models.CASCADE)
    brick = models.ForeignKey(Brick, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantity} x {self.brick} in set {self.brick_set.number}"


class BrickInCollectionQuantity(Countable):
    brick = models.ForeignKey(Brick, on_delete=models.CASCADE)
    collection = models.ForeignKey(UserCollection, on_delete=models.CASCADE)

    def __str__(self):
        return (
            f"{self.quantity} x {self.brick} "
            f"in {self.collection.user.username}'s collection"
        )


class SetInCollectionQuantity(Countable):
    brick_set = models.ForeignKey(LegoSet, on_delete=models.CASCADE)
    collection = models.ForeignKey(UserCollection, on_delete=models.CASCADE)

    def __str__(self):
        return (
            f"{self.quantity} x {self.brick_set} "
            f"in {self.collection.user.username}'s collection"
        )


class Side(models.IntegerChoices):
    OFFERED = 0
    WANTED = 1

    @staticmethod
    def negate(side):
        assert side in [Side.OFFERED, Side.WANTED]
        return 1 - side


class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def modify_sets_quantity(self, brick_set, quantity, side):
        sets_in_wishlist = SetInWishlistQuantity.objects.filter(user=self.user)
        if sets_in_wishlist.filter(legoset=brick_set, side=side).exists():
            sets_in_wishlist.get(
                legoset=brick_set, side=side
            ).modify_quantity_or_delete(quantity)
        elif quantity > 0:
            sets_in_wishlist.create(
                legoset=brick_set, quantity=quantity, user=self.user, side=side
            )

    def modify_bricks_quantity(self, brick, quantity, side):
        bricks_in_wishlist = BrickInWishlistQuantity.objects.filter(user=self.user)
        if bricks_in_wishlist.filter(brick=brick, side=side).exists():
            bricks_in_wishlist.get(brick=brick, side=side).modify_quantity_or_delete(
                quantity
            )
        elif quantity > 0:
            bricks_in_wishlist.create(
                brick=brick, quantity=quantity, user=self.user, side=side
            )


class BrickInWishlistQuantity(Countable):
    """
    Represents a LEGO brick in a user's wishlist.
    Attributes:
        user : whose wishlist does the brick belong to
        brick :
        quantity :
        side :  WANTED - user wants to receive the brick,
                OFFERED - user offers the brick
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wishlist_bricks"
    )
    brick = models.ForeignKey(Brick, on_delete=models.CASCADE)
    side = models.IntegerField(choices=Side.choices)

    class Meta:
        unique_together = (("user", "brick", "side"),)
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name="check_quantity_positive_wishlist",
            )
        ]

    def __str__(self):
        if self.side == Side.WANTED:
            return (
                f"{self.quantity} x (brick {self.brick}) "
                f"wanted "
                f"in {self.user.username}'s wishlist"
            )
        else:
            return (
                f"{self.quantity} x (brick {self.brick}) "
                f"offered "
                f"in {self.user.username}'s wishlist"
            )


class SetInWishlistQuantity(Countable):
    """
    Represents a LEGO set in a user's wishlist.
    Attributes:
        user : whose wishlist does the set belong to
        legoset :
        quantity :
        side :  WANTED - user wants to receive the set,
                OFFERED - user offers the set
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wishlist_sets"
    )
    legoset = models.ForeignKey(LegoSet, on_delete=models.CASCADE)
    side = models.IntegerField(choices=Side.choices)

    class Meta:
        unique_together = (("user", "legoset", "side"),)
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name="set_check_quantity_positive_wishlist",
            )
        ]

    def __str__(self):
        return (
            f"{self.quantity} x {self.legoset} " f"in {self.user.username}'s wishlist"
        )


class ExchangeOffer(models.Model):
    """
    Represents an offer that 'offer_author' made to 'offer_receiver'

    Attributes:
        offer_author :
        offer_receiver :
    """

    offer_author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="authored_offers"
    )
    offer_receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_offers"
    )

    class Status(models.IntegerChoices):
        PENDING = 0, _("Pending")
        ACCEPTED = 1, _("Accepted")
        EXCHANGED = 2, _("Exchanged")

    author_state = models.IntegerField(choices=Status.choices, default=Status.ACCEPTED)
    receiver_state = models.IntegerField(choices=Status.choices, default=Status.PENDING)

    exchanged = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(offer_author=models.F("offer_receiver")),
                name="check_author_receiver_different",
            )
        ]

    def __str__(self):
        return (
            f"Offer of {self.offer_author.username} to {self.offer_receiver.username}"
        )


class BrickInOfferQuantity(Countable):
    """
    Represents a LEGO brick in an offer.
    Attributes:
        offer : offer the brick is part of
        brick :
        quantity :
        side :  WANTED - 'offer_author' from 'offer' wants to receive the brick,
                OFFERED - 'offer_author' from 'offer' offers the brick
    """

    offer = models.ForeignKey(ExchangeOffer, on_delete=models.CASCADE)
    brick = models.ForeignKey(Brick, on_delete=models.CASCADE)
    side = models.IntegerField(choices=Side.choices)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name="check_quantity_positive_offer_brick",
            )
        ]

    def __str__(self):
        return (
            f"{self.quantity} x {self.brick} "
            f"in {self.offer.offer_author.username}'s offer to {self.offer.offer_receiver.username}"
        )


class SetInOfferQuantity(Countable):
    """
    Represents a LEGO brick in an offer.

    Attributes:
        offer : offer the brick is part of
        legoset :
        quantity :
        side :  WANTED - 'offer_author' from 'offer' wants to receive the brick,
                OFFERED - 'offer_author' from 'offer' offers the brick
    """

    offer = models.ForeignKey(ExchangeOffer, on_delete=models.CASCADE)
    legoset = models.ForeignKey(LegoSet, on_delete=models.CASCADE)
    side = models.IntegerField(choices=Side.choices)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name="check_quantity_positive_offer_set",
            )
        ]

    def __str__(self):
        return (
            f"{self.quantity} x {self.legoset} "
            f"in {self.offer.offer_author.username}'s offer to {self.offer.offer_receiver.username}"
        )

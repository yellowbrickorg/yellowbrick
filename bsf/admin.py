from django.contrib import admin
from .models import (
    UserCollection,
    LegoSet,
    Brick,
    Color,
    BrickInCollectionQuantity,
    BrickInSetQuantity,
    SetInCollectionQuantity,
)

admin.site.register(UserCollection)
admin.site.register(LegoSet)
admin.site.register(Brick)
admin.site.register(Color)
admin.site.register(BrickInSetQuantity)
admin.site.register(BrickInCollectionQuantity)
admin.site.register(SetInCollectionQuantity)

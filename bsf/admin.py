from django.contrib import admin
from .models import UserCollection, LegoSet, Brick, Color

admin.site.register(UserCollection)
admin.site.register(LegoSet)
admin.site.register(Brick)
admin.site.register(Color)

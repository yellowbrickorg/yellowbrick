from django.db import models

class Color(models.Model):
    color_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    rgb = models.CharField(max_length=6)
    is_transparent = models.BooleanField(default=False)
class Brick(models.Model):
    brick_id = models.IntegerField(primary_key=True)
    part_num = models.CharField(max_length=30)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)


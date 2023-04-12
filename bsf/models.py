from django.db import models

class Color(models.Model):
    color_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
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


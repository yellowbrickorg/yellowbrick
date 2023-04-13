# Generated by Django 4.2 on 2023-04-13 13:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('bsf', '0003_brickincollectionquantity_brickinsetquantity_legoset_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='brickinsetquantity',
            old_name='brickset',
            new_name='brick_set',
        ),
        migrations.RenameField(
            model_name='legoset',
            old_name='imageLink',
            new_name='image_link',
        ),
        migrations.RenameField(
            model_name='setincollectionquantity',
            old_name='brickset',
            new_name='brick_set',
        ),
        migrations.RenameField(
            model_name='usercollection',
            old_name='userid',
            new_name='user',
        ),
        migrations.AlterField(
            model_name='usercollection',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]

# Generated by Django 4.2 on 2023-04-13 18:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Brick',
            fields=[
                ('brick_id', models.IntegerField(primary_key=True, serialize=False)),
                ('part_num', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='BrickInCollectionQuantity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('brick', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bsf.brick')),
            ],
        ),
        migrations.CreateModel(
            name='BrickInSetQuantity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('brick', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bsf.brick')),
            ],
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('color_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=60)),
                ('rgb', models.CharField(max_length=6)),
                ('is_transparent', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='LegoSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=256)),
                ('image_link', models.CharField(max_length=256)),
                ('bricks', models.ManyToManyField(through='bsf.BrickInSetQuantity', to='bsf.brick')),
            ],
        ),
        migrations.CreateModel(
            name='SetInCollectionQuantity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('brick_set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bsf.legoset')),
            ],
        ),
        migrations.CreateModel(
            name='UserCollection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bricks', models.ManyToManyField(through='bsf.BrickInCollectionQuantity', to='bsf.brick')),
                ('sets', models.ManyToManyField(through='bsf.SetInCollectionQuantity', to='bsf.legoset')),
                (
                'user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='setincollectionquantity',
            name='collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bsf.usercollection'),
        ),
        migrations.AddField(
            model_name='brickinsetquantity',
            name='brick_set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bsf.legoset'),
        ),
        migrations.AddField(
            model_name='brickincollectionquantity',
            name='collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bsf.usercollection'),
        ),
        migrations.AddField(
            model_name='brick',
            name='color',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bsf.color'),
        ),
    ]

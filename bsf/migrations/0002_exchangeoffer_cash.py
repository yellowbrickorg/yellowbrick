# Generated by Django 4.2 on 2023-05-24 20:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bsf", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="exchangeoffer",
            name="cash",
            field=models.IntegerField(default=0),
        ),
    ]
# Generated by Django 4.2 on 2023-05-16 20:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("bsf", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomLegoSet",
            fields=[
                (
                    "legoset_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="bsf.legoset",
                    ),
                ),
                ("video_link", models.CharField(max_length=256)),
            ],
            bases=("bsf.legoset",),
        ),
    ]
# Generated by Django 4.2 on 2023-06-01 12:47

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
            name="Brick",
            fields=[
                ("brick_id", models.IntegerField(primary_key=True, serialize=False)),
                ("part_num", models.CharField(max_length=30)),
                ("image_link", models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name="BrickInCollectionQuantity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.IntegerField(default=1)),
                (
                    "brick",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="bsf.brick"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="BrickInSetQuantity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.IntegerField(default=1)),
                (
                    "brick",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="bsf.brick"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Color",
            fields=[
                ("color_id", models.IntegerField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=60)),
                ("rgb", models.CharField(max_length=6)),
                ("is_transparent", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="ExchangeChain",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "initial_author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="authored_chains",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "initial_receiver",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="received_chains",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ExchangeOffer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "author_state",
                    models.IntegerField(
                        choices=[
                            (0, "Pending"),
                            (1, "Accepted"),
                            (2, "Exchanged"),
                            (3, "Refused"),
                        ],
                        default=1,
                    ),
                ),
                (
                    "receiver_state",
                    models.IntegerField(
                        choices=[
                            (0, "Pending"),
                            (1, "Accepted"),
                            (2, "Exchanged"),
                            (3, "Refused"),
                        ],
                        default=0,
                    ),
                ),
                ("cash", models.IntegerField(default=0)),
                ("exchanged", models.BooleanField(default=False)),
                ("which_in_order", models.PositiveIntegerField()),
                (
                    "exchange_chain",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="related_offers",
                        to="bsf.exchangechain",
                    ),
                ),
                (
                    "offer_author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="authored_offers",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "offer_receiver",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="received_offers",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LegoSet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("number", models.CharField(max_length=20)),
                ("name", models.CharField(max_length=256)),
                ("image_link", models.CharField(max_length=256)),
                ("inventory_id", models.IntegerField()),
                ("theme", models.CharField(max_length=256)),
                ("quantity_of_bricks", models.IntegerField()),
                ("custom_video_link", models.CharField(max_length=256, null=True)),
                ("visibility", models.BooleanField(default=True)),
                (
                    "author",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "bricks",
                    models.ManyToManyField(
                        through="bsf.BrickInSetQuantity", to="bsf.brick"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SetInCollectionQuantity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.IntegerField(default=1)),
                (
                    "brick_set",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="bsf.legoset"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Wishlist",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserCollection",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "bricks",
                    models.ManyToManyField(
                        through="bsf.BrickInCollectionQuantity", to="bsf.brick"
                    ),
                ),
                (
                    "sets",
                    models.ManyToManyField(
                        through="bsf.SetInCollectionQuantity", to="bsf.legoset"
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SetInWishlistQuantity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.IntegerField(default=1)),
                ("side", models.IntegerField(choices=[(0, "Offered"), (1, "Wanted")])),
                (
                    "legoset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="bsf.legoset"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="wishlist_sets",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SetInOfferQuantity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.IntegerField(default=1)),
                ("side", models.IntegerField(choices=[(0, "Offered"), (1, "Wanted")])),
                (
                    "legoset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="bsf.legoset"
                    ),
                ),
                (
                    "offer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="bsf.exchangeoffer",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="setincollectionquantity",
            name="collection",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="bsf.usercollection"
            ),
        ),
        migrations.CreateModel(
            name="OwnedLegoSet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("missing_total", models.PositiveIntegerField(default=0)),
                (
                    "collection",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="bsf.usercollection",
                    ),
                ),
                (
                    "realizes",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="bsf.legoset"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MissingBrick",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.IntegerField(default=1)),
                (
                    "brick",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="bsf.brick"
                    ),
                ),
                (
                    "overlays",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="bsf.brickinsetquantity",
                    ),
                ),
                (
                    "owned_set",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="bsf.ownedlegoset",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="BrickStats",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("likes", models.IntegerField()),
                ("min_recommended_age", models.IntegerField()),
                ("build_time", models.IntegerField()),
                (
                    "instruction_rating",
                    models.IntegerField(
                        choices=[
                            (0, "Very confusing"),
                            (1, "Somewhat clear"),
                            (2, "Mediocre"),
                            (3, "Mostly clear"),
                            (4, "Extremely clear"),
                        ]
                    ),
                ),
                ("review_text", models.TextField(blank=True, null=True)),
                (
                    "brick_set",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="bsf.legoset"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BrickInWishlistQuantity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.IntegerField(default=1)),
                ("side", models.IntegerField(choices=[(0, "Offered"), (1, "Wanted")])),
                (
                    "brick",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="bsf.brick"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="wishlist_bricks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="brickinsetquantity",
            name="brick_set",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="bsf.legoset"
            ),
        ),
        migrations.CreateModel(
            name="BrickInOfferQuantity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.IntegerField(default=1)),
                ("side", models.IntegerField(choices=[(0, "Offered"), (1, "Wanted")])),
                (
                    "brick",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="bsf.brick"
                    ),
                ),
                (
                    "offer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="bsf.exchangeoffer",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="brickincollectionquantity",
            name="collection",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="bsf.usercollection"
            ),
        ),
        migrations.AddField(
            model_name="brick",
            name="color",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="bsf.color"
            ),
        ),
        migrations.AddConstraint(
            model_name="setinwishlistquantity",
            constraint=models.CheckConstraint(
                check=models.Q(("quantity__gt", 0)),
                name="set_check_quantity_positive_wishlist",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="setinwishlistquantity",
            unique_together={("user", "legoset", "side")},
        ),
        migrations.AddConstraint(
            model_name="setinofferquantity",
            constraint=models.CheckConstraint(
                check=models.Q(("quantity__gt", 0)),
                name="check_quantity_positive_offer_set",
            ),
        ),
        migrations.AddConstraint(
            model_name="exchangeoffer",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("offer_author", models.F("offer_receiver")), _negated=True
                ),
                name="check_author_receiver_different",
            ),
        ),
        migrations.AddConstraint(
            model_name="brickinwishlistquantity",
            constraint=models.CheckConstraint(
                check=models.Q(("quantity__gt", 0)),
                name="check_quantity_positive_wishlist",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="brickinwishlistquantity",
            unique_together={("user", "brick", "side")},
        ),
        migrations.AddConstraint(
            model_name="brickinofferquantity",
            constraint=models.CheckConstraint(
                check=models.Q(("quantity__gt", 0)),
                name="check_quantity_positive_offer_brick",
            ),
        ),
    ]

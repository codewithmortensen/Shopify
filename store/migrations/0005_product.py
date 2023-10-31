# Generated by Django 4.2.6 on 2023-10-31 18:20

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0004_collection"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
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
                    "title",
                    models.CharField(
                        max_length=255,
                        validators=[django.core.validators.MinLengthValidator(3)],
                    ),
                ),
                ("slug", models.SlugField()),
                ("description", models.TextField()),
                ("price", models.DecimalField(decimal_places=2, max_digits=6)),
                ("last_update", models.DateTimeField(auto_now_add=True)),
                ("is_digital", models.BooleanField(default=False)),
                (
                    "collection",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="product",
                        to="store.collection",
                    ),
                ),
                (
                    "promotions",
                    models.ManyToManyField(blank=True, to="store.promotion"),
                ),
            ],
            options={
                "ordering": ["title", "price"],
                "indexes": [
                    models.Index(
                        fields=["title", "slug"], name="store_produ_title_8d6576_idx"
                    ),
                    models.Index(
                        fields=["price", "title"], name="store_produ_price_191685_idx"
                    ),
                ],
            },
        ),
    ]

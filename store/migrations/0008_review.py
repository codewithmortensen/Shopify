# Generated by Django 4.2.6 on 2023-10-31 18:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0007_stock"),
    ]

    operations = [
        migrations.CreateModel(
            name="Review",
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
                    "rating",
                    models.CharField(
                        choices=[
                            ("1", "very bad"),
                            ("1.5", "bad"),
                            ("2", "not good"),
                            ("2.5", "below average"),
                            ("3", "average"),
                            ("3.5", "decent"),
                            ("4", "good"),
                            ("4.5", "very good"),
                            ("5", "excellent"),
                        ],
                        max_length=3,
                    ),
                ),
                ("description", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_updated", models.BooleanField(default=False)),
                ("updated_at", models.DateTimeField(blank=True, null=True)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="store.customer",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="store.product",
                    ),
                ),
            ],
            options={
                "ordering": ["created_at", "is_updated", "updated_at"],
                "indexes": [
                    models.Index(
                        fields=["product", "customer", "rating"],
                        name="store_revie_product_946935_idx",
                    )
                ],
            },
        ),
    ]

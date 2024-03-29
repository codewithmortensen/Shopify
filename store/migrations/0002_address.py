# Generated by Django 4.2.6 on 2023-10-31 18:14

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Address",
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
                    "city",
                    models.CharField(
                        max_length=255,
                        validators=[django.core.validators.MinLengthValidator(3)],
                    ),
                ),
                (
                    "street",
                    models.CharField(
                        max_length=255,
                        validators=[django.core.validators.MinLengthValidator(3)],
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="address",
                        to="store.customer",
                    ),
                ),
            ],
        ),
    ]

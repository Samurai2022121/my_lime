# Generated by Django 3.2.4 on 2021-10-23 17:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import utils.models_utils


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_auto_20211023_1906"),
    ]

    operations = [
        migrations.CreateModel(
            name="GeneratedPassword",
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
                ("date", models.DateTimeField(auto_now_add=True)),
                (
                    "password",
                    models.IntegerField(
                        default=utils.models_utils.generate_new_password, editable=False
                    ),
                ),
                ("attempts", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

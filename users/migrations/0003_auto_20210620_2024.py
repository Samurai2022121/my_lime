# Generated by Django 3.2.4 on 2021-06-20 17:24

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_auto_20210620_1442"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="date_of_birth",
            field=models.DateField(blank=True, null=True, verbose_name="День рождения"),
        ),
        migrations.AlterField(
            model_name="user",
            name="fathers_name",
            field=models.CharField(
                blank=True, max_length=40, null=True, verbose_name="Отчество"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="name",
            field=models.CharField(
                blank=True, max_length=40, null=True, verbose_name="Имя"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=models.CharField(
                max_length=17,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message='Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.',
                        regex="^\\+?1?\\d{9,15}$",
                    )
                ],
                verbose_name="Телефон",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="surname",
            field=models.CharField(
                blank=True, max_length=40, null=True, verbose_name="Фамилия"
            ),
        ),
    ]

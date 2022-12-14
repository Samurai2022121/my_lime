# Generated by Django 4.0.1 on 2022-02-14 12:45

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0010_alter_recipe_calories_alter_recipe_carbohydrates_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipecategory",
            name="image",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="recipe/categories/",
                validators=[
                    django.core.validators.FileExtensionValidator(["svg", "png", "jpg"])
                ],
                verbose_name="Изображение категории рецепта",
            ),
        ),
    ]

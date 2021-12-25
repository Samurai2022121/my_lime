from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from products.models import Product
from users.models import User
from utils.models_utils import Timestampable


class RecipeCategory(MPTTModel):
    name = models.CharField(max_length=70, unique=True, verbose_name="Название")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Родительская категория",
    )
    image = models.FileField(
        blank=True,
        null=True,
        verbose_name="Изображение категории рецепта",
        upload_to="recipe/categories/",
    )
    is_archive = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]
        verbose_name = "категория рецептов"
        verbose_name_plural = "категории рецептов"

    class MPTTMeta:
        order_insertion_by = ["name"]

    def __str__(self):
        return self.name


class Recipe(Timestampable, models.Model):
    name = models.CharField(max_length=150, verbose_name="Название")
    author = models.ForeignKey(
        User, related_name="recipes", on_delete=models.CASCADE, verbose_name="Автор"
    )
    ingredients = models.ManyToManyField(
        Product, through="RecipeProducts", verbose_name="Ингриндиенты в наличии"
    )
    other_ingredients = models.TextField(
        null=True, blank=True, verbose_name="Прочие ингриндиенты"
    )
    recipe_category = models.ForeignKey(
        RecipeCategory,
        related_name="recipes",
        on_delete=models.SET_NULL,
        verbose_name="Категория",
        blank=True,
        null=True,
    )
    cook_time = models.IntegerField(verbose_name="Время приготовления")
    description = models.TextField(null=True, blank=True, verbose_name="Описание")
    image = models.ImageField(
        null=True, blank=True, verbose_name="Изображение", upload_to="recipe/"
    )
    protein = models.FloatField(blank=True, null=True, verbose_name="Белки")
    carbohydrates = models.FloatField(blank=True, null=True, verbose_name="Углеводы")
    fats = models.FloatField(blank=True, null=True, verbose_name="Жиры")
    calories = models.FloatField(blank=True, null=True, verbose_name="Калорийность")
    servings = models.IntegerField(verbose_name="Порции")
    video = models.URLField(null=True, blank=True)
    is_archive = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]
        unique_together = ["name", "recipe_category"]
        verbose_name = "рецепт"
        verbose_name_plural = "рецепты"

    def __str__(self):
        return self.name


class RecipeCookingSteps(models.Model):
    recipe = models.ForeignKey(
        Recipe, related_name="recipe_steps", on_delete=models.PROTECT
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    image = models.ImageField(upload_to="recipe/steps/")


class RecipeProducts(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name="Ингриндиенты"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="рецепт",
        related_name="recipe_products",
    )
    quantity = models.FloatField(default=1)

    class Meta:
        verbose_name = "ингриндиент для рецепта"
        verbose_name_plural = "ингриндиенты для рецепта"

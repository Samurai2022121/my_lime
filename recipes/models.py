from django.db import models

from products.models import Product
from users.models import User


class RecipeCategory(models.Model):
    name = models.CharField(max_length=70, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    class Meta:
        ordering = ['name']
        verbose_name = 'категория рецептов'
        verbose_name_plural = 'категории рецептов'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=150, verbose_name='Название')
    author = models.ForeignKey(User, related_name='recipes', on_delete=models.CASCADE, verbose_name='Автор')
    publication_date = models.DateTimeField(auto_now=True, verbose_name='Дата публикации')
    ingredients_in_stock = models.ManyToManyField(Product, related_name='recipes',
                                                  verbose_name='Ингриндиенты в наличии')
    other_ingredients = models.TextField(null=True, blank=True, verbose_name='Прочие ингриндиенты')
    recipe_category = models.ForeignKey(RecipeCategory, related_name='recipes', on_delete=models.SET_NULL,
                                        verbose_name='Категория', blank=True, null=True)
    cook_time = models.IntegerField(verbose_name='Время приготовления')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    image = models.ImageField(null=True, blank=True, verbose_name='Изображение')
    protein = models.FloatField(blank=True, null=True, verbose_name='Белки')
    carbohydrates = models.FloatField(blank=True, null=True, verbose_name='Углеводы')
    fats = models.FloatField(blank=True, null=True, verbose_name='Жиры')
    calories = models.FloatField(blank=True, null=True, verbose_name='Калорийность')

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'recipe_category']
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name

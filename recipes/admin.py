from django.contrib import admin

from utils.models_utils import ListDisplayAllModelFieldsAdminMixin
from .models import RecipeCategory, Recipe, RecipeProducts


@admin.register(RecipeCategory)
class RecipeCategoryAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(RecipeProducts)
class RecipeProductsAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass

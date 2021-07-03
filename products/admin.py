from django.contrib import admin

from utils.models_utils import ListDisplayAllModelFieldsAdminMixin
from .models import Category, Product, Subcategory


@admin.register(Category)
class CategoryAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Subcategory)
class SubcategoryAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass

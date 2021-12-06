from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from utils.models_utils import ListDisplayAllModelFieldsAdminMixin

from .models import Category, Product, ProductImages


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    fields = ["name", "parent", "description", "image"]


@admin.register(Product)
class ProductAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(ProductImages)
class ProductImagesAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    readonly_fields = ["image_150", "image_500"]

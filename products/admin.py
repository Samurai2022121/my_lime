from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from utils.models_utils import ListDisplayAllModelFieldsAdminMixin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    fields = ['name', 'parent', 'description']


@admin.register(Product)
class ProductAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass

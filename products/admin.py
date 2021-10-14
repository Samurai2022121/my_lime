from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from utils.models_utils import ListDisplayAllModelFieldsAdminMixin
from .models import Category, Product, ProductImages


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    fields = ['name', 'parent', 'description']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description', 'price', 'barcode', 'origin',
                    'in_stock', 'own_production', 'discount', 'get_1000_image', 'get_500_image',
                    'get_150_image')

    @admin.display(description='1000x1000 image')
    def get_1000_image(self, obj):
        return obj.images.image_1000

    @admin.display(description='500x500 image')
    def get_500_image(self, obj):
        return obj.images.image_500

    @admin.display(description='150x150 image')
    def get_150_image(self, obj):
        return obj.images.image_150


@admin.register(ProductImages)
class ProductImagesAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass

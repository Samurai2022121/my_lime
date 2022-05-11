from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from utils.models_utils import ListDisplayAllModelFieldsAdminMixin

from .models import (
    Category,
    MeasurementUnit,
    Product,
    ProductImages,
    ProductUnit,
    ProductUnitConversion,
)


@admin.register(ProductUnitConversion)
class ProductUnitConversionAdmin(admin.ModelAdmin):
    list_display = ("__str__",)


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    fields = ("name", "parent", "description", "image")
    search_fields = ("name", "description")


@admin.register(MeasurementUnit)
class MeasurementUnitAdmin(admin.ModelAdmin):
    pass


class ProductUnitInline(admin.TabularInline):
    model = ProductUnit
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        # preserve selected choice of unit names
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields["unit"].widget.can_change_related = False
        formset.form.base_fields["unit"].widget.can_add_related = False
        return formset


@admin.register(Product)
class ProductAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    inlines = (ProductUnitInline,)
    search_fields = ("name", "short_name")


@admin.register(ProductImages)
class ProductImagesAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    readonly_fields = ["image_150", "image_500"]

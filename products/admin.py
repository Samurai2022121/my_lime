from django import forms
from django.contrib import admin
from django_svg_image_form_field import SvgAndImageFormField
from mptt.admin import MPTTModelAdmin
from sorl.thumbnail.admin import AdminInlineImageMixin

from .models import (
    Category,
    MeasurementUnit,
    Product,
    ProductImage,
    ProductUnit,
    ProductUnitConversion,
)


@admin.register(ProductUnitConversion)
class ProductUnitConversionAdmin(admin.ModelAdmin):
    list_display = ("__str__",)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = []
        field_classes = {
            "image_svg": SvgAndImageFormField,
        }


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    fields = ("name", "parent", "description", "image", "image_svg", "is_excisable")
    search_fields = ("name", "description")
    list_filter = ("is_excisable",)
    form = CategoryForm


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


class ProductImageInline(AdminInlineImageMixin, admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "updated_at",
        "name",
        "short_name",
        "category",
        "own_production",
        "is_archive",
        "is_sorted",
        "vat_rate",
    )
    list_filter = ("is_sorted", "is_archive", "own_production", "vat_rate")
    inlines = (ProductUnitInline, ProductImageInline)
    search_fields = ("name", "short_name")

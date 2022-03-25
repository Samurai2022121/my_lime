from django.contrib import admin

from utils.models_utils import ListDisplayAllModelFieldsAdminMixin

from .models import DailyMenuPlan, MenuDish, TechCard, TechCardProduct


class TechCardProductInline(admin.StackedInline):
    autocomplete_fields = ("product_unit",)
    model = TechCardProduct
    extra = 1


@admin.register(TechCard)
class TechCardAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    autocomplete_fields = ("end_product",)
    inlines = [
        TechCardProductInline,
    ]


class MenuDishInline(admin.StackedInline):
    model = MenuDish
    extra = 1


@admin.register(DailyMenuPlan)
class DailyMenuPlanAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    inlines = [
        MenuDishInline,
    ]

from django.contrib import admin

from utils.models_utils import ListDisplayAllModelFieldsAdminMixin

from .models import DailyMenuPlan, MenuDish, TechCard, TechCardProduct


class ProductForTechCardInline(admin.StackedInline):
    model = TechCardProduct
    extra = 1


@admin.register(TechCard)
class TechCardAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    inlines = [
        ProductForTechCardInline,
    ]


class MenuDishInline(admin.StackedInline):
    model = MenuDish
    extra = 1


@admin.register(DailyMenuPlan)
class DailyMenuPlanAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    inlines = [
        MenuDishInline,
    ]

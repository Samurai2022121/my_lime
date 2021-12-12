from django.contrib import admin

from utils.models_utils import ListDisplayAllModelFieldsAdminMixin

from . import models


@admin.register(models.Shop)
class ShopAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(models.Personnel)
class PersonnelAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(models.Warehouse)
class WarehouseAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(models.TechCard)
class TechCardAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(models.DailyMenuPlan)
class DailyMenuPlanAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass

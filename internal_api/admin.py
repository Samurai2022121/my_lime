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


@admin.register(models.TechCardProduct)
class WarehouseAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


class ProductForTechCardInline(admin.StackedInline):
    model = models.TechCardProduct
    extra = 1


@admin.register(models.TechCard)
class TechCardAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    inlines = [
        ProductForTechCardInline,
    ]


@admin.register(models.MenuDish)
class MenuDishesAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


class MenuDishInline(admin.StackedInline):
    model = models.MenuDish
    extra = 1


@admin.register(models.DailyMenuPlan)
class DailyMenuPlanAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    inlines = [
        MenuDishInline,
    ]


@admin.register(models.WarehouseOrder)
class WarehouseOrderAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(models.WarehouseOrderPositions)
class WarehouseOrderPositionsAdmin(
    ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin
):
    pass


@admin.register(models.Supplier)
class SupplierAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(models.SupplyContract)
class SupplierAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass

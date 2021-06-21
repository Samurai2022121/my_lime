from django.contrib import admin

from products.models import Category, Product


class ListDisplayAllModelFieldsAdminMixin(object):

    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields if field.name != "id"]
        super(ListDisplayAllModelFieldsAdminMixin, self).__init__(model, admin_site)


@admin.register(Category)
class CategoryAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass

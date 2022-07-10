from django.contrib import admin

from .models import Order, OrderLine


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    autocomplete_fields = ("warehouse",)
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ("buyer",)
    inlines = (OrderLineInline,)

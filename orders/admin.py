from django.contrib import admin
from nested_admin.nested import NestedModelAdmin, NestedTabularInline

from .models import Order, OrderLine, OrderLineOffer, PaymentResult


class OrderLineOfferInline(NestedTabularInline):
    model = OrderLineOffer
    extra = 1


class OrderLineInline(NestedTabularInline):
    model = OrderLine
    inlines = (OrderLineOfferInline,)
    autocomplete_fields = ("warehouse",)
    extra = 1


@admin.register(Order)
class OrderAdmin(NestedModelAdmin):
    autocomplete_fields = ("buyer",)
    inlines = (OrderLineInline,)


@admin.register(PaymentResult)
class PaymentResultAdmin(NestedModelAdmin):
    list_display = ("order", "bank_order_id", "amount", "result", "payment_status")

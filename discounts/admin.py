from django.contrib import admin
from django.db.models.expressions import F
from django.utils.translation import gettext as _

from .models import Benefit, BuyerCount, Condition, LoyaltyCard, Offer, Range, Voucher


@admin.register(Range)
class RangeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "includes_all",
    )
    autocomplete_fields = (
        "include_product_units",
        "include_products",
        "include_categories",
        "exclude_product_units",
        "exclude_products",
        "exclude_categories",
    )
    search_fields = ("name",)


class ActiveOfferFilter(admin.SimpleListFilter):
    title = "предложение активно"
    parameter_name = "is_offer_active"

    def lookups(self, request, model_admin):
        return (
            (True, _("Yes")),
            (False, _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        return queryset.filter(offer__is_active=self.value())


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ("id", "is_active", "offer", "is_offer_active")
    list_filter = ("offer", "is_active", ActiveOfferFilter)
    search_fields = ("id",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(is_offer_active=F("offer__is_active"))
        return qs

    def is_offer_active(self, obj):
        return obj.is_offer_active

    is_offer_active.short_description = "предложение активно"
    is_offer_active.boolean = True


@admin.register(LoyaltyCard)
class LoyaltyCardAdmin(admin.ModelAdmin):
    search_fields = ("buyer__name", "buyer_surname", "buyer__fathers_name")


@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    list_display = ("range", "type", "value")


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ("range", "type", "value")


class BuyerCountInline(admin.TabularInline):
    model = BuyerCount
    autocomplete_fields = ("buyer",)
    extra = 1


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "created_at",
        "is_public",
        "is_active",
        "condition",
        "benefit",
    )
    inlines = (BuyerCountInline,)

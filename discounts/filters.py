import django_filters.rest_framework as filters
from django.db.models import Q

from .models import BuyerCount, Offer, Voucher


class OfferFilterSet(filters.FilterSet):
    s = filters.CharFilter(method="search", label="поиск по имени и описанию")
    created = filters.DateTimeFromToRangeFilter(
        field_name="created_at", label="дата создания"
    )
    started = filters.DateTimeFromToRangeFilter(
        field_name="started_at", label="доступно с"
    )
    ended = filters.DateTimeFromToRangeFilter(
        field_name="ended_at", label="доступно до"
    )
    type = filters.ChoiceFilter(choices=Offer.TYPES, label="тип предложения")

    class Meta:
        model = Offer
        fields = ("is_public", "is_active")

    def search(self, qs, name, value):
        return qs.filter(Q(name__icontains=value) | Q(description__icontains=value))


class BuyerCountFilter(filters.FilterSet):
    class Meta:
        model = BuyerCount
        fields = ("buyer",)


class VoucherFilter(filters.FilterSet):
    class Meta:
        model = Voucher
        fields = ("offer",)

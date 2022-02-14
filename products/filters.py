import django_filters
from django.db.models import Q

from .models import Product


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        field_name="category__id", lookup_expr="iexact"
    )
    s = django_filters.CharFilter(
        method="search",
        label="поиск по наименованию, штрихкоду, id",
    )
    is_sorted = django_filters.CharFilter(method="is_sorted_filter")

    class Meta:
        model = Product
        fields = {
            "price": ["lt", "lte", "gt", "gte", "exact"],
            "is_sorted": ["exact"],
            "is_archive": ["exact"],
            "for_own_production": ["exact"],
            "for_scales": ["exact"],
        }

    def search(self, qs, name, value):
        return qs.filter(
            Q(name__icontains=value)
            | Q(barcode__icontains=value)
            | Q(id__icontains=value)
        )

    def is_sorted_filter(self, qs, name, value):
        if value == "all":
            return qs
        elif value == "false":
            return qs.filter(is_sorted=False)
        else:
            return qs.filter(is_sorted=True)

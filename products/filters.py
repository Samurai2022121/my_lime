import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        field_name="category__id", lookup_expr="iexact"
    )

    class Meta:
        model = Product
        fields = {
            "price": ["lt", "lte", "gt", "gte", "exact"],
        }


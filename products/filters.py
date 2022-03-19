import django_filters as filters
from django.db.models import Q
from rest_framework.serializers import BooleanField

from .models import Category, Product, ProductUnit


class ProductFilter(filters.FilterSet):
    category = filters.CharFilter(
        method="in_category_filter",
        label="входит в категорию или её подкатегории (Id категории)",
    )
    s = filters.CharFilter(
        method="search",
        label="поиск по наименованию, ед. изм., Id товара",
    )
    is_sorted = filters.CharFilter(
        method="is_sorted_filter",
        label="ревизован после автоматического ввода",
    )
    is_archive = filters.CharFilter(
        method="is_archived_filter",
        label="в архиве",
    )
    for_resale = filters.BooleanFilter(
        field_name="units__for_resale",
        label="для розничной/мелкооптовой продажи",
    )
    for_scales = filters.BooleanFilter(
        field_name="units__for_scales",
        label="для выгрузки на весы",
    )
    barcode = filters.CharFilter(
        field_name="units__barcode",
        method="exact",
        label="штрихкод",
    )

    class Meta:
        model = Product
        fields = ("own_production",)

    @staticmethod
    def search(qs, name, value):
        return qs.filter(
            Q(name__icontains=value)
            | Q(short_name__icontains=value)
            | Q(unit__name__icontains=value)
            | Q(unit__barcode__icontains=value)
            | Q(id__icontains=value)
        )

    @staticmethod
    def is_sorted_filter(qs, name, value):
        if value == "all":
            return qs

        return qs.filter(**{name: BooleanField().to_representation(value)})

    @staticmethod
    def is_archived_filter(qs, name, value):
        if value == "all":
            return qs

        return qs.filter(**{name: BooleanField().to_representation(value)})

    @staticmethod
    def in_category_filter(qs, name, value):
        try:
            category = Category.objects.get(pk=value)
        except Category.DoesNotExist:
            return qs

        return qs.filter(
            category__in=category.get_descendants(include_self=True),
        )


class ProductUnitFilter(filters.FilterSet):
    class Meta:
        model = ProductUnit
        fields = ("for_resale", "for_scales", "barcode")

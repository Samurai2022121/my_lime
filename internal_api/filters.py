import django_filters
from django.db.models import Q
from haystack.inputs import Clean, Exact
from haystack.query import SearchQuerySet

from products.models import Category, ProductUnit

from . import models


class FullTextFilter(django_filters.CharFilter):
    QUERY_MIN_LENGTH = 2

    def get_search_queryset(self, queryset):
        return SearchQuerySet().models(queryset.model)

    def filter(self, qs, value):
        # the shorter the search term, the longer the list of keys
        if len(value) >= FullTextFilter.QUERY_MIN_LENGTH:
            sqs = self.get_search_queryset(qs)
            # search for all terms
            for term in value.split():
                sqs = sqs.filter(content=Clean(term))
            qs = qs.filter(pk__in=sqs.values_list("pk", flat=True))
        return qs


class WarehouseFullTextFilter(FullTextFilter):
    def get_search_queryset(self, queryset):
        sqs = super().get_search_queryset(queryset)
        # filter by URL parameters (small optimization)
        return sqs.filter(shop=Exact(self.parent.data["shop"]))


class SupplierFilter(django_filters.FilterSet):
    s = FullTextFilter(label="поиск по имени, емейлу и телефону")

    class Meta:
        model = models.Supplier
        fields = {"is_archive": ["exact"]}


class WarehouseOrderFilter(django_filters.FilterSet):
    s = django_filters.CharFilter(
        method="search",
        label="поиск по номеру заказа",
    )

    class Meta:
        model = models.WarehouseOrder
        fields = {"is_archive": ["exact"]}

    def search(self, qs, name, value):
        return qs.filter(Q(number__icontains=value))


class LegalEntityFilterSet(django_filters.FilterSet):

    """Searches through `registration_id` and/or `name` fields."""

    s = FullTextFilter(label="регистрационный номер или наименование")

    class Meta:
        model = models.LegalEntities
        fields = ("s",)


class ShopFilter(django_filters.FilterSet):
    s = FullTextFilter(label="поиск по названию, адресу, id")

    class Meta:
        model = models.Shop
        fields = {"is_archive": ["exact"]}


def warehouse_product_unit_qs(request):
    if request is None:
        return ProductUnit.objects.none()
    qs = ProductUnit.objects.filter(
        warehouses__shop_id=request.query_params.get("shop")
    )
    return qs


class WarehouseFilter(django_filters.FilterSet):
    s = WarehouseFullTextFilter(
        label="поиск по наименованию продукта, штрихкоду продукта, id продукта",
    )
    is_archive = django_filters.BooleanFilter(
        field_name="product_unit__product__is_archive",
        label="показывать архивные запасы",
    )
    is_sorted = django_filters.BooleanFilter(
        field_name="product_unit__product__is_sorted",
        label="показывать неревизованные запасы",
    )
    remaining = django_filters.RangeFilter(
        label="отобрать по количеству на складе",
    )
    category = django_filters.CharFilter(
        method="in_category_filter",
        label="входит в категорию или её подкатегории (Id категории)",
    )
    product_unit = django_filters.ModelMultipleChoiceFilter(
        queryset=warehouse_product_unit_qs,
        label="единицы хранения",
    )
    order_by = django_filters.OrderingFilter(
        fields=(
            ("id", "id"),
            ("product_unit__barcode", "barcode"),
            ("product_unit__product__name", "product_name"),
            ("supplier__name", "supplier_name"),
            ("auto_order", "auto_order"),
            ("price", "price"),
            ("margin", "margin"),
        ),
        field_labels={
            "id": "Warehouse entry id",
            "product_unit__barcode": "Product barcode",
            "product_unit__product__name": "Product name",
            "supplier__name": "Supplier's name",
            "auto_order": "Product auto order status",
            "price": "Price",
            "margin": "Margin",
        },
    )

    class Meta:
        model = models.Warehouse
        fields = ("s",)

    @staticmethod
    def in_category_filter(qs, name, value):
        try:
            category = Category.objects.get(pk=value)
        except Category.DoesNotExist:
            return qs

        return qs.filter(
            product_unit__product__category__in=category.get_descendants(
                include_self=True
            ),
        )


class BatchFilter(django_filters.FilterSet):
    created = django_filters.DateFromToRangeFilter(
        field_name="created_at",
        label="период создания записи",
    )
    expired = django_filters.DateFromToRangeFilter(
        field_name="expiration_date",
        label="период истечения срока годности",
    )
    produced = django_filters.DateFromToRangeFilter(
        field_name="production_date",
        label="период производства",
    )
    shop = django_filters.ModelChoiceFilter(
        field_name="warehouse_records__warehouse__shop",
        queryset=models.Shop.objects.all(),
        label="филиал",
    )
    warehouse = django_filters.ModelChoiceFilter(
        field_name="warehouse_records__warehouse",
        queryset=models.Warehouse.objects.select_related(
            "product_unit__product",
            "product_unit__unit",
            "shop",
        ),
        label="запас",
    )

    class Meta:
        model = models.Batch
        fields = ("supplier",)


class PrimaryDocumentFilter(django_filters.FilterSet):
    created = django_filters.DateFromToRangeFilter(
        field_name="created_at",
        label="период времени",
    )
    number = django_filters.CharFilter(lookup_expr="icontains", label="номер")

    class Meta:
        model = models.PrimaryDocument
        fields = ("created", "number")

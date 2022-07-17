from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.postgres.expressions import ArrayField, ArraySubquery
from django.db.models import BigAutoField, DecimalField, OuterRef, Subquery
from rest_framework import serializers
from rest_framework_nested.serializers import NestedHyperlinkedRelatedField

from discounts.models import LoyaltyCard, Voucher
from internal_api.models import Warehouse
from products.models import ProductUnit
from utils.models_utils import build_offer_subquery


class BasketOfferSerializer(serializers.Serializer):
    offer = serializers.HyperlinkedRelatedField(
        view_name="discounts:offer-detail",
        label="скидка",
        read_only=True,
        lookup_url_kwarg="id",
    )
    apply_times = serializers.IntegerField(label="число применений")


class ProductUnitFieldMixin:
    def get_queryset(self):
        if self.queryset is None:
            view = self.context["view"]
            offer_qs = view.offer_queryset
            warehouse_qs = Warehouse.objects.filter(
                shop_id=view.kwargs["shop_id"],
                product_unit_id=OuterRef("pk"),
            )

            self.queryset = ProductUnit.objects.filter(
                product__is_archive=False,
            ).annotate(
                full_price=Subquery(
                    warehouse_qs.values("price"),
                    output_field=DecimalField("цена", decimal_places=2, max_digits=6),
                ),
                cond_range=ArraySubquery(
                    build_offer_subquery(offer_qs, "condition").values("pk"),
                    output_field=ArrayField(BigAutoField, verbose_name="предложения"),
                ),
            )
        return self.queryset


class ProductUnitField(ProductUnitFieldMixin, serializers.PrimaryKeyRelatedField):
    pass


class ProductUnitDisplayField(ProductUnitFieldMixin, NestedHyperlinkedRelatedField):
    pass


class BasketLineSerializer(serializers.Serializer):
    product_unit = ProductUnitField(
        label="единица хранения",
        write_only=True,
    )
    product_unit_on_read = ProductUnitDisplayField(
        label="единица хранения",
        view_name="products:productunit-detail",
        lookup_url_kwarg="id",
        parent_lookup_kwargs={"product_id": "product__pk"},
        read_only=True,
        source="product_unit",
    )
    quantity = serializers.DecimalField(
        label="количество в складских единицах",
        max_digits=8,
        decimal_places=3,
        min_value=Decimal("0.001"),
    )
    full_price = serializers.DecimalField(
        label="полная цена",
        max_digits=9,
        decimal_places=2,
        min_value=Decimal("0.0"),
        read_only=True,
        allow_null=True,
    )
    discounted_price = serializers.DecimalField(
        label="цена со скидками",
        max_digits=9,
        decimal_places=2,
        min_value=Decimal("0.0"),
        read_only=True,
        allow_null=True,
    )
    offers = BasketOfferSerializer(
        label="скидки",
        many=True,
        read_only=True,
    )
    warehouse = NestedHyperlinkedRelatedField(
        label="запас",
        view_name="internal_api:warehouse-detail",
        parent_lookup_kwargs={"shop_id": "shop__pk"},
        lookup_url_kwarg="id",
        read_only=True,
        allow_null=True,
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["product_unit"] = data.pop("product_unit_on_read", None)
        return data


class BasketSerializer(serializers.Serializer):
    lines = BasketLineSerializer(label="строки", many=True)
    buyer = serializers.PrimaryKeyRelatedField(
        label="покупатель",
        queryset=get_user_model().objects.all(),
        required=False,
        allow_null=True,
    )
    card = serializers.PrimaryKeyRelatedField(
        label="программа лояльности",
        queryset=LoyaltyCard.objects.all(),
        required=False,
        allow_null=True,
    )
    vouchers = serializers.PrimaryKeyRelatedField(
        many=True,
        label="ваучеры",
        queryset=Voucher.objects.all(),
        required=False,
        allow_empty=True,
    )

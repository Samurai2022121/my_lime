from datetime import datetime, timedelta
from typing import Sequence

from croniter import croniter
from django.contrib.auth import get_user_model
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_nested.serializers import NestedHyperlinkedRelatedField

from products.models import Category, Product, ProductUnit
from utils.models_utils import phone_regex

from .models import Benefit, BuyerCount, Condition, LoyaltyCard, Offer, Range, Voucher


class ConditionSerializer(serializers.ModelSerializer):
    range_on_read = serializers.HyperlinkedRelatedField(
        label="диапазоны товаров",
        lookup_field="id",
        source="range",
        read_only=True,
        view_name="discounts:range-detail",
    )
    range = serializers.PrimaryKeyRelatedField(
        label="диапазоны товаров",
        queryset=Range.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Condition
        exclude = ("id",)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["range"] = data.pop("range_on_read")
        return data


class BenefitSerializer(serializers.ModelSerializer):
    range_on_read = serializers.HyperlinkedRelatedField(
        label="диапазоны товаров",
        lookup_field="id",
        source="range",
        read_only=True,
        view_name="discounts:range-detail",
    )
    range = serializers.PrimaryKeyRelatedField(
        label="диапазоны товаров",
        queryset=Range.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Benefit
        exclude = ("id",)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["range"] = data.pop("range_on_read")
        return data


def crontab_string(value):
    if not croniter.is_valid(value):
        raise ValidationError(f"“{value}” is not a valid crontab expression.")


def datetime_range(value):
    started_at = value.get("started_at", datetime.min)
    ended_at = value.get("ended_at", datetime.max)
    if started_at >= ended_at:
        raise ValidationError(f"Invalid {started_at}:{ended_at} range.")


def schedule_duration(value):
    if value.get("schedule") and value.get("duration", timedelta()) < timedelta(
        seconds=1
    ):
        raise ValidationError("Duration is too short.")


class OfferSerializer(WritableNestedModelSerializer):
    condition = ConditionSerializer()
    benefit = BenefitSerializer()

    class Meta:
        model = Offer
        fields = "__all__"
        extra_kwargs = {
            "schedule": {
                "validators": [crontab_string],
            },
        }
        validators = [datetime_range, schedule_duration]

    def is_valid(self, raise_exception=False):
        return super().is_valid(raise_exception)


class BuyerCountSerializer(serializers.ModelSerializer):
    buyer_on_read = serializers.HyperlinkedRelatedField(
        label="покупатель",
        lookup_field="id",
        read_only=True,
        source="buyer",
        view_name="users:user-detail",
    )
    buyer = serializers.PrimaryKeyRelatedField(
        label="покупатель",
        queryset=get_user_model().objects.all(),
        write_only=True,
    )

    class Meta:
        model = BuyerCount
        exclude = ("offer",)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["buyer"] = data.pop("buyer_on_read")
        return data


class RangeSerializer(serializers.ModelSerializer):
    include_product_units_on_read = NestedHyperlinkedRelatedField(
        allow_null=True,
        label="действует на товарные единицы",
        many=True,
        lookup_field="id",
        parent_lookup_kwargs={"product_id": "product__id"},
        source="include_product_units",
        read_only=True,
        view_name="products:productunit-detail",
    )
    include_product_units = serializers.PrimaryKeyRelatedField(
        allow_empty=True,
        allow_null=True,
        label="действует на товарные единицы",
        many=True,
        required=False,
        queryset=ProductUnit.objects.all(),
        write_only=True,
    )
    include_products_on_read = serializers.HyperlinkedRelatedField(
        allow_null=True,
        label="действует на товары",
        lookup_field="id",
        many=True,
        source="include_products",
        read_only=True,
        view_name="products:product-detail",
    )
    include_products = serializers.PrimaryKeyRelatedField(
        allow_empty=True,
        allow_null=True,
        label="действует на товары",
        many=True,
        required=False,
        queryset=Product.objects.all(),
        write_only=True,
    )
    include_categories_on_read = serializers.HyperlinkedRelatedField(
        allow_null=True,
        label="действует на категории товаров",
        lookup_field="id",
        many=True,
        source="include_categories",
        read_only=True,
        view_name="products:category-detail",
    )
    include_categories = serializers.PrimaryKeyRelatedField(
        allow_empty=True,
        allow_null=True,
        label="действует на категории товаров",
        many=True,
        required=False,
        queryset=Category.objects.all(),
        write_only=True,
    )
    exclude_product_units_on_read = NestedHyperlinkedRelatedField(
        allow_null=True,
        label="не действует на товарные единицы",
        lookup_field="id",
        many=True,
        parent_lookup_kwargs={"product_id": "product__id"},
        source="exclude_product_units",
        read_only=True,
        view_name="products:productunit-detail",
    )
    exclude_product_units = serializers.PrimaryKeyRelatedField(
        allow_empty=True,
        allow_null=True,
        label="не действует на товарные единицы",
        many=True,
        required=False,
        queryset=ProductUnit.objects.all(),
        write_only=True,
    )
    exclude_products_on_read = serializers.HyperlinkedRelatedField(
        allow_null=True,
        label="не действует на товары",
        lookup_field="id",
        many=True,
        source="exclude_products",
        read_only=True,
        view_name="products:product-detail",
    )
    exclude_products = serializers.PrimaryKeyRelatedField(
        allow_empty=True,
        allow_null=True,
        label="не действует на товары",
        many=True,
        required=False,
        queryset=Product.objects.all(),
        write_only=True,
    )
    exclude_categories_on_read = serializers.HyperlinkedRelatedField(
        allow_null=True,
        label="не действует на категории товаров",
        lookup_field="id",
        many=True,
        source="exclude_categories",
        read_only=True,
        view_name="products:category-detail",
    )
    exclude_categories = serializers.PrimaryKeyRelatedField(
        allow_empty=True,
        allow_null=True,
        label="не действует на категории товаров",
        many=True,
        required=False,
        queryset=Category.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Range
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field_name in (
            "include_product_units",
            "include_products",
            "include_categories",
            "exclude_product_units",
            "exclude_products",
            "exclude_categories",
        ):
            data[field_name] = data.pop(f"{field_name}_on_read", None)
        return data


class OfferTypeValidator:
    def __init__(self, offer_types: Sequence):
        self.offer_types = offer_types

    def __call__(self, value):
        if value.type not in self.offer_types:
            raise ValidationError(f"Wrong offer type: {value.type}.")


class VoucherSerializer(serializers.ModelSerializer):
    offer_on_read = serializers.HyperlinkedRelatedField(
        label="предложение",
        lookup_field="id",
        read_only=True,
        source="offer",
        view_name="discounts:offer-detail",
    )
    offer = serializers.PrimaryKeyRelatedField(
        label="предложение",
        queryset=Offer.objects.all(),
        validators=[OfferTypeValidator(offer_types=(Offer.TYPES.voucher,))],
        write_only=True,
    )

    class Meta:
        model = Voucher
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["offer"] = data.pop("offer_on_read")
        return data


class LoyaltyCardSerializer(serializers.ModelSerializer):
    buyer_on_read = serializers.HyperlinkedRelatedField(
        label="покупатель",
        lookup_field="id",
        read_only=True,
        source="buyer",
        view_name="users:user-detail",
    )
    buyer = serializers.PrimaryKeyRelatedField(
        label="покупатель",
        queryset=get_user_model().objects.all(),
        write_only=True,
    )
    offer_on_read = serializers.HyperlinkedRelatedField(
        label="предложение",
        lookup_field="id",
        read_only=True,
        source="offer",
        view_name="discounts:offer-detail",
    )
    offer = serializers.PrimaryKeyRelatedField(
        label="предложение",
        queryset=Offer.objects.all(),
        validators=[OfferTypeValidator(offer_types=(Offer.TYPES.loyalty,))],
        write_only=True,
    )

    class Meta:
        model = LoyaltyCard
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["offer"] = data.pop("offer_on_read")
        data["buyer"] = data.pop("buyer_on_read")
        return data


class OfferApplySerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        label="номер телефона покупателя",
        max_length=17,
        required=False,
        validators=(phone_regex,),
    )

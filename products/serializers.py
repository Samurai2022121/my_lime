from django.contrib.contenttypes.models import ContentType
from django.core.validators import FileExtensionValidator
from django.db.models import Avg
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework_nested.serializers import NestedHyperlinkedIdentityField

from reviews.models import Favourite, Star
from utils.models_utils import Round

from .models import (
    Category,
    MeasurementUnit,
    Product,
    ProductImages,
    ProductUnit,
    ProductUnitConversion,
)


class CategoryListSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "description", "children", "image"]

    def get_children(self, obj):
        serializer = CategoryListSerializer(instance=obj.get_children(), many=True)
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()
    parent_id = serializers.CharField(write_only=True, required=False)
    image = serializers.FileField(
        write_only=True,
        validators=[FileExtensionValidator(["svg", "png", "jpg"])],
        required=False,
    )

    class Meta:
        model = Category
        fields = ["id", "name", "parent", "parent_id", "image"]

    def get_parent(self, obj):
        # do not show empty root parent
        if obj.parent:
            serializer = CategorySerializer(instance=obj.parent)
            return serializer.data

    def create(self, validated_data):
        parent_category_id = validated_data.pop("parent_id", None)
        if parent_category_id:
            parent_category = Category.objects.get(id=parent_category_id)
            category = Category.objects.create(parent=parent_category, **validated_data)
        else:
            category = Category.objects.create(**validated_data)
        return category

    def update(self, instance, validated_data):
        parent_category_id = validated_data.pop("parent_id", None)
        parent_category = None
        if parent_category_id:
            parent_category = Category.objects.get(id=parent_category_id)
        validated_data.update({"parent": parent_category})
        instance = super().update(instance, validated_data)
        return instance


class EditProductImagesSerializer(serializers.ModelSerializer):
    image_1000 = Base64ImageField(required=True)

    class Meta:
        model = ProductImages
        fields = ("id", "image_1000", "main", "description", "product")


class BulkEditProductImagesSerializer(serializers.Serializer):
    images = EditProductImagesSerializer(many=True)

    class Meta:
        fields = ("images",)


class BulkUpdateProductImagesSerializer(serializers.Serializer):
    instances = serializers.ListField(child=serializers.JSONField(), required=True)
    product = serializers.IntegerField(required=True)


class ProductImagesSerializer(serializers.ModelSerializer):
    image_1000 = Base64ImageField()

    class Meta:
        model = ProductImages
        fields = ("id", "image_1000", "image_500", "image_150", "main", "description")


class MeasurementUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementUnit
        fields = "__all__"


class ProductUnitSerializer(serializers.ModelSerializer):
    unit = serializers.SlugRelatedField(
        slug_field="name",
        queryset=MeasurementUnit.objects,
    )
    product = serializers.HyperlinkedIdentityField(
        view_name="products:product-detail",
        read_only=True,
        lookup_field="product_id",
        lookup_url_kwarg="id",
    )
    conversion_sources = NestedHyperlinkedIdentityField(
        view_name="products:sources-list",
        read_only=True,
        lookup_url_kwarg="unit_id",
        lookup_field="id",
        parent_lookup_kwargs={
            "product_id": "product__id",
        },
    )
    conversion_targets = NestedHyperlinkedIdentityField(
        view_name="products:targets-list",
        read_only=True,
        lookup_url_kwarg="unit_id",
        lookup_field="id",
        parent_lookup_kwargs={
            "product_id": "product__id",
        },
    )

    class Meta:
        model = ProductUnit
        fields = "__all__"


class ConversionSourceSerializer(serializers.ModelSerializer):
    target_unit = NestedHyperlinkedIdentityField(
        view_name="products:productunit-detail",
        read_only=True,
        lookup_field="target_unit_id",
        lookup_url_kwarg="id",
        parent_lookup_kwargs={
            "product_id": "target_unit__product__id",
        },
    )

    class Meta:
        model = ProductUnitConversion
        fields = "__all__"


class ConversionTargetSerializer(serializers.ModelSerializer):
    source_unit = NestedHyperlinkedIdentityField(
        view_name="products:productunit-detail",
        read_only=True,
        lookup_field="source_unit_id",
        lookup_url_kwarg="id",
        parent_lookup_kwargs={
            "product_id": "target_unit__product__id",
        },
    )

    class Meta:
        model = ProductUnitConversion
        fields = "__all__"


class ProductListAdminSerializer(serializers.ModelSerializer):
    units = ProductUnitSerializer(many=True)
    category = CategorySerializer()
    images = ProductImagesSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = "__all__"


class ProductListSerializer(serializers.ModelSerializer):
    units = serializers.HyperlinkedIdentityField(
        view_name="products:productunit-list",
        lookup_url_kwarg="product_id",
    )
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()
    average_star = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    favourite_count = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()
    category = CategorySerializer()
    images = ProductImagesSerializer(many=True, required=False)

    class Meta:
        model = Product
        exclude = ["is_archive", "is_sorted"]

    def get_stars_count(self, obj):
        return Star.objects.filter(
            content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
        ).count()

    def get_average_star(self, obj):
        return Star.objects.filter(
            content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
        ).aggregate(value=Round(Avg("mark")))["value"]

    def get_stared(self, obj):
        user = self.context["request"].user
        return (
            user.is_authenticated
            and Star.objects.filter(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id,
                user=user,
            ).exists()
        )

    def get_favourite_count(self, obj):
        return Favourite.objects.filter(
            content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
        ).count()

    def get_is_favourite(self, obj):
        user = self.context["request"].user
        return (
            user.is_authenticated
            and Favourite.objects.filter(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id,
                user=user,
            ).exists()
        )

    def get_discounted_price(self, obj):
        return (
            round((obj.price * (1 - obj.discount / 100)), 2) if obj.discount else None
        )


class ProductSerializer(serializers.ModelSerializer):
    units = serializers.HyperlinkedIdentityField(
        view_name="products:productunit-list",
        lookup_url_kwarg="product_id",
    )
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()
    average_star = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    favourite_count = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()
    category_read = CategorySerializer(read_only=True, source="category")
    images = ProductImagesSerializer(many=True, required=False)

    class Meta:
        model = Product
        exclude = ["is_archive", "is_sorted"]

    def get_average_star(self, obj):
        return Star.objects.filter(
            content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
        ).aggregate(value=Round(Avg("mark")))["value"]

    def get_stars_count(self, obj):
        return Star.objects.filter(
            content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
        ).count()

    def get_stared(self, obj):
        user = self.context["request"].user
        return (
            user.is_authenticated
            and Star.objects.filter(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id,
                user=user,
            ).exists()
        )

    def get_reviews(self, obj):
        return Star.objects.filter(
            content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
        ).values("review", "mark", "created_at", "user__name")

    def get_favourite_count(self, obj):
        return Favourite.objects.filter(
            content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
        ).count()

    def get_is_favourite(self, obj):
        user = self.context["request"].user
        return (
            user.is_authenticated
            and Favourite.objects.filter(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id,
                user=user,
            ).exists()
        )

    def get_discounted_price(self, obj):
        return (
            round((obj.price * (1 - obj.discount / 100)), 2) if obj.discount else None
        )


class ProductAdminSerializer(serializers.ModelSerializer):
    units = ProductUnitSerializer(many=True, read_only=True)
    category_read = CategorySerializer(read_only=True, source="category")
    images = ProductImagesSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = "__all__"

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result["category"] = result.pop("category_read")
        return result

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        product = Product.objects.create(**validated_data)

        for image in images_data:
            ProductImages.objects.create(product=product, **image)
        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images", [])

        for image_obj in images_data:
            image_id = image_obj.get("id", "")
            if image_id:
                ProductImages.objects.filter(id=image_id).update(**image_obj)
            else:
                ProductImages.objects.create(product=instance, **image_obj)
        super().update(instance, validated_data)
        return instance

    def validate(self, data):
        for_scales = data.get("for_scales")
        short_name = data.get("short_name")
        category = data.get("category")

        if for_scales and not short_name:
            raise serializers.ValidationError("Введите short_name.")

        if for_scales and not category:
            raise serializers.ValidationError("Введите category.")

        return data


class SimpleProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        exclude = ("is_archive", "is_sorted")


class SimpleProductUnitSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)
    unit = serializers.CharField(read_only=True, source="unit.name")

    class Meta:
        model = ProductUnit
        fields = "__all__"


class BulkActionProductSerializer(serializers.Serializer):
    product_ids = serializers.ListField(child=serializers.IntegerField(), required=True)


class BulkChangeProductCategorySerializer(BulkActionProductSerializer):
    new_category = serializers.IntegerField(required=True)


class BulkActionProductImageSerializer(serializers.Serializer):
    image_ids = serializers.ListField(child=serializers.IntegerField(), required=True)

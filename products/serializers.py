from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg
from rest_framework import serializers

from reviews.models import Star, Favourite
from utils.models_utils import Round
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductListSerializer(serializers.ModelSerializer):
    image_150 = serializers.ImageField(source="images.image_150")
    image_1000 = serializers.ImageField(source="images.image_1000")
    image_500 = serializers.ImageField(source="images.image_500")
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()
    average_star = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    favourite_count = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'main_image', 'in_stock', 'id',
                  'stars_count', 'stared', 'average_star', 'is_favourite',
                  'favourite_count', 'discount', 'discounted_price', 'image_150',
                  'image_500', 'image_1000']

    def get_category(self, obj):
        return obj.category.get_ancestors(include_self=True).values('id', 'name')

    def get_stars_count(self, obj):
        return Star.objects.filter(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id).count()

    def get_average_star(self, obj):
        return Star.objects.filter(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
                                   ).aggregate(value=Round(Avg('mark')))['value']

    def get_stared(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and Star.objects.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            user=user
        ).exists()

    def get_favourite_count(self, obj):
        return Favourite.objects.filter(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id).count()

    def get_is_favourite(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and Favourite.objects.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            user=user
        ).exists()

    def get_discounted_price(self, obj):
        return round((obj.price * (1 - obj.discount/100)), 2) if obj.discount else None


class ProductSerializer(serializers.ModelSerializer):
    image_1000 = serializers.ImageField(source="images.image_1000")
    image_500 = serializers.ImageField(source="images.image_500")
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()
    average_star = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    favourite_count = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'creation_date', 'images', 'protein',
                  'carbohydrates', 'fats', 'calories', 'barcode', 'manufacturer', 'origin',
                  'expiration_date', 'weight', 'in_stock', 'id', 'stars_count', 'stared',
                  'average_star', 'is_favourite', 'favourite_count', 'category', 'main_image',
                  'discount', 'discounted_price', 'image_500', 'image_1000']

    def get_category(self, obj):
        return obj.category.get_ancestors(include_self=True).values('id', 'name')

    def get_average_star(self, obj):
        return Star.objects.filter(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
                                   ).aggregate(value=Round(Avg('mark')))['value']

    def get_stars_count(self, obj):
        return Star.objects.filter(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id).count()

    def get_stared(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and Star.objects.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            user=user
        ).exists()

    def get_favourite_count(self, obj):
        return Favourite.objects.filter(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id).count()

    def get_is_favourite(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and Favourite.objects.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            user=user
        ).exists()

    def get_discounted_price(self, obj):
        return round((obj.price * (1 - obj.discount/100)), 2) if obj.discount else None

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from reviews.models import Star
from .models import Category, Product, Subcategory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = '__all__'


class ProductListSerializer(serializers.ModelSerializer):
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()
    subcategory = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['name', 'subcategory', 'price', 'image', 'in_stock',
                  'stars_count', 'stared', 'category', 'subcategory']

    def get_stars_count(self, obj):
        return Star.objects.filter(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id).count()

    def get_stared(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and Star.objects.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            user=user
        ).exists()

    def get_subcategory(self, obj):
        return {'id': obj.subcategory.id, 'name': obj.subcategory.name}

    def get_category(self, obj):
        return Category.objects.filter(subcategories=obj.subcategory).values_list('id', 'name')


class ProductSerializer(serializers.ModelSerializer):
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()
    subcategory = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'creation_date', 'image', 'protein',
                  'carbohydrates', 'fats', 'calories', 'barcode', 'manufacturer', 'origin',
                  'expiration_date', 'weight', 'in_stock', 'stars_count', 'stared',
                  'subcategory', 'category']

    def get_stars_count(self, obj):
        return Star.objects.filter(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id).count()

    def get_stared(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and Star.objects.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            user=user
        ).exists()

    def get_subcategory(self, obj):
        return {'id': obj.subcategory.id, 'name': obj.subcategory.name}

    def get_category(self, obj):
        return Category.objects.filter(subcategories=obj.subcategory).values_list('id', 'name')

from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

from reviews.models import Star
from .models import Recipe, RecipeCategory


class RecipeCategorySerializer(serializers.ModelSerializer):
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()

    class Meta:
        model = RecipeCategory
        fields = '__all__'


class RecipeListSerializer(serializers.ModelSerializer):
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    recipe_category = serializers.SerializerMethodField()
    ingredients_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ['protein', 'carbohydrates', 'fats', 'calories']

    def get_stars_count(self, obj):
        return Star.objects.filter(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id).count()

    def get_stared(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and Star.objects.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            user=user
        ).exists()

    def get_author(self, obj):
        return {'id': obj.author.id, 'name': obj.author.name}

    def get_recipe_category(self, obj):
        return {'id': obj.recipe_category.id, 'name': obj.recipe_category.name}

    def get_ingredients_in_stock(self, obj):
        return obj.ingredients_in_stock.values_list('id', 'name')


class RecipeSerializer(serializers.ModelSerializer):
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    recipe_category = serializers.SerializerMethodField()
    ingredients_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_stars_count(self, obj):
        return Star.objects.filter(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id).count()

    def get_stared(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and Star.objects.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            user=user
        ).exists()

    def get_author(self, obj):
        return {'id': obj.author.id, 'name': obj.author.name}

    def get_recipe_category(self, obj):
        return {'id': obj.recipe_category.id, 'name': obj.recipe_category.name}

    def get_ingredients_in_stock(self, obj):
        return obj.ingredients_in_stock.values_list('id', 'name')

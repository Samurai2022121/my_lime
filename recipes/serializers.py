from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg

from reviews.models import Star, Favourite
from utils.models_utils import Round
from .models import Recipe, RecipeCategory


class RecipeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeCategory
        fields = '__all__'


class RecipeListSerializer(serializers.ModelSerializer):
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    recipe_category = serializers.SerializerMethodField()
    ingredients_in_stock = serializers.SerializerMethodField()
    average_star = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    favourite_count = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ['protein', 'carbohydrates', 'fats', 'calories',  'average_star',
                   'is_favourite', 'favourite_count']

    def get_stars_count(self, obj):
        return Star.objects.filter(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id).count()

    def get_stared(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and Star.objects.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            user=user
        ).exists()

    def get_average_star(self, obj):
        return Star.objects.filter(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
                                   ).aggregate(value=Round(Avg('mark')))['value']

    def get_author(self, obj):
        return {'id': obj.author.id, 'name': obj.author.name}

    def get_recipe_category(self, obj):
        return {'id': obj.recipe_category.id, 'name': obj.recipe_category.name}

    def get_ingredients_in_stock(self, obj):
        return obj.ingredients_in_stock.values_list('id', 'name')

    def get_favourite_count(self, obj):
        return Favourite.objects.filter(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id).count()

    def get_is_favourite(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and Favourite.objects.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            user=user
        ).exists()


class RecipeSerializer(serializers.ModelSerializer):
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    recipe_category = serializers.SerializerMethodField()
    ingredients_in_stock = serializers.SerializerMethodField()
    average_star = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    favourite_count = serializers.SerializerMethodField()

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

    def get_average_star(self, obj):
        return Star.objects.filter(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
                                   ).aggregate(value=Round(Avg('mark')))['value']

    def get_author(self, obj):
        return {'id': obj.author.id, 'name': obj.author.name}

    def get_recipe_category(self, obj):
        return {'id': obj.recipe_category.id, 'name': obj.recipe_category.name}

    def get_ingredients_in_stock(self, obj):
        return obj.ingredients_in_stock.values_list('id', 'name')

    def get_favourite_count(self, obj):
        return Favourite.objects.filter(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id).count()

    def get_is_favourite(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and Favourite.objects.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            user=user
        ).exists()

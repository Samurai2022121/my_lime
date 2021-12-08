from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg
from rest_framework import serializers

from reviews.models import Favourite, Star
from utils.models_utils import Round

from .models import Recipe, RecipeCategory


class RecipeCategoryListSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = RecipeCategory
        fields = ["id", "name", "description", "children", "image"]

    def get_children(self, obj):
        serializer = RecipeCategoryListSerializer(
            instance=obj.get_children(), many=True
        )
        return serializer.data


class RecipeCategorySerializer(serializers.ModelSerializer):
    parents = serializers.SerializerMethodField()

    class Meta:
        model = RecipeCategory
        fields = ["id", "name", "parents"]

    def get_parents(self, obj):
        serializer = RecipeCategorySerializer(instance=obj.parent)
        return serializer.data


class RecipeListSerializer(serializers.ModelSerializer):
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    recipe_category = RecipeCategorySerializer()
    ingredients_in_stock = serializers.SerializerMethodField()
    average_star = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    favourite_count = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = [
            "protein",
            "carbohydrates",
            "fats",
            "calories",
            "video",
            "cooking_steps",
        ]

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

    def get_average_star(self, obj):
        return Star.objects.filter(
            content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
        ).aggregate(value=Round(Avg("mark")))["value"]

    def get_author(self, obj):
        return {"id": obj.author.id, "name": obj.author.name}

    def get_ingredients_in_stock(self, obj):
        return obj.recipe_products.values("product", "quantity")

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


class RecipeSerializer(serializers.ModelSerializer):
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    recipe_category = RecipeCategorySerializer()
    ingredients_in_stock = serializers.SerializerMethodField()
    average_star = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    favourite_count = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = "__all__"

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

    def get_average_star(self, obj):
        return Star.objects.filter(
            content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
        ).aggregate(value=Round(Avg("mark")))["value"]

    def get_author(self, obj):
        return {"id": obj.author.id, "name": obj.author.name}

    def get_ingredients_in_stock(self, obj):
        return obj.recipe_products.values("product", "quantity")

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

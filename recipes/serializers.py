from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, F
from rest_framework import serializers

from reviews.models import Favourite, Star
from utils.models_utils import Round

from .models import Recipe, RecipeCategory, RecipeCookingSteps


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
            "is_archive",
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


class RecipeListAdminSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    recipe_category = RecipeCategorySerializer()
    ingredients_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = "__all__"

    def get_author(self, obj):
        return {"id": obj.author.id, "name": obj.author.name}

    def get_ingredients_in_stock(self, obj):
        return obj.recipe_products.values("product", "quantity")


class RecipeCookingStepsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeCookingSteps
        fields = "__all__"


class RecipeAdminSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    recipe_category = RecipeCategorySerializer(read_only=True)
    recipe_category_id = serializers.IntegerField(write_only=True, required=True)
    ingredients_in_stock = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    recipe_steps = RecipeCookingStepsSerializer(many=True)

    class Meta:
        model = Recipe
        fields = "__all__"

    def create(self, validated_data):
        user = self.context["request"].user.id
        recipe_category_id = validated_data.pop("recipe_category_id")
        recipe_steps = validated_data.pop("recipe_steps")
        category = RecipeCategory.objects.get(id=recipe_category_id)
        validated_data.update({"recipe_category": category, "author_id": user})
        recipe = Recipe.objects.create(**validated_data)
        for step in recipe_steps:
            RecipeCookingSteps.objects.create(recipe=recipe, **step)
        return recipe

    def update(self, instance, validated_data):
        recipe_steps = validated_data.pop("recipe_steps", [])
        recipe_category_id = validated_data.pop("recipe_category_id", "")
        category = RecipeCategory.objects.get(id=recipe_category_id)
        validated_data.update({"recipe_category": category})
        instance = super().update(instance, validated_data)
        for step in recipe_steps:
            step_id = step.get("id", "")
            if step_id:
                RecipeCookingSteps.objects.get(id=step_id).update(**step)
            else:
                RecipeCookingSteps.objects.create(recipe=instance, **step)
        return instance

    def get_reviews(self, obj):
        return (
            Star.objects.filter(
                content_type=ContentType.objects.get_for_model(obj), object_id=obj.id
            )
            .annotate(username=F("user__name"))
            .values("review", "mark", "created_at", "username")
        )

    def get_author(self, obj):
        return {"id": obj.author.id, "name": obj.author.name}

    def get_ingredients_in_stock(self, obj):
        return obj.recipe_products.values("product", "quantity")


class RecipeSerializer(RecipeAdminSerializer):
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()
    average_star = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    favourite_count = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ["is_archive"]

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

from rest_framework import serializers

from .models import Recipe, RecipeCategory


class RecipeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeCategory
        fields = '__all__'


class RecipeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        exclude = ['protein', 'carbohydrates', 'fats', 'calories']


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'

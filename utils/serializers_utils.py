from rest_framework import serializers

from news.models import News
from products.models import Product
from recipes.models import Recipe

CONTENT_TYPES = dict(PD=Product, RP=Recipe, NW=News)


class BulkUpdateSerializer(serializers.Serializer):
    instances = serializers.ListField(child=serializers.JSONField(), required=True)

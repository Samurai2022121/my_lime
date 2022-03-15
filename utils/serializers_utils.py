from typing import Type

from rest_framework import serializers

from news.models import News
from products.models import Product
from recipes.models import Recipe

CONTENT_TYPES = dict(PD=Product, RP=Recipe, NW=News)


class BulkUpdateSerializer(serializers.Serializer):
    instances = serializers.ListField(child=serializers.JSONField(), required=True)


class BulkActionSerializer(serializers.Serializer):
    instances = serializers.ListField(child=serializers.IntegerField(), required=True)


def exclude_field(
    serializer: Type[serializers.Serializer],
    field: str,
) -> Type[serializers.Serializer]:
    """Exclude field from serializer. Optional chaining."""
    fields = getattr(serializer.Meta, "fields", None)
    if fields == "__all__":
        del serializer.Meta.fields
        serializer.Meta.exclude = [field]
    elif fields is None:
        serializer.Meta.exclude.append(field)
        serializer.Meta.exclude = list(set(serializer.Meta.exclude))
    else:
        serializer.Meta.fields.remove(field)
    return serializer

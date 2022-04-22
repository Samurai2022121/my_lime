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
    serializer_class: Type[serializers.Serializer],
    field: str,
) -> Type:
    """Exclude field from serializer class."""
    new_class = type(
        serializer_class.__name__,
        serializer_class.__bases__,
        dict(serializer_class.__dict__),
    )
    new_class.Meta = type(
        serializer_class.Meta.__name__,
        serializer_class.Meta.__bases__,
        dict(serializer_class.Meta.__dict__),
    )
    fields = getattr(new_class.Meta, "fields", None)
    if fields == "__all__":
        del new_class.Meta.fields
        new_class.Meta.exclude = [field]
    elif fields is None:
        new_class.Meta.exclude.append(field)
        new_class.Meta.exclude = list(set(new_class.Meta.exclude))
    else:
        new_class.Meta.fields.remove(field)
    return new_class

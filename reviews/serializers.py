from rest_framework import serializers

from utils.serializers_utils import CONTENT_TYPES as content_types
from .models import Star


class StarSerializer(serializers.Serializer):
    content_type = serializers.CharField(write_only=True)
    id = serializers.IntegerField(write_only=True)

    def create(self, validated_data):
        content_type = validated_data.get("content_type")
        content_model = content_types[content_type].objects.get(id=validated_data.get("id"))
        star = Star.objects.create(
            content_object=content_model,
            user=self.context["request"].user
        )
        return star

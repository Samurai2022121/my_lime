from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from reviews.models import Star

from .models import News, Section


class NewsSerializer(serializers.ModelSerializer):
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = "__all__"

    def create(self, validated_data):
        user = self.context["request"].user.id
        validated_data.update({"author_id": user})
        recipe = News.objects.create(**validated_data)
        return recipe

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

    def get_author(self, obj):
        return {"id": obj.author.id, "name": obj.author.name}


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = "__all__"


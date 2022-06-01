from django.contrib.contenttypes.models import ContentType
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from reviews.models import Star
from utils.serializers_utils import AuthorMixin

from .models import News, NewsParagraphs, NewsParagraphsImages, Section


class NewsParagraphsImagesSerializer(
    WritableNestedModelSerializer, serializers.ModelSerializer
):
    class Meta:
        model = NewsParagraphsImages
        fields = "__all__"


class NewsParagraphsSerializer(
    WritableNestedModelSerializer, serializers.ModelSerializer
):
    news_paragraps_images = NewsParagraphsImagesSerializer(many=True)

    class Meta:
        model = NewsParagraphs
        fields = "__all__"


class NewsSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    news_paragraphs = NewsParagraphsSerializer(many=True)

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


class NewsAdminSerializer(AuthorMixin, serializers.ModelSerializer):
    author_on_read = serializers.SerializerMethodField(source="author", read_only=True)
    news_paragraphs = NewsParagraphsSerializer(many=True)

    class Meta:
        model = News
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["author"] = data.pop("author_on_read", None)
        return data

    def get_author_on_read(self, obj):
        return {"id": obj.author.id, "name": obj.author.name}


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = "__all__"

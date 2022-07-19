from django.contrib.contenttypes.models import ContentType
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from reviews.models import Star
from utils.serializers_utils import AuthorMixin

from .models import Article, ArticleParagraph, ArticleParagraphImage, Section


class ArticleParagraphImageSerializer(
    WritableNestedModelSerializer, serializers.ModelSerializer
):
    class Meta:
        model = ArticleParagraphImage
        fields = "__all__"


class ArticleParagraphSerializer(
    WritableNestedModelSerializer, serializers.ModelSerializer
):
    news_paragraphs_images = ArticleParagraphImageSerializer(many=True)

    class Meta:
        model = ArticleParagraph
        fields = "__all__"


class ArticleSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    stars_count = serializers.SerializerMethodField()
    stared = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    news_paragraphs = ArticleParagraphSerializer(many=True)

    class Meta:
        model = Article
        fields = "__all__"

    def create(self, validated_data):
        user = self.context["request"].user.id
        validated_data.update({"author_id": user})
        recipe = Article.objects.create(**validated_data)
        return recipe

    def get_stars_count(self, obj):
        print("get_stars_count")
        print(ContentType.objects.get_for_model(obj))
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


class ArticleAdminSerializer(AuthorMixin, serializers.ModelSerializer):
    author_on_read = serializers.SerializerMethodField(source="author", read_only=True)
    news_paragraphs = ArticleParagraphSerializer(many=True)

    class Meta:
        model = Article
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

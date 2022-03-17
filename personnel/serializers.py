from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.serializers import UserSerializer

from .models import LocalPassport, Personnel, PersonnelDocument, Position


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = "__all__"


class PersonnelDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonnelDocument
        exclude = ("employee",)


class LocalPassportSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalPassport
        exclude = ("employee",)


class PersonnelSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects,
        required=False,
        write_only=True,
        allow_null=True,
        validators=[UniqueValidator(queryset=Personnel.objects)],
    )
    user_on_read = UserSerializer(source="user", read_only=True)
    position = serializers.SlugRelatedField(
        queryset=Position.objects,
        slug_field="name",
    )
    personnel_document = PersonnelDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Personnel
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["user"] = data.pop("user_on_read", None)
        return data

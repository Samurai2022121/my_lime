from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from rest_framework import serializers

# from orders.serializers import OrdersSerializer
from users.models import CustomerDeliveryAddress, RefreshToken


class AuthTokenSerializer(serializers.Serializer):
    phone_number = serializers.CharField(label="телефон", write_only=True)
    password = serializers.CharField(
        label="пароль",
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )
    token = serializers.CharField(label="токен", read_only=True)

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        password = attrs.get("password")

        if phone_number and password:
            user = authenticate(
                request=self.context.get("request"),
                phone_number=phone_number,
                password=password,
            )

            if not user:
                msg = "Недопустимые телефон или пароль."
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = 'Должны быть указаны поля "phone_number" и "password".'
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)
    confirm_password = serializers.CharField(
        max_length=128, min_length=8, write_only=True
    )
    access = serializers.CharField(max_length=255, read_only=True)
    expires_in = serializers.IntegerField(read_only=True)
    refresh = serializers.UUIDField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "phone_number",
            "password",
            "confirm_password",
            "access",
            "refresh",
            "expires_in",
        )

    def validate(self, data):
        if not data.get("password") or not data.get("confirm_password"):
            raise serializers.ValidationError(
                "Пожалуйста, введите пароль и подтвердите его."
            )
        if data.get("password") != data.pop("confirm_password"):
            raise serializers.ValidationError("Пароли не совпадают.")
        return data

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, required=False)
    phone_number = serializers.CharField(max_length=17, write_only=True, required=False)
    password = serializers.CharField(max_length=128, write_only=True)
    access = serializers.CharField(max_length=255, read_only=True)
    expires_in = serializers.IntegerField(read_only=True)
    refresh = serializers.UUIDField(read_only=True)
    full_name = serializers.CharField(read_only=True, required=False)

    def validate(self, data):
        email = data.get("email")
        phone_number = data.get("phone_number").replace("+", "")
        password = data.get("password")

        if email is None and phone_number is None:
            raise serializers.ValidationError("Введите номер телефона.")

        if password is None:
            raise serializers.ValidationError("Введите пароль.")

        try:
            model = get_user_model()
            user = (
                model.objects.get(email=email)
                if email
                else model.objects.get(phone_number=phone_number)
            )
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError("Такого пользователя не существует.")

        if not user.is_active:
            raise serializers.ValidationError("Пользователь был деактивирован.")

        if not user.check_password(password):
            raise serializers.ValidationError("Неверный логин или пароль.")

        validate_data = user.generate_tokens()
        validate_data["full_name"] = user.phone_number
        return validate_data


class TokenObtainSerializer(serializers.Serializer):
    access = serializers.CharField(max_length=255, required=False)
    expires_in = serializers.IntegerField(read_only=True, required=False)
    refresh = serializers.UUIDField()
    full_name = serializers.CharField(read_only=True, required=False)

    def validate(self, data):
        if "refresh" not in data:
            raise serializers.ValidationError("Refresh token must be set")

        try:
            old_refresh = RefreshToken.objects.select_related("user").get(
                uuid=data["refresh"]
            )
        except RefreshToken.DoesNotExist:
            raise serializers.ValidationError("Refresh token is invalid")

        if (old_refresh.date + settings.REFRESH_TOKEN_LIFETIME) < timezone.now():
            raise serializers.ValidationError("Refresh token is invalid")

        validate_data = old_refresh.user.generate_tokens()
        validate_data["phone_number"] = old_refresh.user.phone_number
        return validate_data


class GenerateRegistrationCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField()


class ValidateRegistrationCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()


class CustomerDeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDeliveryAddress
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    # orders = OrdersSerializer(many=True, read_only=True)
    delivery_address = CustomerDeliveryAddressSerializer(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "name",
            "surname",
            "fathers_name",
            "phone_number",
            "date_of_birth",
            "registration_date",
            "orders",
            "avatar",
            "delivery_address",
        )


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "name",
            "surname",
            "fathers_name",
            "phone_number",
            "registration_date",
            "date_of_birth",
        )


class ChangeUserPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, data):
        new_password = data.get("new_password")

        if new_password is None:
            raise serializers.ValidationError("Введите новый пароль.")

        if new_password != data.pop("new_password_confirm"):
            raise serializers.ValidationError("Пароли не совпадают.")

        return data

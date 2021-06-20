from django.utils import timezone

from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework import serializers, status

from KnoxStorage.apps.ipfs_app.models import File, Folder
from KnoxStorage.apps.users.models import RefreshToken, AccessFile, AccessFolder, User


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)
    access = serializers.CharField(max_length=255, read_only=True)
    expires_in = serializers.IntegerField(read_only=True)
    refresh = serializers.UUIDField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('email', 'phone_number', 'password', 'name', 'surname', 'access', 'refresh', 'expires_in')

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
        email = data.get('email')
        phone_number = data.get('phone_number')
        password = data.get('password')

        if email is None and phone_number is None:
            raise serializers.ValidationError('Email or phone number must be set')

        if password is None:
            raise serializers.ValidationError('Password must be set')

        try:
            model = get_user_model()
            user = model.objects.get(email=email) if email else model.objects.get(phone_number=phone_number)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError('No such user')

        if not user.is_active:
            raise serializers.ValidationError('This user has been deactivated.')

        if not user.check_password(password):
            raise serializers.ValidationError('Wrong login or password')

        validate_data = user.generate_tokens()
        validate_data['full_name'] = user.get_full_name()
        return validate_data


class TokenObtainSerializer(serializers.Serializer):
    access = serializers.CharField(max_length=255, required=False)
    expires_in = serializers.IntegerField(read_only=True, required=False)
    refresh = serializers.UUIDField()
    full_name = serializers.CharField(read_only=True, required=False)

    def validate(self, data):
        if 'refresh' not in data:
            raise serializers.ValidationError('Refresh token must be set')

        try:
            old_refresh = RefreshToken.objects.select_related('user').get(uuid=data['refresh'])
        except RefreshToken.DoesNotExist:
            raise serializers.ValidationError('Refresh token is invalid')

        if (old_refresh.date + settings.REFRESH_TOKEN_LIFETIME) < timezone.now():
            raise serializers.ValidationError('Refresh token is invalid')

        validate_data = old_refresh.user.generate_tokens()
        validate_data['full_name'] = old_refresh.user.get_full_name()
        return validate_data


class AccessFileSerializer(serializers.Serializer):
    email = serializers.EmailField()
    file = serializers.IntegerField()
    write = serializers.BooleanField()

    def validate(self, data):
        validated_data = super().validate(data)

        try:
            file = File.objects.get(id=validated_data['file'])
        except File.DoesNotExist:
            raise serializers.ValidationError('File not found')
        validated_data['file'] = file

        owner = self.context['request'].user
        if file.user != owner:
            raise serializers.ValidationError('No access')

        try:
            user = User.objects.get(email=validated_data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found')
        validated_data['user'] = user

        if user == owner:
            raise serializers.ValidationError('User is invalid')

        return validated_data

    def create(self, validated_data):
        access_file, created = AccessFile.objects.update_or_create(
            user=validated_data['user'], file=validated_data['file'], defaults={'write': validated_data['write']})

        return access_file

    def delete(self, validated_data):
        AccessFile.objects.filter(file=validated_data['file'], user=validated_data['user']).delete()


class AccessFolderSerializer(serializers.Serializer):
    email = serializers.EmailField()
    folder = serializers.IntegerField()
    write = serializers.BooleanField()

    def validate(self, data):
        validated_data = super().validate(data)

        try:
            folder = Folder.objects.get(id=validated_data['folder'])
        except Folder.DoesNotExist:
            raise serializers.ValidationError('File not found')
        validated_data['folder'] = folder

        owner = self.context['request'].user
        if folder.user != owner:
            raise serializers.ValidationError('No access')

        try:
            user = User.objects.get(email=validated_data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found')
        validated_data['user'] = user

        if user == owner:
            raise serializers.ValidationError('User is invalid')

        return validated_data

    def create(self, validated_data):
        access_file, created = AccessFolder.objects.update_or_create(
            user=validated_data['user'], folder=validated_data['folder'], defaults={'write': validated_data['write']})

        return access_file

    def delete(self, validated_data):
        AccessFolder.objects.filter(folder=validated_data['folder'], user=validated_data['user']).delete()

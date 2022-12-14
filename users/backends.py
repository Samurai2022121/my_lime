from datetime import datetime

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import authentication, exceptions


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = "Bearer"

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header or len(auth_header) != 2:
            return None

        prefix = auth_header[0].decode("utf-8")
        token = auth_header[1].decode("utf-8")

        if prefix.lower() != auth_header_prefix:
            return None

        return self._authenticate_credentials(token)

    @staticmethod
    def _authenticate_credentials(token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except Exception:
            raise exceptions.AuthenticationFailed(
                "Invalid authentication. Could not decode token."
            )

        if payload["expires_in"] < datetime.timestamp(timezone.now()):
            raise exceptions.AuthenticationFailed("Invalid authentication.")

        try:
            user = get_user_model().objects.get(pk=payload["id"])
        except get_user_model().DoesNotExist:
            raise exceptions.AuthenticationFailed(
                "No user matching this token was found."
            )

        if not user.is_active:
            raise exceptions.AuthenticationFailed("This user has been deactivated.")

        return user, token

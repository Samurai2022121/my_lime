import json
import uuid
from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone
from loguru import logger
from rest_framework import status, views, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import CustomerDeliveryAddress, GeneratedPassword, User
from users.serializers import (
    ChangeUserPasswordSerializer,
    CustomerDeliveryAddressSerializer,
    GenerateRegistrationCodeSerializer,
    LoginSerializer,
    RegistrationSerializer,
    TokenObtainSerializer,
    UserListSerializer,
    UserSerializer,
    ValidateRegistrationCodeSerializer,
)
from utils import permissions as perms
from utils.models_utils import generate_new_password
from utils.views_utils import (
    BulkChangeArchiveStatusViewSetMixin,
    OrderingModelViewsetMixin,
)

from .filters import UserFilter
from .serializers import AuthTokenSerializer

SMS_TIMEOUT = 60


class ObtainAuthTokenIfPermitted(ObtainAuthToken):

    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        if user.has_perm(
            f"{Token._meta.app_label}.add_{Token._meta.model_name}",
        ):
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})

        raise PermissionDenied("Plain token authentication is not allowed.")


class RegistrationAPIView(views.APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = user.generate_tokens()
        return Response(data, status=status.HTTP_201_CREATED)


class LoginAPIView(views.APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        data = {"password": request.data.get("password")}
        if "@" in request.data:
            data["email"] = request.data.get("email")
        else:
            data["phone_number"] = request.data.get("phone_number").replace("+", "")
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenObtainAPIView(views.APIView):
    permission_classes = (AllowAny,)
    serializer_class = TokenObtainSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GenerateLoginCodeAPIView(views.APIView):
    permission_classes = (AllowAny,)
    serializer_class = GenerateRegistrationCodeSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.data["phone_number"].replace("+", "")
        user = User.objects.filter(phone_number=phone_number)
        if not user:
            user = User.objects.create_user(
                phone_number=phone_number, password=str(uuid.uuid4())
            )
        else:
            user = user.first()
        expiry_date = timezone.now() - timedelta(minutes=62)

        password, created = GeneratedPassword.objects.get_or_create(
            user=user, date__gte=expiry_date
        )

        if not created:
            if password.attempts == 2:
                return Response(
                    status=405,
                    data={
                        "message": "???????????????? ?????????? ???? ???????????????? ??????????????????, ???????????????????? ??????????."
                    },
                )
            password.attempts += 1
            password.password = generate_new_password()
            password.save()

        sms_params = {
            "token": settings.SMS_API_KEY,
            "message": f"?????? ?????????? ????????????: {password.password}",
            "phone": f"+{phone_number}",
            "alphaname_id": settings.SMS_ALPHA_NAME,
        }
        sms = requests.get(
            "https://app.sms.by/api/v1/sendQuickSMS",
            params=sms_params,
            timeout=SMS_TIMEOUT,
        )
        if sms.status_code == 200 and "error" not in json.loads(sms.content):
            return Response(
                status=200,
                data={"message": "???????????? ?????????????????? ???? ?????????????????? ?????????????????? ??????????."},
            )
        else:
            logger.error(
                f"""Error authenticating user via SMS:
                request was {sms_params}
                answer was {sms.status_code}: {sms.content}"""
            )
            return Response(
                status=405, data={"message": "?????????????????? ????????????, ???????????????????? ??????????."}
            )


class ValidateLoginCodeAPIView(views.APIView):
    permission_classes = (AllowAny,)
    serializer_class = ValidateRegistrationCodeSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.data["phone_number"].replace("+", "")
        submitted_password = serializer.data["password"]

        user = User.objects.filter(phone_number=phone_number).first()
        expiry_date = timezone.now() - timedelta(minutes=62)

        password = GeneratedPassword.objects.filter(
            user=user, attempts__lt=2, date__gte=expiry_date
        )

        if not password:
            return Response(
                status=405, data={"message": "???????????????????? ?????????????????????????? ?????????? ????????????."}
            )

        if submitted_password != password.first().password:
            return Response(status=405, data={"message": "???????????????? ????????????."})
        else:
            password.first().delete()
            data = user.generate_tokens()
            return Response(data, status=status.HTTP_200_OK)


class UserView(
    BulkChangeArchiveStatusViewSetMixin,
    OrderingModelViewsetMixin,
    viewsets.ModelViewSet,
):
    filterset_class = UserFilter
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_staff,
            write=perms.allow_staff,
            get_current_user=perms.allow_authenticated,
        ),
    )
    serializer_class = UserSerializer
    lookup_field = "id"
    queryset = User.objects.all()
    serializer_action_classes = {
        "list": UserListSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_action_classes.get(
            self.action, super().get_serializer_class()
        )

    def get_queryset(self):
        qs = self.queryset.filter(is_staff=False)
        if "is_archive" not in self.request.query_params:
            qs = qs.filter(is_archive=False)
        ordering_fields = self.get_ordering_fields()
        if ordering_fields:
            return qs.order_by(*ordering_fields)
        return qs

    @action(detail=False, methods=["get"], url_path="current-user-info")
    def get_current_user(self, request, **kwargs):
        current_user = self.request.user
        serialized_data = self.serializer_class(current_user)
        return Response(status=status.HTTP_200_OK, data=serialized_data.data)


class ChangeUserPasswordAPIView(views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangeUserPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        user.set_password(raw_password=serializer.validated_data["new_password"])
        user.save()
        return Response(
            status=status.HTTP_202_ACCEPTED, data={"message": "???????????? ?????????????? ??????????????."}
        )


class CustomerDeliveryAddressViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = None
    serializer_class = CustomerDeliveryAddressSerializer
    lookup_field = "id"
    queryset = CustomerDeliveryAddress.objects.none()

    def get_queryset(self):
        qs = self.request.user.delivery_address.all()
        if "is_archive" not in self.request.query_params:
            qs = qs.filter(is_archive=False)
        return qs

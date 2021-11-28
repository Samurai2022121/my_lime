from datetime import timedelta
import requests
import json
import uuid

from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from rest_framework import views, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.serializers import (LoginSerializer, RegistrationSerializer, TokenObtainSerializer,
                               GenerateRegistrationCodeSerializer, ValidateRegistrationCodeSerializer,
                               UserSerializer, ChangeUserPasswordSerializer, UserListSerializer,
                               CustomerDeliveryAddressSerializer, )
from users.models import User, GeneratedPassword, CustomerDeliveryAddress
from utils.models_utils import generate_new_password


class RegistrationAPIView(views.APIView):
    permission_classes = (AllowAny, )
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = user.generate_tokens()
        return Response(data, status=status.HTTP_201_CREATED)


class LoginAPIView(views.APIView):
    permission_classes = (AllowAny, )
    serializer_class = LoginSerializer

    def post(self, request):
        data = {'password': request.data.get('password')}
        if '@' in request.data:
            data['email'] = request.data.get('email')
        else:
            data['phone_number'] = request.data.get('phone_number').replace("+", "")
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenObtainAPIView(views.APIView):
    permission_classes = (AllowAny, )
    serializer_class = TokenObtainSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GenerateLoginCodeAPIView(views.APIView):
    permission_classes = (AllowAny, )
    serializer_class = GenerateRegistrationCodeSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.data['phone_number'].replace("+", "")
        user = User.objects.filter(phone_number=phone_number)
        if not user:
            user = User.objects.create_user(phone_number=phone_number, password=str(uuid.uuid4()))
        else:
            user = user.first()
        expiry_date = timezone.now() - timedelta(minutes=62)

        password, created = GeneratedPassword.objects.get_or_create(user=user, date__gte=expiry_date)

        if not created:
            if password.attempts == 2:
                return Response(status=405, data={"message": "Превышен лимит на отправку сообщений, попробуйте позже."})
            password.attempts += 1
            password.password = generate_new_password()
            password.save()

        sms_params = {"token": settings.SMS_API_KEY, "message": f"Ваш новый пароль: {password.password}",
                      "phone": f'+{phone_number}', 'alphaname_id': settings.SMS_ALPHA_NAME}
        sms = requests.get("https://app.sms.by/api/v1/sendQuickSMS", params=sms_params)
        if sms.status_code == 200 and 'error' not in json.loads(sms.content):
            return Response(status=200, data={"message": "Пароль отправлен на указанный мобильный номер."})
        else:
            print(sms.json())
            return Response(status=405, data={"message": "Произошла ошибка, попробуйте позже."})


class ValidateLoginCodeAPIView(views.APIView):
    permission_classes = (AllowAny, )
    serializer_class = ValidateRegistrationCodeSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.data['phone_number'].replace("+", "")
        submitted_password = serializer.data['password']

        user = User.objects.filter(phone_number=phone_number).first()
        expiry_date = timezone.now() - timedelta(minutes=62)

        password = GeneratedPassword.objects.filter(user=user, attempts__lt=2, date__gte=expiry_date)

        if not password:
            return Response(status=405, data={"message": "Необходимо сгенерировать новый пароль."})

        if submitted_password != password.first().password:
            return Response(status=405, data={"message": "Неверный пароль."})
        else:
            password.first().delete()
            data = user.generate_tokens()
            return Response(data, status=status.HTTP_200_OK)


class UserView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    lookup_field = 'id'
    queryset = User.objects.filter(is_staff=False)
    serializer_action_classes = {
        'list': UserListSerializer
    }

    def get_serializer_class(self):
        return self.serializer_action_classes.get(self.action, super().get_serializer_class())

    def get_queryset(self):
        qs = self.queryset
        if 's' in self.request.query_params:
            search_value = self.request.query_params['s']
            qs = qs.filter(Q(phone_number__icontains=search_value))
        return qs


class ChangeUserPasswordAPIView(views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangeUserPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        user.set_password(raw_password=serializer.data['new_password'])
        user.save()
        return Response(status=status.HTTP_202_ACCEPTED,  data={"message": "Пароль успешно изменен."})


class CustomerDeliveryAddressViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CustomerDeliveryAddressSerializer
    lookup_field = 'id'
    queryset = CustomerDeliveryAddress.objects.none()

    def get_queryset(self):
        return self.request.user.delivery_address.all()

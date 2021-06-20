from rest_framework import views, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from users.serializers import LoginSerializer, RegistrationSerializer, TokenObtainSerializer


class RegistrationAPIView(views.APIView):
    permission_classes = (AllowAny, )
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = user.generate_tokens()
        data['full_name'] = user.get_full_name()
        return Response(data, status=status.HTTP_201_CREATED)


class LoginAPIView(views.APIView):
    permission_classes = (AllowAny, )
    serializer_class = LoginSerializer

    def post(self, request):
        data = {'password': request.data.get('password')}
        print(request.data)
        if '@' in request.data:
            data['email'] = request.data.get('email')
        else:
            data['phone_number'] = request.data.get('phone_number')
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

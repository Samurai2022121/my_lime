from django.urls import path

from users.users.v1.views import LoginAPIView, RegistrationAPIView, TokenObtainAPIView


urlpatterns = [
    path('user/registration', RegistrationAPIView.as_view(), name='registration'),
    path('user/login', LoginAPIView.as_view(), name='login'),
    path('user/obtain', TokenObtainAPIView.as_view(), name='obtain'),
]

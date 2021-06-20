from django.urls import path

from users.views import LoginAPIView, RegistrationAPIView, TokenObtainAPIView


urlpatterns = [
    path('registration', RegistrationAPIView.as_view(), name='registration'),
    path('login', LoginAPIView.as_view(), name='login'),
    path('obtain', TokenObtainAPIView.as_view(), name='obtain'),
]

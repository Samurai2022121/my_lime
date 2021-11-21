from django.urls import path
from rest_framework import routers

from users.views import LoginAPIView, RegistrationAPIView, TokenObtainAPIView, GenerateLoginCodeAPIView,\
    ValidateLoginCodeAPIView, UserView

router = routers.SimpleRouter()
router.register('users', UserView)

urlpatterns = [
    path('registration', RegistrationAPIView.as_view(), name='registration'),
    path('login', LoginAPIView.as_view(), name='login'),
    path('obtain', TokenObtainAPIView.as_view(), name='obtain'),
    path('generate-login-code', GenerateLoginCodeAPIView.as_view(), name='generate_reg_code'),
    path('validate-login-code', ValidateLoginCodeAPIView.as_view(), name='validate_reg_code')
]

urlpatterns += router.urls

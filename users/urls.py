from django.urls import path
from rest_framework import routers

from users.views import (
    ChangeUserPasswordAPIView,
    CustomerDeliveryAddressViewset,
    GenerateLoginCodeAPIView,
    LoginAPIView,
    RegistrationAPIView,
    TokenObtainAPIView,
    UserView,
    ValidateLoginCodeAPIView,
)

router = routers.SimpleRouter()
router.register("users", UserView)
router.register("delivery-address", CustomerDeliveryAddressViewset)

urlpatterns = [
    path("registration", RegistrationAPIView.as_view(), name="registration"),
    path("login", LoginAPIView.as_view(), name="login"),
    path("obtain", TokenObtainAPIView.as_view(), name="obtain"),
    path(
        "generate-login-code",
        GenerateLoginCodeAPIView.as_view(),
        name="generate_reg_code",
    ),
    path(
        "validate-login-code",
        ValidateLoginCodeAPIView.as_view(),
        name="validate_reg_code",
    ),
    path(
        "change-user-password",
        ChangeUserPasswordAPIView.as_view(),
        name="change-user-password",
    ),
]

urlpatterns += router.urls

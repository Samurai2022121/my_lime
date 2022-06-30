from django.urls import path

from .views import ApplicableOffersView

urlpatterns = [
    path(
        "outlets/<int:shop_id>/offers/", ApplicableOffersView.as_view(), name="offers"
    ),
]

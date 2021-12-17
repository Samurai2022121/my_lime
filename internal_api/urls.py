from django.urls import path
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register("outlets", views.ShopViewSet)
router.register("personnel", views.PersonnelViewSet)
router.register("matrix", views.WarehouseViewSet)

urlpatterns = [
    path("upload-csv/", views.UploadCSVGenericView.as_view(), name="csv-upload"),
]

urlpatterns += router.urls

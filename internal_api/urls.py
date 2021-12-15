from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register("outlets", views.ShopViewSet)
router.register("personnel", views.PersonnelViewSet)
router.register("matrix", views.WarehouseViewSet)

urlpatterns = []

urlpatterns += router.urls

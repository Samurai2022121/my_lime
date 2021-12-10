from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register("outlets", views.ShopViewset)

urlpatterns = []

urlpatterns += router.urls

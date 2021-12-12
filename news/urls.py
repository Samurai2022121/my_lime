from rest_framework import routers

from .views import NewsViewset, SectionViewset

router = routers.SimpleRouter()
router.register("news", NewsViewset)
router.register("sections", SectionViewset)

urlpatterns = []

urlpatterns += router.urls

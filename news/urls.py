from rest_framework import routers

from .views import (
    NewsParagraphsImagesViewset,
    NewsParagraphsViewset,
    NewsViewset,
    SectionViewset,
)

router = routers.SimpleRouter()
router.register("news", NewsViewset)
router.register("sections", SectionViewset)
router.register("news-paragraphs", NewsParagraphsViewset)
router.register("news-paragraphs-images", NewsParagraphsImagesViewset)

urlpatterns = []

urlpatterns += router.urls

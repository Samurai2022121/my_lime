from rest_framework import routers

from .views import NewsViewset, SectionViewset, NewsParagraphsViewset, NewsParagraphsImagesViewset

router = routers.SimpleRouter()
router.register("news", NewsViewset)
router.register("sections", SectionViewset)
router.register("news-paragraphs", NewsParagraphsViewset)
router.register("news-paragraphs-images", NewsParagraphsImagesViewset)

urlpatterns = []

urlpatterns += router.urls

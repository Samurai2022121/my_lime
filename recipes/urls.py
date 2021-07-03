from rest_framework import routers

from .views import (
    RecipeViewset,
    RecipeCategoryViewset
)

router = routers.SimpleRouter()
router.register('recipes', RecipeViewset)
router.register('categories', RecipeCategoryViewset)

urlpatterns = router.urls

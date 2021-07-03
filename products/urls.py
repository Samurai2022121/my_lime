from rest_framework import routers

from .views import (
    ProductViewset, CategoryViewset, SubcategoryViewset
)

router = routers.SimpleRouter()
router.register('products', ProductViewset)
router.register('categories', CategoryViewset)
router.register('subcategories', SubcategoryViewset)

urlpatterns = router.urls

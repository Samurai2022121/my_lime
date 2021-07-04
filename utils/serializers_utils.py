from products.models import Product
from recipes.models import Recipe
from news.models import News


CONTENT_TYPES = dict(
    PDD=Product,
    RCP=Recipe,
    NW=News
)

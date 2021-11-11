from products.models import Product
from recipes.models import Recipe
from news.models import News


CONTENT_TYPES = dict(
    PD=Product,
    RP=Recipe,
    NW=News
)

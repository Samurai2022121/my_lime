from typing import Literal

from django.db.models import OuterRef, Q, QuerySet


def build_offer_subquery(
    sqs: QuerySet,
    by: Literal["condition", "benefit"],
) -> QuerySet:
    by += "__range__"
    return (
        sqs.filter(
            Q(**{f"{by}includes_all": True})
            | Q(**{f"{by}include_product_units": OuterRef("pk")})
            | Q(**{f"{by}include_products__units": OuterRef("pk")})
            | Q(**{f"{by}include_categories__products__units": OuterRef("pk")})
        )
        .exclude(
            Q(**{f"{by}exclude_product_units": OuterRef("pk")})
            | Q(**{f"{by}exclude_products__units": OuterRef("pk")})
            | Q(**{f"{by}exclude_categories__products__units": OuterRef("pk")})
        )
        .order_by("pk")
        .distinct("pk")
    )

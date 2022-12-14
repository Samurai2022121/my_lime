from decimal import Decimal, DecimalException
from itertools import chain
from typing import Dict

from django.contrib.auth import get_user_model
from django.contrib.postgres.expressions import ArraySubquery
from django.contrib.postgres.fields import ArrayField
from django.db.models import BigAutoField, DecimalField, OuterRef, Subquery
from django.utils.functional import cached_property
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from discounts.models import Benefit, Condition, LoyaltyCard, Offer, Voucher
from internal_api.models import Shop, Warehouse
from products.models import ProductUnit
from utils import permissions as perms
from utils.models_utils import build_offer_subquery

from .serializers import BasketSerializer


class OfferMixin:
    """
    Container for business logic related to finding and applying offers (discounts).
    """

    @staticmethod
    def check_outlet(shop_id: int) -> Shop:
        try:
            shop = Shop.objects.filter(is_archive=False, e_shop_base=True).get(
                pk=shop_id
            )
        except Shop.DoesNotExist:
            raise NotFound(detail=f"{shop_id} is not a valid e-store Id.")
        return shop

    @cached_property
    def basket_data(self) -> Dict:
        # input data contains verified model objects
        serializer = self.get_serializer(
            data=self.request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    @cached_property
    def buyer(self):
        buyer = self.request.user
        # anonymous is not an identity
        if buyer.is_anonymous:
            buyer = None
        # only staff is allowed to provide the user identity, or lack thereof
        elif buyer.is_superuser or buyer.is_staff:
            buyer = (
                get_user_model()
                .objects.filter(pk=self.request.data.get("buyer"))
                .first()
            )
        return buyer

    @cached_property
    def card(self):
        card = LoyaltyCard.objects.filter(pk=self.request.data.get("card")).first()
        # it's not allowed to use a card that don't match the identity
        # (or should we use the card owner's identity at this point?)
        if self.buyer and card and card.buyer != self.buyer:
            card = None
        return card

    @cached_property
    def offer_queryset(self):
        qs = Offer.objects.filter(is_active=True, type=Offer.TYPES.site)

        if self.buyer is not None:
            qs |= Offer.objects.filter(is_active=True, type=Offer.TYPES.buyer)
        if self.card is not None:
            qs |= Offer.objects.filter(is_active=True, pk=self.card.offer.pk)

        voucher_pks = self.request.data.get("vouchers")
        if voucher_pks:
            voucher_subquery = Voucher.objects.filter(
                pk__in=voucher_pks,
                is_active=True,
            )
            qs |= Offer.objects.filter(
                is_active=True,
                pk__in=Subquery(voucher_subquery.values("offer_id")),
            )

        return qs

    def apply_offers(self, shop_id: int) -> Dict:
        lines = self.basket_data["lines"]

        # accelerate product unit lookup
        unit_dict = {x["product_unit"].pk: x for x in lines}

        # get offer queryset using condition ranges
        cond_offer_pks = set(
            chain.from_iterable(
                x["product_unit"].cond_range or [] for x in unit_dict.values()
            )
        )
        offer_qs = Offer.objects.filter(pk__in=cond_offer_pks)

        # accelerate offer lookup
        offer_dict = {x.pk: {"offer": x} for x in offer_qs}

        # evaluate offers' application
        for offer_line in offer_dict.copy().values():
            offer = offer_line["offer"]
            units = [
                x["product_unit"]
                for x in unit_dict.values()
                if offer.pk in x["product_unit"].cond_range or []
            ]

            # decide how many times the offer may be applied
            match offer.condition.type:
                case Condition.TYPES.value:
                    in_basket = Decimal("0.00")
                    for unit in units:
                        quantity = unit_dict[unit.pk]["quantity"]
                        in_basket += quantity * unit.full_price
                case Condition.TYPES.count:
                    in_basket = sum(unit_dict[x.pk]["quantity"] for x in units)
                case Condition.TYPES.coverage:
                    in_basket = len(units)
                case unknown:  # noqa: F821
                    raise ValidationError(
                        f"Unknown condition type: {unknown}"  # noqa: F821
                    )
            try:
                apply_times = int(in_basket // offer.condition.value)
            except (DecimalException, ZeroDivisionError):
                # `offer.condition.value` should not be 0
                apply_times = 0

            # abide offer limit per purchase
            if offer.order_limit > 0:
                apply_times = min(apply_times, offer.order_limit)

            if apply_times > 0:
                offer_line["apply_times"] = apply_times
            else:
                # delete inapplicable offers
                del offer_dict[offer.pk]

        # adjust offer queryset again using application data
        offer_qs = Offer.objects.filter(pk__in=offer_dict.keys())

        # build a subquery of offers that match a benefit range
        benefit_range_sub = build_offer_subquery(offer_qs, "benefit")

        # annotate product units with applicable offers
        unit_qs = ProductUnit.objects.filter(pk__in=unit_dict.keys(),).annotate(
            warehouse=Subquery(
                Warehouse.objects.filter(
                    shop_id=shop_id,
                    product_unit_id=OuterRef("pk"),
                ).values("pk"),
                output_field=BigAutoField("??????????"),
            ),
            full_price=Subquery(
                Warehouse.objects.filter(
                    shop_id=shop_id,
                    product_unit_id=OuterRef("pk"),
                ).values("price"),
                output_field=DecimalField("????????", decimal_places=2, max_digits=6),
            ),
            # empty array subqueries are represented as None, which is sucks
            benefit_range=ArraySubquery(
                benefit_range_sub.values("pk"),
                output_field=ArrayField(BigAutoField, verbose_name="??????????????????????"),
            ),
        )

        # update dicts
        for unit in unit_qs:
            unit_dict[unit.pk].update(
                {
                    "product_unit": unit,
                    "full_price": unit.full_price,
                    "discounted_price": unit.full_price,
                    "warehouse": unit.warehouse,
                }
            )

        for offer_pk, offer_line in offer_dict.items():
            offer_line["units"] = {}
            for unit_pk, unit_line in unit_dict.items():
                if offer_pk in unit_line["product_unit"].benefit_range or []:
                    offer_line["units"][unit_pk] = unit_line

        # calculate discounted prices
        for offer_line in offer_dict.values():
            match offer_line["offer"].benefit.type:
                case Benefit.TYPES.percentage:
                    for _ in range(offer_line["apply_times"]):
                        for unit_line in offer_line["units"].values():
                            unit_line["discounted_price"] *= (
                                100 - offer_line["offer"].benefit.value
                            ) / 100
                case Benefit.TYPES.absolute:
                    discount_avail = (
                        offer_line["units"].benefit.value * offer_line["apply_times"]
                    )
                    full_total = sum(
                        x["discounted_price"] * x["quantity"]
                        for x in offer_line["units"]
                    )
                    for unit_line in offer_line["units"].values():
                        # calculate discount share; on the last iteration
                        # discounted price should be equal to the full total
                        discount = (
                            discount_avail
                            * unit_line["discounted_price"]
                            * unit_line["quantity"]
                            / full_total
                        )
                        full_total -= (
                            unit_line["discounted_price"] * unit_line["quantity"]
                        )
                        discount_avail -= discount
                        # TODO: this sharing is improper:
                        unit_line["discounted_price"] -= (
                            discount / unit_line["quantity"]
                        )
                case Benefit.TYPES.multibuy:
                    cheapest = sorted(
                        offer_line["units"].values(),
                        key=lambda x: x["discounted_price"] * x["quantity"],
                    )[0]
                    cheapest["discounted_price"] = Decimal("0.00")
                case Benefit.TYPES.fixed_price:
                    price_avail = offer_line["offer"].benefit.value
                    full_total = sum(
                        x["discounted_price"] * x["quantity"]
                        for x in offer_line["units"].values()
                    )
                    for unit_line in offer_line["units"].values():
                        price = (
                            price_avail
                            * unit_line["discounted_price"]
                            * unit_line["quantity"]
                            / full_total
                        )
                        full_total -= (
                            unit_line["discounted_price"] * unit_line["quantity"]
                        )
                        price_avail -= price
                        # TODO: this sharing may be improper:
                        unit_line["discounted_price"] -= price / unit_line["quantity"]
                case unknown:  # noqa: F821
                    raise ValidationError(
                        f"Unknown benefit type: {unknown}"  # noqa: F821
                    )

        # align the decimal point
        for line in lines:
            if line["discounted_price"] is not None:
                line["discounted_price"] = round(line["discounted_price"], 2)

        # prepare warehouse data
        warehouse_qs = Warehouse.objects.filter(
            shop_id=shop_id,
            product_unit__in=unit_dict.keys(),
        )
        warehouse_dict = {x.pk: x for x in warehouse_qs}
        for line in lines:
            line["warehouse"] = warehouse_dict.get(line["warehouse"])

        # prepare applied offers data
        for line in lines:
            line["offers"] = []
            for offer_line in offer_dict.values():
                if line["product_unit"].pk in offer_line["units"]:
                    line["offers"].append(
                        {
                            "offer": offer_line["offer"],
                            "apply_times": offer_line["apply_times"],
                        }
                    )

        # build output data with applied offers and discount prices
        return {
            "buyer": self.basket_data.get("buyer"),
            "card": self.basket_data.get("card"),
            "vouchers": self.basket_data.get("vouchers", []),
            "lines": lines,
        }


class ApplicableOffersView(OfferMixin, APIView):
    """Suggest discounts for a given basket object."""

    serializer_class = BasketSerializer
    permission_classes = (perms.ActionPermission(default=perms.allow_all),)

    def post(self, request, shop_id, *args, **kwargs):
        self.check_outlet(shop_id)
        output_data = self.apply_offers(shop_id)
        return Response(
            data=BasketSerializer(
                output_data,
                context=self.get_serializer_context(),
            ).data,
            status=status.HTTP_200_OK,
        )

    def get_serializer(self, *args, **kwargs):
        # borrow serializer logic (without model object-related stuff)
        # from DRF generic views
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        assert self.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method." % self.__class__.__name__
        )
        return self.serializer_class

    def get_serializer_context(self):
        return {"request": self.request, "format": self.format_kwarg, "view": self}

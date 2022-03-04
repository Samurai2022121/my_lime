from decimal import Decimal

from django.db import models
from django.db.models import Case, F, OuterRef, Subquery, Sum, When
from django.db.models.functions import Coalesce
from sql_util.aggregates import SubquerySum

from internal_api.models import Personnel, Shop
from products.models import ProductUnit
from utils.models_utils import Timestampable


class TechCard(Timestampable, models.Model):
    name = models.CharField("наименование", max_length=255)
    author = models.ForeignKey(
        Personnel,
        on_delete=models.PROTECT,
        related_name="tech_card",
        verbose_name="автор",
    )
    is_archive = models.BooleanField(default=False)
    ingredients = models.ManyToManyField(
        ProductUnit,
        through="TechCardProduct",
        related_name="ingredients",
        verbose_name="ингредиенты",
    )
    end_product = models.ForeignKey(
        ProductUnit,
        on_delete=models.PROTECT,
        related_name="end_products",
        verbose_name="готовый продукт",
    )
    amount = models.DecimalField(
        "выход",
        default=1,
        max_digits=7,
        decimal_places=2,
    )

    class Meta:
        verbose_name = "Техкарта"
        verbose_name_plural = "Техкарты"

    def __str__(self):
        return self.name


class TechCardProduct(models.Model):
    tech_card = models.ForeignKey(
        TechCard, on_delete=models.PROTECT, related_name="tech_products"
    )
    product_unit = models.ForeignKey(
        ProductUnit,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name="сырьё",
    )
    quantity = models.DecimalField(
        "количество",
        max_digits=7,
        decimal_places=2,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.quantity} {self.product_unit}"


class DailyMenuPlanLayoutManager(models.Manager):
    """
    Annotates the model with the following stock quantities:
    - `total`: ingredient required for the whole plan,
    - `remaining`: ingredient available in stock in production units (weight,
      volume, et c.),
    - `to_convert`: ingredients available in other units (e.g. packages,
      boxes, bottles, or crates),
    - `shortage`: the deficit of the ingredient (0 if there's enough).
    """

    def get_queryset(self):
        from internal_api.models import Warehouse, WarehouseRecord

        convert_subquery = Warehouse.objects.filter(
            shop=OuterRef("shop"),
            product_unit__in=OuterRef(
                "dishes__tech_products__product_unit__conversion_targets__source_unit"
            ),
        ).annotate(
            convert=Sum(
                F("warehouse_records__quantity")
                * OuterRef(
                    "dishes__tech_products__product_unit__conversion_targets__factor"
                )
            ),
        )

        warehouse_subquery = WarehouseRecord.objects.filter(
            warehouse__shop=OuterRef("shop"),
            warehouse__product_unit=OuterRef("dishes__tech_products__product_unit"),
        )

        return (
            super()
            .get_queryset()
            .values(
                "dishes__tech_products__product_unit",
            )
            .annotate(
                product_name=F("dishes__tech_products__product_unit__product__name"),
                unit_name=F("dishes__tech_products__product_unit__unit__name"),
                total=Sum(
                    F("dishes__tech_products__quantity") * F("menu_dishes__quantity")
                ),
                remaining=Coalesce(
                    SubquerySum(warehouse_subquery.values("quantity")),
                    Decimal(0),
                ),
                to_convert=Coalesce(
                    Sum(
                        Subquery(convert_subquery.values("convert")[:1]),
                        distinct=True,
                    ),
                    Decimal(0),
                ),
                # TODO: account for conversion in ProductionDocument creation,
                #   then change the shortage calculation as follows:
                #   raw_shortage=F("total") - F("remaining") - F("to_convert"),
                raw_shortage=F("total") - F("remaining"),
                shortage=Case(
                    When(raw_shortage__lt=0, then=Decimal(0)),
                    default=F("raw_shortage"),
                ),
            )
        )


class DailyMenuPlanProduceManager(models.Manager):
    def get_queryset(self):
        quantity_subquery = MenuDish.objects.filter(
            menu=OuterRef("id"), dish=OuterRef("dishes__id")
        )

        return (
            super()
            .get_queryset()
            .values(
                "dishes__end_product",
            )
            .annotate(
                product_name=F("dishes__end_product__product__name"),
                unit_name=F("dishes__end_product__unit__name"),
                produce=Sum(
                    F("dishes__amount")
                    * Subquery(quantity_subquery.values("quantity")[:1])
                ),
            )
        )


class DailyMenuPlan(Timestampable, models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    name = models.CharField("название", max_length=255)
    dishes = models.ManyToManyField(TechCard, through="MenuDish")
    author = models.ForeignKey(Personnel, on_delete=models.PROTECT)

    objects = models.Manager()
    layout = DailyMenuPlanLayoutManager()
    produce = DailyMenuPlanProduceManager()

    class Meta:
        verbose_name = "План меню на день"
        verbose_name_plural = "Планы меню на день"
        default_related_name = "daily_menu_plans"

    def __str__(self):
        return self.author.first_name


class MenuDish(models.Model):
    dish = models.ForeignKey(TechCard, on_delete=models.CASCADE)
    menu = models.ForeignKey(DailyMenuPlan, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Заявка меню на день"
        verbose_name_plural = "Заявки меню на день"
        default_related_name = "menu_dishes"

    def __str__(self):
        return self.dish.name
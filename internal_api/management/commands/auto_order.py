from django.core.management.base import BaseCommand

from internal_api.models import Warehouse, WarehouseOrder, WarehouseOrderPositions

AUTO_ORDER_PREFIX = "AO"
AUTO_ORDER_DIGITS = 8


class Command(BaseCommand):
    help = "Обработка автоматических заказов"

    def generate_order_number(self):
        """Generate next order number."""
        last_order = (
            WarehouseOrder.objects.filter(
                order_number__startswith=AUTO_ORDER_PREFIX,
            )
            .order_by("order_number")
            .last()
        )
        base_number = 1
        if last_order:
            base_number = int(last_order.order_number.lstrip(AUTO_ORDER_PREFIX)) + 1
        return AUTO_ORDER_PREFIX + str(base_number).zfill(AUTO_ORDER_DIGITS)

    def handle(self, *args, **options):
        """
        Iterate through auto orders. If particular stock is low (less than
        the threshold), generate an order to resupply.
        """
        for wh in Warehouse.objects.filter(auto_order=True).iterator():
            if wh.remaining <= wh.min_remaining:
                order, _ = WarehouseOrder.objects.get_or_create(
                    status="approving",
                    is_archive=False,
                    supplier=wh.supplier,
                    shop=wh.shop,
                    defaults={
                        "order_number": self.generate_order_number(),
                    },
                )
                # TODO: m2m explicit intermediate seems a poor choice
                WarehouseOrderPositions.objects.get_or_create(
                    warehouse_order=order,
                    product=wh.product,
                    defaults={
                        "quantity": wh.max_remaining - wh.remaining,
                    },
                )

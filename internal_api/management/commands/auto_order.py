from django.core.management.base import BaseCommand

from internal_api.models import Warehouse, WarehouseOrder, WarehouseOrderPositions


class Command(BaseCommand):
    help = "Обработка автоматических заказов"

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
                )
                # TODO: m2m explicit intermediate seems a poor choice
                WarehouseOrderPositions.objects.get_or_create(
                    warehouse_order=order,
                    product=wh.product,
                    defaults={
                        "quantity": wh.max_remaining - wh.remaining,
                    },
                )

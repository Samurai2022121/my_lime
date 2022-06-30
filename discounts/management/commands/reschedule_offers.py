from itertools import chain

from django.core.management.base import BaseCommand
from loguru import logger

from lime import app

from ...models import Offer
from ...tasks import reschedule_offer


class Command(BaseCommand):
    help = "Запланировать изменения актуальности предложений (скидок)."

    def handle(self, *args, **options):
        logger.info("Revoking stale tasks...")
        tasks = chain.from_iterable(app.control.inspect().scheduled().values())
        task_count = 0
        for task in tasks:
            if task["request"]["name"] == "discounts.tasks.reschedule_offer":
                task_id = task["request"]["id"]
                app.control.revoke(task_id)
                task_count += 1
        logger.info(f"{task_count} tasks has been tagged for revoke.")

        # create new tasks
        for offer_id in Offer.objects.values_list("id", flat=True).iterator():
            reschedule_offer.apply_async(args=(offer_id,))

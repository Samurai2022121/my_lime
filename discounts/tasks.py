from datetime import datetime

from croniter import croniter
from django.apps import apps
from django.utils import timezone as dj_tz
from loguru import logger

from lime import app


def enable_offer(offer):
    offer.is_active = True
    offer.save()
    logger.info(f"Offer {offer.id} is enabled.")


def disable_offer(offer):
    offer.is_active = False
    offer.save()
    logger.info(f"Offer {offer.id} is disabled.")


def reschedule(task, offer_id: int, at: datetime):
    task.apply_async(args=(offer_id,), eta=at)
    logger.info(f"Rescheduling offer {offer_id} at {at}")


@app.task(bind=True, ignore_result=True)
def reschedule_offer(sender, offer_id: int, **kwargs):
    offer = apps.get_model("discounts", "Offer").objects.get(id=offer_id)
    now = dj_tz.make_aware(datetime.now())

    # check big interval
    if offer.started_at <= now < offer.ended_at:

        # is there any small interval?
        if offer.schedule:
            cron = croniter(offer.schedule, start_time=now, ret_type=datetime)
            prev_start = cron.get_prev()
            prev_end = prev_start + offer.duration

            if now < prev_end:
                # we're in the middle of the previous small interval
                enable_offer(offer)

                # reschedule at the end ot the current small interval
                # (or at the end of the big interval, whichever comes first)
                reschedule(sender, offer_id, min(prev_end, offer.ended_at))
                return

            next_start = cron.get_next()
            if next_start < offer.ended_at:
                # the next small interval is coming, reschedule at its start
                reschedule(sender, offer_id, next_start)

        else:
            enable_offer(offer)

            # no small interval, use big interval for scheduling
            reschedule(sender, offer_id, offer.ended_at)
            return

    # otherwise, deactivate the offer (just to be safe)
    disable_offer(offer)

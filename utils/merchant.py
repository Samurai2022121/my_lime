from urllib.parse import urlencode

import requests
from django.conf import settings
from django.urls import reverse_lazy


class Merchant:
    def registration_order(self, order):
        return_url = f"{settings.DOMAIN}{reverse_lazy('internal_api:alfa-callback', kwargs={'id': order.pk,})}"

        params = {
            "amount": int(order.sum_total),
            "currency": 933,
            "language": "ru",
            "orderNumber": order.pk,
            "returnUrl": return_url,
            "jsonParams": {},
            "expirationDate": "2022-09-08T14:14:00",
        }
        url = "https://web.rbsuat.com/ab_by/rest/register.do?password=Gce7UBpe&userName=thefresh.by-api&"
        r = requests.post("{}{}".format(url, urlencode(params)))
        return r.json()

    def get_status(self, order_id, merchant_order_number):
        params = {
            "orderId": order_id,
            "merchantOrderNumber": merchant_order_number,
        }
        url = "https://web.rbsuat.com/ab_by/rest/getOrderStatusExtended.do?password=Gce7UBpe&userName=thefresh.by-api&"
        r = requests.post("{}{}".format(url, urlencode(params)))
        return r.json()


merchant = Merchant()

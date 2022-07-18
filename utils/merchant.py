from datetime import datetime, timedelta
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.urls import reverse_lazy


class Merchant:
    @staticmethod
    def registration_order(order_id, amount, currency=933, language="ru"):
        return_url = f"{settings.DOMAIN}{reverse_lazy('orders:alfa-callback', kwargs={'id': order_id,})}"
        params = {
            "amount": amount,
            "currency": currency,
            "language": language,
            "orderNumber": order_id,
            "returnUrl": return_url,
            "jsonParams": {},
            "expirationDate": (datetime.now() + timedelta(days=2)).strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
        }
        url = "https://web.rbsuat.com/ab_by/rest/register.do?password={}&userName={}&".format(
            settings.ALFA_AUTH_PASSWORD, settings.ALFA_AUTH_LOGIN
        )
        r = requests.post("{}{}".format(url, urlencode(params)))
        return r.json()

    @staticmethod
    def get_status(order_id, merchant_order_number):
        params = {
            "orderId": order_id,
            "merchantOrderNumber": merchant_order_number,
        }
        url = "https://web.rbsuat.com/ab_by/rest/getOrderStatusExtended.do?password={}&userName={}&".format(
            settings.ALFA_AUTH_PASSWORD, settings.ALFA_AUTH_LOGIN
        )
        r = requests.post("{}{}".format(url, urlencode(params)))
        return r.json()


merchant = Merchant()

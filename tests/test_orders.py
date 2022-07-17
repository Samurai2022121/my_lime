from decimal import Decimal
from pathlib import Path

import pytest
from django.core.management import call_command
from pytest_drf import (
    Returns200,
    Returns201,
    UsesDetailEndpoint,
    UsesGetMethod,
    UsesListEndpoint,
    UsesPatchMethod,
    UsesPostMethod,
)
from pytest_drf.util import url_for
from pytest_lambda import lambda_fixture, static_fixture

from utils.views_utils import APIViewTest, ViewSetTest


@pytest.fixture(scope="module")
def django_db_setup(request, django_db_setup):
    # load a fixture from current directory
    call_command(
        "loaddata",
        Path(request.fspath).parent / "fixtures" / "products.json",
        Path(request.fspath).parent / "fixtures" / "shops.json",
        Path(request.fspath).parent / "fixtures" / "units.json",
        Path(request.fspath).parent / "fixtures" / "warehouses.json",
        Path(request.fspath).parent / "fixtures" / "discounts.json",
        Path(request.fspath).parent / "fixtures" / "orders.json",
    )


class TestOrdersViewSet(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, staff_client, get_response):
        return get_response

    shop_id = static_fixture(1)

    list_url = lambda_fixture(
        lambda shop_id: url_for("orders:order-list", shop_id=shop_id)
    )

    detail_url = lambda_fixture(
        lambda shop_id, id: url_for("orders:order-detail", shop_id=shop_id, id=id)
    )

    class TestList(UsesListEndpoint, UsesGetMethod, Returns200):
        pass

    class TestDetail(UsesDetailEndpoint, UsesGetMethod, Returns200):
        id = static_fixture(10)

    class TestUpdate(UsesDetailEndpoint, UsesPatchMethod, Returns200):
        id = static_fixture(10)

        data = static_fixture(
            {
                "payment_method": "card-post",
            }
        )

    class TestCreate(UsesListEndpoint, UsesPostMethod, Returns201):
        data = static_fixture(
            {
                "buyer": 3,
                "payment_method": "cash",
                "lines": [],
            }
        )

        def test_customer(self, json):
            assert json["buyer"] == 3


class TestOrderLinesViewSet(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, staff_client, get_response):
        return get_response

    shop_id = static_fixture(1)

    order_id = static_fixture(10)

    list_url = lambda_fixture(
        lambda shop_id, order_id: url_for(
            "orders:orderline-list", shop_id=shop_id, order_id=order_id
        )
    )

    detail_url = lambda_fixture(
        lambda shop_id, order_id, id: url_for(
            "orders:orderline-detail", shop_id=shop_id, order_id=order_id, id=id
        )
    )

    class TestList(UsesListEndpoint, UsesGetMethod, Returns200):
        pass

    class TestDetail(UsesDetailEndpoint, UsesGetMethod, Returns200):
        id = static_fixture(1)

    class TestUpdate(UsesDetailEndpoint, UsesPatchMethod, Returns200):
        id = static_fixture(1)

        data = static_fixture(
            {
                "full_price": Decimal("56.67"),
            }
        )

    class TestCreate(UsesListEndpoint, UsesPostMethod, Returns201):
        data = static_fixture(
            {
                "warehouse": 2,
                "quantity": 5,
                "discounted_price": Decimal("40.54"),
            }
        )


class TestOrderLineOffers(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, staff_client, get_response):
        return get_response

    shop_id = static_fixture(1)

    order_id = static_fixture(10)

    line_id = static_fixture(1)

    list_url = lambda_fixture(
        lambda shop_id, order_id, line_id: url_for(
            "orders:orderlineoffer-list",
            shop_id=shop_id,
            order_id=order_id,
            line_id=line_id,
        )
    )

    detail_url = lambda_fixture(
        lambda shop_id, order_id, line_id, id: url_for(
            "orders:orderlineoffer-detail",
            shop_id=shop_id,
            order_id=order_id,
            line_id=line_id,
            id=id,
        )
    )

    class TestList(UsesListEndpoint, UsesGetMethod, Returns200):
        pass

    class TestCreate(UsesListEndpoint, UsesPostMethod, Returns201):
        id = static_fixture(3)

        data = static_fixture(
            {
                "offer": 1,
                "apply_times": 1,
            }
        )


class TestOrderFromBasket(APIViewTest, UsesPostMethod, Returns201):
    @pytest.fixture
    def common_subject(self, db, staff_client, get_response):
        return get_response

    shop_id = static_fixture(1)

    url = lambda_fixture(
        lambda shop_id: url_for("orders:order-from-basket", shop_id=shop_id)
    )

    data = static_fixture(
        {
            "payment_method": "cash",
            "lines": [
                {
                    "product_unit": 1,
                    "quantity": 5,
                },
                {
                    "product_unit": 3,
                    "quantity": 2,
                },
                {
                    "product_unit": 4,
                    "quantity": 5,
                },
            ],
        }
    )

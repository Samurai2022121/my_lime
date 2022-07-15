from pathlib import Path

import pytest
from django.core.management import call_command
from pytest_drf import (
    Returns200,
    Returns201,
    UsesGetMethod,
    UsesListEndpoint,
    UsesPostMethod,
)
from pytest_drf.util import url_for
from pytest_lambda import lambda_fixture, static_fixture

from utils.views_utils import ViewSetTest


@pytest.fixture(scope="module")
def django_db_setup(request, django_db_setup):
    # load a fixture from current directory
    call_command(
        "loaddata",
        Path(request.fspath).parent / "fixtures" / "products.json",
        Path(request.fspath).parent / "fixtures" / "shops.json",
        Path(request.fspath).parent / "fixtures" / "units.json",
    )


class TestOrdersViewSet(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, staff_client, get_response):
        return get_response

    shop_id = static_fixture(1)

    list_url = lambda_fixture(
        lambda shop_id: url_for("orders:order-list", shop_id=shop_id)
    )

    class TestList(UsesListEndpoint, UsesGetMethod, Returns200):
        pass

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

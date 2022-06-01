from pathlib import Path

import pytest
from django.core.management import call_command
from pytest_drf import (
    Returns200,
    Returns201,
    UsesDetailEndpoint,
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
        Path(request.fspath).parent / "fixtures" / "shops.json",
        Path(request.fspath).parent / "fixtures" / "units.json",
    )


class TestWarehouseOrderViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, staff_client, get_response):
        return get_response

    list_url = lambda_fixture(lambda: url_for("internal_api:warehouseorder-list"))

    detail_url = lambda_fixture(
        lambda id: url_for("internal_api:warehouseorder-detail", id=id)
    )

    data = static_fixture(
        {
            "shop": 1,
            "status": "approving",
            "order_positions": [
                {
                    "product_unit": 1,
                },
                {
                    "product_unit": 3,
                },
            ],
        }
    )

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        pass

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        pass

    class TestDetail(UsesGetMethod, UsesDetailEndpoint, Returns200):
        @pytest.fixture
        def id(self, client, list_url, data):
            result = client.post(list_url, data, format="json")
            return result.json()["id"]

        def test_order_record_created(self, json):
            # two order positions made it from data fixture to database
            assert len(json["order_positions"]) == 2

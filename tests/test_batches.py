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
from rest_framework import status

from utils.views_utils import ViewSetTest


@pytest.fixture(scope="module")
def django_db_setup(request, django_db_setup):
    # load a fixture from current directory
    call_command(
        "loaddata",
        Path(request.fspath).parent / "fixtures" / "shops.json",
        Path(request.fspath).parent / "fixtures" / "units.json",
        Path(request.fspath).parent / "fixtures" / "warehouses.json",
        Path(request.fspath).parent / "fixtures" / "suppliers.json",
        Path(request.fspath).parent / "fixtures" / "batches.json",
    )


class TestBatchesViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, staff_client, get_response):
        return get_response

    list_url = lambda_fixture(lambda: url_for("internal_api:batch-list"))

    detail_url = lambda_fixture(lambda id: url_for("internal_api:batch-detail", id=id))

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        pass

    class TestDetail(UsesGetMethod, UsesDetailEndpoint, Returns200):
        id = static_fixture(1)

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        data = static_fixture(
            {
                "supplier": 1,
            }
        )

        def test_add_to_warehouse_record(self, json, client):
            batch_id = json["id"]

            result = client.patch(
                url_for(
                    "internal_api:warehouserecord-detail",
                    shop_id=1,
                    warehouse_id=3,
                    id=3,
                ),
                data={"batch": batch_id},
            )
            assert result.status_code == status.HTTP_200_OK

            result = client.patch(
                url_for(
                    "internal_api:warehouserecord-detail",
                    shop_id=1,
                    warehouse_id=1,
                    id=1,
                ),
                data={"batch": batch_id},
            )
            assert result.status_code == status.HTTP_400_BAD_REQUEST

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
        Path(request.fspath).parent / "fixtures" / "suppliers.json",
    )


class TestSupplierViewSet(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, staff_client, get_response):
        return get_response

    list_url = lambda_fixture(lambda: url_for("internal_api:supplier-list"))

    detail_url = lambda_fixture(
        lambda id: url_for("internal_api:supplier-detail", id=id)
    )

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        def test_count_suppliers(self, json):
            # archived suppliers must be filtered out
            assert len(json["results"]) == 1

    class TestSearchList(UsesGetMethod, UsesListEndpoint, Returns200):
        list_url = lambda_fixture(
            lambda: url_for("internal_api:supplier-list") + "?s=555"
        )

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        data = static_fixture(
            {
                "name": "Test Supplier",
                "phone_numbers": [
                    "+77010011100",
                    "+77010011101",
                ],
            }
        )

    class TestDetail(UsesGetMethod, UsesDetailEndpoint, Returns200):
        id = static_fixture(1)

from pathlib import Path

import pytest
from django.core.management import call_command
from pytest_drf import (
    Returns200,
    UsesDetailEndpoint,
    UsesGetMethod,
    UsesListEndpoint,
    ViewSetTest,
)
from pytest_drf.util import url_for
from pytest_lambda import lambda_fixture, static_fixture


@pytest.fixture
def django_db_setup(request, django_db_setup, django_db_blocker):
    # load a fixture from current directory
    with django_db_blocker.unblock():
        call_command(
            "loaddata",
            Path(request.fspath).parent / "fixtures" / "production.json",
        )
    yield
    with django_db_blocker.unblock():
        call_command("flush", "--no-input")


class TestDailyMenuViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, get_response):
        # this test set is going to use database
        return get_response

    list_url = lambda_fixture(lambda: url_for("production:dailymenuplan-list"))

    detail_url = lambda_fixture(
        lambda menu_id: url_for("production:dailymenuplan-detail", menu_id)
    )

    class TestList(
        UsesGetMethod,
        UsesListEndpoint,
        Returns200,
    ):
        # check if list endpoint returns 200
        pass

    class TestDetail(
        UsesGetMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        menu_id = static_fixture(2)

    class TestLayout(
        UsesGetMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        detail_url = lambda_fixture(
            lambda menu_id: url_for("production:dailymenuplan-layout", menu_id)
        )
        menu_id = static_fixture(2)

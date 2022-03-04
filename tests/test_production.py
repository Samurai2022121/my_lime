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
def django_db_setup(request, django_db_setup, django_db_blocker):
    # load a fixture from current directory
    with django_db_blocker.unblock():
        call_command(
            "loaddata",
            Path(request.fspath).parent / "fixtures" / "users.json",
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

    class TestPost(
        UsesPostMethod,
        UsesListEndpoint,
        Returns201,
    ):
        data = static_fixture(
            {
                "shop": 1,
                "author": 1,
                "menu_dishes": [
                    {
                        "dish": 2,
                        "quantity": 10,
                    },
                    {
                        "dish": 3,
                        "quantity": 5,
                    },
                ],
            }
        )

    class TestLayout(
        UsesGetMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        detail_url = lambda_fixture(
            lambda menu_id: url_for("production:dailymenuplan-layout", menu_id)
        )
        menu_id = static_fixture(2)

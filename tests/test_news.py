import pytest
from pytest_drf import Returns200, UsesGetMethod, UsesListEndpoint
from pytest_drf.util import url_for
from pytest_lambda import lambda_fixture

from utils.views_utils import ViewSetTest


class TestNewsViewSet(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, get_response):
        return get_response

    list_url = lambda_fixture(lambda: url_for("news:news-list"))

    class TestList(UsesListEndpoint, UsesGetMethod, Returns200):
        pass

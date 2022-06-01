from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command


@pytest.fixture(scope="module")
def wojak(request):
    with open(Path(request.fspath).parent / "files" / "wojak.jpg", "rb") as p:
        return SimpleUploadedFile("wojak.jpg", p.read(), content_type="image/jpeg")


@pytest.fixture(scope="module")
def pepe(request):
    with open(Path(request.fspath).parent / "files" / "pepe.jpg", "rb") as p:
        return SimpleUploadedFile("pepe.jpg", p.read(), content_type="image/jpeg")


@pytest.fixture(scope="module", autouse=True)
def django_db_setup(request, django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        # make user database available for all tests
        call_command(
            "loaddata",
            Path(request.fspath).parent / "fixtures" / "users.json",
        )
        yield
        # cleanup
        call_command("flush", "--no-input")


@pytest.fixture
def admin_client(client, django_user_model):
    admin = django_user_model.objects.get(email="admin@localhost")
    client.force_login(admin)
    return client


@pytest.fixture
def staff_client(client, django_user_model):
    admin = django_user_model.objects.get(email="staff@localhost")
    client.force_login(admin)
    return client


@pytest.fixture
def authenticated_client(client, django_user_model):
    user = django_user_model.objects.get(email="user@localhost")
    client.force_login(user)
    return client

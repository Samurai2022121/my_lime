from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.fixture(scope="module")
def wojak(request):
    with open(Path(request.fspath).parent / "files" / "wojak.jpg", "rb") as p:
        return SimpleUploadedFile("wojak.jpg", p.read(), content_type="image/jpeg")


@pytest.fixture(scope="module")
def pepe(request):
    with open(Path(request.fspath).parent / "files" / "pepe.jpg", "rb") as p:
        return SimpleUploadedFile("pepe.jpg", p.read(), content_type="image/jpeg")

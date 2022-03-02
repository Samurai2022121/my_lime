import sys
from io import BytesIO
from random import randint

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import RegexValidator
from django.db import models
from PIL import Image

phone_regex = RegexValidator(
    regex=r"^\+?\d{9,15}$",
    message='Phone number must be entered in the format: "+999999999". '
    "Up to 15 digits allowed.",
)


class Timestampable(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class ListDisplayAllModelFieldsAdminMixin(object):
    def __init__(self, model, admin_site):
        self.list_display = [
            field.name for field in model._meta.fields if field.name != "id"
        ]
        super(ListDisplayAllModelFieldsAdminMixin, self).__init__(model, admin_site)


class Round(models.Func):
    function = "ROUND"
    template = "%(function)s(%(expressions)s, 2)"


def compress_image(image, sizes, field, image_format):
    im = Image.open(image)
    output = BytesIO()
    im = im.resize(sizes)
    try:
        im.save(output, format=image_format[0], quality=70)
        output.seek(0)
        compressed_image = InMemoryUploadedFile(
            output,
            field,
            f"{image.name.split('.')[0]}_{sizes[0]}.{image_format[0]}",
            f"image/{image_format[1]}",
            sys.getsizeof(output),
            None,
        )
    except Exception as e:
        print(e)
        im.save(output, format="PNG", quality=70)
        output.seek(0)
        compressed_image = InMemoryUploadedFile(
            output,
            field,
            f"{image.name.split('.')[0]}_{sizes[0]}.png",
            "image/png",
            sys.getsizeof(output),
            None,
        )
    return compressed_image


def generate_new_password():
    return str(randint(10000, 99999))


class classproperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

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


class Enumerable(models.Model):
    """
    If a document number is not provided, generate one.
    """

    NUMBER_PREFIX = ""
    NUMBER_DIGITS = 8

    number = models.CharField("номер", max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk is None and not self.number:
            new_number = 1
            for latest_number in (
                self._meta.model.objects.filter(
                    number__startswith=self.NUMBER_PREFIX,
                )
                .order_by("-number")
                .values_list("number", flat=True)
                .iterator(chunk_size=1)
            ):
                try:
                    new_number = int(latest_number.lstrip(self.NUMBER_PREFIX)) + 1
                    break
                except ValueError:
                    pass

            self.number = self.NUMBER_PREFIX + str(new_number).zfill(self.NUMBER_DIGITS)
        super().save(*args, **kwargs)

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
    base_width = sizes[0]
    w_percent = base_width / float(im.size[0])
    h_size = int((float(im.size[1]) * float(w_percent)))
    image_name = f"{image.name.split('.')[0]}_{sizes[0]}.{image_format[0]}"

    output = BytesIO()
    im = im.resize((base_width, h_size))
    try:
        im.save(output, format=image_format[0])
        output.seek(0)
        image = InMemoryUploadedFile(
            output,
            field,
            image_name,
            f"image/{image_format[1]}",
            sys.getsizeof(output),
            None,
        )
    except Exception as e:
        print(e)

    return image


def generate_new_password():
    return str(randint(10000, 99999))


class classproperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

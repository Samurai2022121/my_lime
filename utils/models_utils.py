import sys
from io import BytesIO
from random import randint
from typing import Literal

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import RegexValidator
from django.db.models import (
    CharField,
    DateTimeField,
    Func,
    JSONField,
    Model,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
)
from PIL import Image

phone_regex = RegexValidator(
    regex=r"^\+?\d{9,15}$",
    message='Phone number must be entered in the format: "+999999999". '
    "Up to 15 digits allowed.",
)


class Timestampable(Model):
    created_at = DateTimeField(auto_now_add=True, editable=False)
    updated_at = DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class Enumerable(Model):
    """
    If a document number is not provided, generate one.
    """

    NUMBER_PREFIX = ""
    NUMBER_DIGITS = 8

    number = CharField("номер", max_length=255, unique=True, blank=True)

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


class Round(Func):
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


def build_offer_subquery(
    sqs: QuerySet,
    by: Literal["condition", "benefit"],
    outer: str = "pk",
) -> QuerySet:
    by += "__range__"
    return (
        sqs.filter(
            Q(**{f"{by}includes_all": True})
            | Q(**{f"{by}include_product_units": OuterRef(outer)})
            | Q(**{f"{by}include_products__units": OuterRef(outer)})
            | Q(**{f"{by}include_categories__products__units": OuterRef(outer)})
        )
        .exclude(
            Q(**{f"{by}exclude_product_units": OuterRef(outer)})
            | Q(**{f"{by}exclude_products__units": OuterRef(outer)})
            | Q(**{f"{by}exclude_categories__products__units": OuterRef(outer)})
        )
        .order_by("pk")
        .distinct("pk")
    )


class LiteralJSONField(JSONField):
    """Returns list or dict instead of bytes."""

    def from_db_value(self, value, expression, connection):
        return value


class ArrayJSONSubquery(Subquery):
    """Allows a subquery to return an array of rows instead of array of values."""

    template = (
        "(SELECT array_to_json(coalesce(array_agg(row_to_json(_subquery)),"
        " array[]::json[])) FROM (%(subquery)s) _subquery)"
    )
    output_field = LiteralJSONField()


class JSONSubquery(Subquery):
    """Allows a subquery to return a whole row instead of one value."""

    template = "(SELECT row_to_json(_subquery) FROM (%(subquery)s) _subquery)"
    output_field = LiteralJSONField()


class SuperclassMixin:
    @classproperty
    @classmethod
    def SUBCLASS_OBJECT_CHOICES(cls):
        """All known subclasses, keyed by a unique name per class."""
        return {
            rel.name: rel.related_model
            for rel in cls._meta.related_objects
            if rel.parent_link
        }

    @classproperty
    @classmethod
    def SUBCLASS_CHOICES(cls):
        """Available subclass choices, with nice names."""
        return [
            (name, model._meta.verbose_name)
            for name, model in cls.SUBCLASS_OBJECT_CHOICES.items()
        ]

    @classmethod
    def SUBCLASS(cls, name):
        """Given a subclass name, return the subclass."""
        return cls.SUBCLASS_OBJECT_CHOICES.get(name, cls)

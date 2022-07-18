from keyword import iskeyword
from string import ascii_letters, digits
from typing import Tuple

from model_utils.choices import Choices as BaseChoices

ALLOWED_FIRST_CHARS = "_" + ascii_letters
ALLOWED_CHARS = ALLOWED_FIRST_CHARS + digits


class Choices(BaseChoices):
    """Makes choice identifier a valid Python identifier."""

    def _store(self, triple: Tuple[str, str, str], *args, **kwargs):
        # `triple` represents a single choice. At this point each `triple` consists of
        # database representation [0], identifier [1], and readable name [2]
        identifier = triple[1]

        # check and replace each invalid character with underscore
        if not identifier.isidentifier():
            first, rest = identifier[0], identifier[1:]
            first = first if first in ALLOWED_FIRST_CHARS else "_"
            rest = "".join(ch if ch in ALLOWED_CHARS else "_" for ch in rest)
            identifier = first + rest

        # prevent clashing with Python keywords (no keyword starts with underscore)
        if iskeyword(identifier):
            identifier = "_" + identifier

        triple = triple[0], identifier, triple[2]
        super()._store(triple, *args, **kwargs)

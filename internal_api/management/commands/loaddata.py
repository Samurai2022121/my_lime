import os
import warnings
from itertools import chain, islice

from django.core import serializers
from django.core.management.base import CommandError
from django.core.management.commands.loaddata import Command as BaseCommand
from django.core.management.commands.loaddata import humanize
from django.db import transaction


def iter_chunks(iterable, size):
    """
    Splits iterable in an iterable of iterables, consuming each item from
    the original sequence as late as possible.

    Taken from the comments to https://stackoverflow.com/a/24527424/10424832 .
    """
    iterator = iter(iterable)
    for first in iterator:
        rest = islice(iterator, size - 1)
        yield chain([first], rest)
        next(islice(rest, size - 1, None), None)


class Command(BaseCommand):
    help = "An improved version of Django's 'loaddata' command."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_progress = False

    def handle(self, *fixture_labels, **options):
        self.show_progress = options["verbosity"] >= 3
        super().handle(*fixture_labels, **options)

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--chunk-size",
            default=2000,
            type=int,
            help="A maximum number of fixture objects saved per transaction",
        )

    def load_chunk(self, chunk, obj_count, loaded_count):
        """Loads a chunk of fixtures."""
        with transaction.atomic(using=self.using):
            for obj in chunk:
                obj_count += 1
                if self.save_obj(obj):
                    loaded_count += 1
                    if self.show_progress:
                        self.stdout.write(
                            f"\rProcessed {loaded_count} objects.",
                            ending="",
                        )
            return obj_count, loaded_count

    def load_label(self, fixture_label, chunk_size=2000):
        """Loads fixtures files for a given label."""
        for fixture_file, fixture_dir, fixture_name in self.find_fixtures(
            fixture_label
        ):
            _, ser_fmt, cmp_fmt = self.parse_name(os.path.basename(fixture_file))
            open_method, mode = self.compression_formats[cmp_fmt]
            fixture = open_method(fixture_file, mode)
            self.fixture_count += 1
            objects_in_fixture = loaded_objects_in_fixture = 0
            if self.verbosity >= 2:
                self.stdout.write(
                    f"Installing {ser_fmt} fixture '{fixture_name}'"
                    f" from {humanize(fixture_dir)}."
                )
            try:
                # TODO: it is possible to conserve RAM here using `ijson`
                #       instead of Django's built-in deserializer
                objects = serializers.deserialize(
                    ser_fmt,
                    fixture,
                    using=self.using,
                    ignorenonexistent=self.ignore,
                    handle_forward_references=True,
                )
                for chunk in iter_chunks(objects, chunk_size):
                    objects_in_fixture, loaded_objects_in_fixture = self.load_chunk(
                        chunk, objects_in_fixture, loaded_objects_in_fixture
                    )
            except Exception as e:
                if not isinstance(e, CommandError):
                    e.args = (f"Problem installing fixture '{fixture_file}': {e}",)
                raise
            finally:
                fixture.close()

            if objects_in_fixture and self.show_progress:
                self.stdout.write()  # Add a newline after progress indicator.
            self.loaded_object_count += loaded_objects_in_fixture
            self.fixture_object_count += objects_in_fixture
            # Warn if the fixture we loaded contains 0 objects.
            if objects_in_fixture == 0:
                warnings.warn(
                    (
                        f"No fixture data found for '{fixture_name}'."
                        f" (File format may be invalid.)"
                    ),
                    RuntimeWarning,
                )

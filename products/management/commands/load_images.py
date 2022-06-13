from pathlib import Path

from django.contrib.postgres.aggregates import ArrayAgg
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand

from products.models import Product


class Command(BaseCommand):
    help = "Loads product images from directory."

    def add_arguments(self, parser):
        parser.add_argument(
            "image_directory",
            type=str,
            help="Directory containing the images in PNG format (*.png)",
        )

    def handle(self, image_directory, *args, **options):
        images = Path(image_directory)
        products = Product.objects.filter(is_archive=False,).annotate(
            barcodes=ArrayAgg("units__barcode"),
        )
        for product in products:
            for barcode in product.barcodes:
                for image in images.glob(f"{barcode}*.png"):
                    with open(image, "rb") as image_file:
                        product.images.create(
                            image_1000=ImageFile(image_file, name=image.name),
                        )

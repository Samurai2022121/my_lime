from typing import Tuple, Union

import pngquant
from django.conf import settings
from loguru import logger
from PIL import Image
from sorl.thumbnail.base import ThumbnailBackend as BaseBackend

PRODUCT_IMAGE_SIZE = 1000, 1000


def resize_image(path: str, size: Union[Tuple, int] = PRODUCT_IMAGE_SIZE):
    """Resizes existing image keeping its aspect ratio and optimizes its palette."""
    try:
        im = Image.open(path)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(path, "PNG")
        pngquant.quant_image(path)
    except Exception as e:
        logger.warning(f"Could not quantize {path}: {e}")


class ThumbnailBackend(BaseBackend):
    """Optimizes thumbnail using pngquant CLI utility on thumbnail file."""

    def _create_thumbnail(self, source_image, geometry_string, options, thumbnail):
        super()._create_thumbnail(source_image, geometry_string, options, thumbnail)
        thumbnail_path = settings.MEDIA_ROOT / thumbnail.name
        try:
            pngquant.quant_image(thumbnail_path)
        except Exception as e:
            logger.warning(f"Could not quantize {thumbnail_path}: {e}")

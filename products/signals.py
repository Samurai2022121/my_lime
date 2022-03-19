from copy import deepcopy

from django.db.models.signals import post_save
from django.dispatch import receiver
import pngquant

from utils.models_utils import compress_image

from .models import ProductImages


@receiver(post_save, sender=ProductImages)
def save_product_images(sender, instance=None, created=False, **kwargs):
    if created:
        with deepcopy(instance.image_1000) as temp:
            instance.image_500 = compress_image(
                temp, (500, 500), "image_500", ("png", "png")
            )
            instance.image_150 = compress_image(
                temp, (150, 150), "image_150", ("png", "png")
            )
            instance.image_1000 = compress_image(
                temp, (1000, 1000), "image_1000", ("png", "png")
            )
            instance.save()
            # TODO: Add Debug check.
            try:
                pngquant.quant_image(instance.image_1000.path)
                pngquant.quant_image(instance.image_500.path)
                pngquant.quant_image(instance.image_150.path)
            except ValueError as e:
                print(e)

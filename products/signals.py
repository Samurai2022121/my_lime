from copy import deepcopy

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ProductImages
from utils.models_utils import compress_image


@receiver(post_save, sender=ProductImages)
def save_product_images(sender, instance=None, created=False, **kwargs):
    post_save.disconnect(save_product_images, sender=sender)
    with deepcopy(instance.image_1000) as temp:
        instance.image_500 = compress_image(temp, (500, 500), 'image_500',  ('jpeg', 'jpg'))
        instance.image_150 = compress_image(temp, (150, 150), 'image_150',  ('png', 'png'))
        instance.image_1000 = compress_image(temp, (1000, 1000), 'image_1000', ('jpeg', 'jpg'))
        instance.save()
    post_save.connect(save_product_images, sender=sender)

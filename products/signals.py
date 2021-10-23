from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Product, ProductImages
from utils.models_utils import compress_image


@receiver(post_save, sender=Product)
def save_product_images(sender, instance=None, created=False, **kwargs):
    if instance.main_image:
        images = ProductImages.objects.create(
            image_1000=compress_image(instance.main_image, (1000, 1000), 'image_1000', ('jpeg', 'jpg')),
            image_500=compress_image(instance.main_image, (500, 500), 'image_500',  ('jpeg', 'jpg')),
            image_150=compress_image(instance.main_image, (150, 150), 'image_150',  ('png', 'png')),
            product_name=instance.name
        )
        instance.images = images
        instance.main_image = None
        instance.save()

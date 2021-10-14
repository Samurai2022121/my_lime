from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Product, ProductImages
from utils.models_utils import compress_image


@receiver(post_save, sender=Product)
def create_student(sender, instance=None, created=False, **kwargs):
    if instance.main_image:
        images = ProductImages.objects.create(
            image_1000=compress_image(instance.main_image, (1000, 1000), 'image_1000'),
            image_500=compress_image(instance.main_image, (500, 500), 'image_500'),
            image_150=compress_image(instance.main_image, (150, 150), 'image_150'),
        )
        images.product.add(instance)
        instance.main_image = None
        instance.save()

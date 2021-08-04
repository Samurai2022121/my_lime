from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from users.models import User


class FavouriteModelManager(models.Manager):
    def delete_favourite(self, obj, user):
        favourite = self.filter(content_type=ContentType.objects.get_for_model(obj),
                                object_id=obj.id, user=user).first()
        return favourite.delete()


class Favourite(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, related_name='favourite', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = FavouriteModelManager()

    def __str__(self):
        return self.user.name

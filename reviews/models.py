from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from users.models import User


class ContentTypeModelManager(models.Manager):
    def delete_instance(self, obj, user):
        instance = self.filter(content_type=ContentType.objects.get_for_model(obj),
                               object_id=obj.id, user=user).first()
        return instance.delete()


class Favourite(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, related_name='favourite', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ContentTypeModelManager()

    def __str__(self):
        return self.user.name


class Star(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, related_name='star', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    mark = models.PositiveIntegerField()

    objects = ContentTypeModelManager()

    def __str__(self):
        return self.user.name

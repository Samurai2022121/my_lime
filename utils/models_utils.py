from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Func
from PIL import Image

import sys
from io import BytesIO


class ListDisplayAllModelFieldsAdminMixin(object):

    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields if field.name != "id"]
        super(ListDisplayAllModelFieldsAdminMixin, self).__init__(model, admin_site)


class Round(Func):
    function = 'ROUND'
    template = '%(function)s(%(expressions)s, 2)'


def compress_image(image, sizes, field):
    im = Image.open(image)
    output = BytesIO()
    im = im.resize(sizes)
    try:
        im.save(output, format='JPG', quality=70)
        output.seek(0)
        compressed_image = InMemoryUploadedFile(output, field, f"{image.name.split('.')[0]}_{sizes[0]}.jpg",
                                                'image/jpg', sys.getsizeof(output), None)
    except Exception as e:
        print(e)
        im.save(output, format='PNG', quality=70)
        output.seek(0)
        compressed_image = InMemoryUploadedFile(output, field, f"{image.name.split('.')[0]}_{sizes[0]}.png",
                                                'image/png', sys.getsizeof(output), None)
    return compressed_image

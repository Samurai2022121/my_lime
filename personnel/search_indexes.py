from haystack import indexes

from .models import Personnel


class PersonnelIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    phone_number = indexes.CharField(model_attr="phone_number")

    def get_model(self):
        return Personnel

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

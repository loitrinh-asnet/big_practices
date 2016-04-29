from datetime import datetime
from haystack import indexes
from .models import Entry


class EntryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    published_date = indexes.DateTimeField(model_attr='published_date')

    def get_model(self):
        return Entry

    def index_queryset(self, using=None):
        """Used when the entrie index for model is update."""
        return self.get_model().objects.all()


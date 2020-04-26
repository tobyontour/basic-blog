import datetime
from haystack import indexes
from django.db.models import signals
from haystack.signals import BaseSignalProcessor

from . import models


class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='author')
    pub_date = indexes.DateTimeField(model_attr='pub_date')

    def get_model(self):
        return models.Article

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())

class ArticleOnlySignalProcessor(BaseSignalProcessor):
    def setup(self):
        signals.post_save.connect(self.handle_save, sender=models.Article)
        signals.post_delete.connect(self.handle_delete, sender=models.Article)

    def teardown(self):
        # Disconnect only for the ``Article`` model.
        signals.post_save.disconnect(self.handle_save, sender=models.Article)
        signals.post_delete.disconnect(self.handle_delete, sender=models.Article)
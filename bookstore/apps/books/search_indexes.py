from haystack import indexes
from books.models import Books

#建立类的索引类
class BooksModel(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True,use_template=True)

    def get_model(self):
        return Books

    def index_queryset(self, using=None):
        return self.get_model().object.all()

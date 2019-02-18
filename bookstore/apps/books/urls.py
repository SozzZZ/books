
from django.conf.urls import url
from .views import detail,list


urlpatterns = [
    url(r'^detail/(?P<books_id>\d+)$',detail,name='detail'),
    url(r'^detail/(?P<type_id>\d+)/(?P<page>\d+)/$', list, name='list'),
]

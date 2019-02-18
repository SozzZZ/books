
from django.conf.urls import url
from .views import add_cart,cart_count,show_cart,cart_del,cart_update

urlpatterns = [
    url(r'^count/$',cart_count,name='count'),
    url(r'^add/$', add_cart, name='add'),
    url(r'^$',show_cart,name='show'),
    url(r'^del/$', cart_del, name='delete'),
    url(r'^update/$', cart_update, name='update')
]

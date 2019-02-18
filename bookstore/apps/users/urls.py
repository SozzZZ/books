
from django.conf.urls import url
from .views import register,login,logout,user,address,order


urlpatterns = [
    url(r'^register/$',register,name='register'),
    url(r'^login/$',login,name='login'),
    url(r'^logout/$',logout,name='logout'),
    url(r'^$', user, name='user'),
    url(r'^address/$',address,name='address'),
    url(r'^order/(?P<page>\d+)?/?$', order, name='order'),
]


from django.conf.urls import url
from .views import register, login, logout, user, address, order, user_active, verify_code


urlpatterns = [
    url(r'^register/$',register,name='register'),
    url(r'^login/$',login,name='login'),
    url(r'^logout/$',logout,name='logout'),
    url(r'^$', user, name='user'),
    url(r'^address/$',address,name='address'),
    url(r'^order/(?P<page>\d+)?/?$', order, name='order'),
    url(r'^active/(?P<token>.*)/$', user_active, name='active'),
    url(r'^verifycode/$', verify_code, name='verifycode'),
]

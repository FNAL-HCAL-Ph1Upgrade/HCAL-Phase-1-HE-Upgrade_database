from django.conf.urls import url, include
from django.views.static import serve

from . import cu_views as views
from card_db.settings import MEDIA_ROOT

urlpatterns = [
    url(r'^catalog$', views.catalog, name='catalog'),
    url(r'^(?P<cu>[0-9]{1,3})/$', views.detail, name='detail'),
    url(r'^uid/(?P<cu>[a-fA-F0-9_]{4,6})/$', views.detail, name='detail'),
    url(r'^field$', views.fieldView, name='field'),
    url(r'^error$', views.error, name='error'),
    ]

from django.conf.urls.defaults import *

urlpatterns = patterns('pooled.views',
    (r'^$', 'index'),
)
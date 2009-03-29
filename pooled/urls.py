from django.conf.urls.defaults import *
from models import Player

urlpatterns = patterns('',
    (r'^$', 'pooled.views.index'),
    (r'^picks/$', 'pooled.views.pick'),
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'pooled/login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout_then_login')
)
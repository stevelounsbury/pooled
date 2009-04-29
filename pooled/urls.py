from django.conf.urls.defaults import *
from models import Player

urlpatterns = patterns('',
    (r'^$', 'pooled.views.index'),
    (r'^leaderboard/(?P<round>[0-9]{1})/$', 'pooled.views.index'),
    (r'^picks/$', 'pooled.views.pick_players'),
    (r'^picks/view/$', 'pooled.views.picks_view'),
    (r'^picks/view/(?P<username>[a-zA-Z]*)/(?P<round>[0-9]{1})/$', 'pooled.views.picks_view'),
    (r'^picks/cup/$', 'pooled.views.pick_cup'),
    (r'^autocomplete/(?P<type>[a-z]*)/$', 'pooled.views.autocomplete'),
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'pooled/login.html'}),
    (r'^register/$', 'pooled.views.user_register'),
    (r'^logout/$', 'django.contrib.auth.views.logout_then_login')
)
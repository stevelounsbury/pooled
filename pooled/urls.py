from django.conf.urls.defaults import *
from models import Player

info_dict = {
    'queryset': Player.objects.all(),
}

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.list_detail.object_list', dict(info_dict, template_name="pooled/index.html")),
)
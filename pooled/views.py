from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required

from models import *

@login_required
def index(request):
    return render_to_response('pooled/index.html', context_instance=RequestContext(request))
    
@login_required
def pick(request):
    template_to_render = "pooled/pick.html"
    try:
        current_pick_round = PickRound.objects.filter(start_date__lte=datetime.now(),
                                                  end_date__gte=datetime.now())[0]
    except:
        current_pick_round = False
        template_to_render = "pooled/picks_closed.html"
    return render_to_response(template_to_render,
                              {'current_pick_round': current_pick_round})
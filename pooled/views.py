from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required
from django.utils.simplejson.encoder import JSONEncoder

from models import *
from forms import *

@login_required
def index(request):
    return render_to_response('pooled/index.html', context_instance=RequestContext(request))
    
@login_required
def pick_players(request):
    template_to_render = "pooled/picks/make_picks.html"
    try:
        current_pick_round = PickRound.objects.filter(start_date__lte=datetime.now(),
                                                  end_date__gte=datetime.now())[0]
    except:
        return render_to_response("pooled/picks/closed.html",
                                  context_instance=RequestContext(request))
    
    user_picks = Pick.objects.filter(user=request.user,
                                     pool__id=1,
                                     round=current_pick_round.current_round)
    
    pick_form = PickForm()
    
    return render_to_response(template_to_render,
                              {'current_pick_round': current_pick_round,
                               'user_picks': user_picks,
                               'pick_form': pick_form},
                              context_instance=RequestContext(request))

@login_required
def autocomplete(request, type="team"):
    test = [
        {'id': 1, 'name': type},
        {'id': 2, 'name': "player 3"}
    ]
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(JSONEncoder().encode(test))
    return response
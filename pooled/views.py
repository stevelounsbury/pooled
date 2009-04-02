from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required
from django.core import serializers

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
    
    this_pool = Pool.objects.get(pk=1)
    
    if request.method == 'POST':
        pick_form = PickForm(request.POST)
        if pick_form.is_valid():
            player = Player.objects.get(pk=pick_form.cleaned_data['player_id'])
            existing_pick = Pick.objects.filter(
                pool=this_pool,
                pick_type=pick_form.cleaned_data['position'],
                round=current_pick_round.current_round,
                user=request.user
                )
            if existing_pick:
                existing_pick[0].player=player
                existing_pick[0].save()
            else:
                pick = Pick(pick_type=pick_form.cleaned_data['position'],
                            player=player,
                            pool=this_pool,
                            round=current_pick_round.current_round,
                            user=request.user)
                pick.save()
            pick_form = PickForm()
    else:
        pick_form = PickForm()
    
    user_picks = Pick.objects.filter(user=request.user,
                                     pool=this_pool,
                                     round=current_pick_round.current_round)
    
    return render_to_response(template_to_render,
                              {'current_pick_round': current_pick_round,
                               'user_picks': user_picks,
                               'pick_form': pick_form},
                              context_instance=RequestContext(request))

@login_required
def autocomplete(request, type="teams"):
    try:
        if type == 'teams':
            pick_type = PickType.objects.filter(pk=request.GET['pick_type'])
            queryset = Team.objects.filter(conference=pick_type[0].conference)
        elif type == 'players':
            pick_type = PickType.objects.get(pk=request.GET['pick_type'])
            team = Team.objects.get(pk=request.GET['team_id'])
            queryset = Player.objects.filter(team=team, position=pick_type.position)
        else:
            raise Http404
    except:
        raise Http404
    
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(serializers.serialize("json", queryset, fields=('id', 'name')))
    return response
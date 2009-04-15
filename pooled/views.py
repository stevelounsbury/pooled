import datetime
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.views import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db.models.signals import post_save

from models import *
from forms import *

@login_required
def index(request):
    return render_to_response('pooled/index.html', context_instance=RequestContext(request))

@login_required
def pick_cup(request):
    template_to_render = "pooled/picks/make_cup.html"
    try:
        current_pick_round = PickRound.objects.filter(start_date__lte=datetime.datetime.now(),
                                                  end_date__gte=datetime.datetime.now())[0]
        if not current_pick_round.can_pick_cup:
            raise Exception
    except:
        request.user.message_set.create(message='Cup picks closed for this round.')
        return HttpResponseRedirect("/picks/")
    
    this_pool = Pool.objects.get(pk=1)
    my_pick = False
    try:
        my_pick = CupPick.objects.filter(user=request.user, pool=this_pool)[0]
        pick_form = CupPickForm(instance=my_pick)
    except:
        pick_form = CupPickForm()
    
    if request.method == "POST":
        pick_form = CupPickForm(request.POST)
        if bool(my_pick) & pick_form.is_valid():
            my_pick.team = pick_form.cleaned_data['team']
            my_pick.save()
            request.user.message_set.create(message='Updated cup pick.')
        else:
            my_pick = CupPick()
            my_pick.team = Team.objects.get(pk=request.POST['team'])
            my_pick.user = request.user
            my_pick.pool = this_pool
            my_pick.save()
            request.user.message_set.create(message='Saved new pick.')
    
    return HttpResponseRedirect("/picks/")
    
@login_required
def pick_players(request):
    template_to_render = "pooled/picks/make_picks.html"
    try:
        current_pick_round = PickRound.objects.filter(start_date__lte=datetime.datetime.now(),
                                                  end_date__gte=datetime.datetime.now())[0]
    except:
        return render_to_response("pooled/picks/closed.html",
                                  context_instance=RequestContext(request))
    
    this_pool = Pool.objects.get(pk=1)
    
    try:
        my_pick = CupPick.objects.filter(user=request.user, pool=this_pool)[0]
        cup_pick_form = CupPickForm(instance=my_pick)
    except:
        cup_pick_form = CupPickForm()
        
    # the two form elements named id-team tend to clash a bit
    cup_pick_form.auto_id = 'cup-pick-%s'
    
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
    
    p = Pick()
    eastern_players = p.get_eastern_picks(request.user, this_pool, current_pick_round.current_round)
    western_players = p.get_western_picks(request.user, this_pool, current_pick_round.current_round)
    eastern_goalies = p.get_eastern_goalies(request.user, this_pool, current_pick_round.current_round)
    western_goalies = p.get_western_goalies(request.user, this_pool, current_pick_round.current_round)
    
    return render_to_response(template_to_render,
                              {'current_pick_round': current_pick_round,
                               'eastern_players': eastern_players,
                               'western_players': western_players,
                               'eastern_goalies': eastern_goalies,
                               'western_goalies': western_goalies,
                               'cup_pick_form': cup_pick_form,
                               'pick_form': pick_form},
                              context_instance=RequestContext(request))

@login_required
def autocomplete(request, type="teams"):
    try:
        if type == 'teams':
            pick_type = PickType.objects.filter(pk=request.GET['pick_type'])
            queryset = Team.objects.filter(conference=pick_type[0].conference, active=True)
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

def user_register(request):
    registration_form = PooledRegForm()
    
    if request.method == "POST":
        registration_form=PooledRegForm(request.POST)
        if registration_form.is_valid():
            user = User.objects.create_user(registration_form.cleaned_data['username'],
                                            registration_form.cleaned_data['email'],
                                            registration_form.cleaned_data['password1'])
            profile = user.get_profile()
            profile.favourite_team = registration_form.cleaned_data['favourite_team']
            profile.save()
            return HttpResponseRedirect("/login")
    
    return render_to_response('pooled/register.html',
                              {'registration_form': registration_form},
                              context_instance=RequestContext(request))
    
def signal_user_profile(sender, instance, created, **kwargs):
    if created==True:
        profile = PooledProfile(user=instance, favourite_team=Team.objects.all()[1])
        profile.save()
post_save.connect(signal_user_profile, sender=User)

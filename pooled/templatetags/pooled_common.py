from django import template
from django.contrib.auth.models import User
from pooled.models import PlayerStat, Pool, CupPick, LeaderboardStat, PickStats, Player, PickRound

register = template.Library()

@register.inclusion_tag('pooled/templatetags/scoring_leaders.html')
def scoring_leaders(num=5):
    leaders = PlayerStat.objects.filter(current=True)[:num]
    last_updated = leaders[0].created
    return {'leaders': leaders, 'last_updated': last_updated}

@register.inclusion_tag('pooled/templatetags/user_profile.html')
def user_profile(user):
    this_pool = Pool.objects.get(pk=1)
    try:
        cup_pick = CupPick.objects.filter(user=user, pool=this_pool)[0]
    except:
        cup_pick = False
        
    current_stat = LeaderboardStat.objects.filter(current=True, user=user)
    if current_stat.count() == 0:
        current_stat = False
    else:
        current_stat = current_stat[0]
    return {'cup_pick': cup_pick, 'current_stat': current_stat, 'user':user}

@register.inclusion_tag('pooled/templatetags/top_picks.html')
def top_picks(num=5):
    total_users_with_picks = User.objects.all().count()
    toppicks = []
    #This should be a for loop, but i couldnt get the syntax
    if PickRound.current_round > 0:
        toppicks.append(PickStats.objects.get_top_picks_summary(total_users_with_picks, 1 ))
    if PickRound.current_round > 1:
        toppicks.append(PickStats.objects.get_top_picks_summary(total_users_with_picks, 2 ))
    if PickRound.current_round > 3:
        toppicks.append(PickStats.objects.get_top_picks_summary(total_users_with_picks, 3 ))
    if PickRound.current_round > 4:
        toppicks.append(PickStats.objects.get_top_picks_summary(total_users_with_picks, 4 ))
    
    return {'toppicks': toppicks}

@register.filter
def get_range(value):
    return range(value)

@register.filter
def gt(value, arg):
    "Returns a boolean of whether the value is greater than the argument"
    return int(value) > int(arg)

@register.filter
def lt(value, arg):
    "Returns a boolean of whether the value is less than the argument"
    return value < int(arg)
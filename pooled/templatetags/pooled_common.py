from django import template
from pooled.models import PlayerStat, Pool, CupPick, PickStats

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
    return {'cup_pick': cup_pick, 'user':user}
	
@register.inclusion_tag('pooled/templatetags/top_picks.html')
def top_picks(num=5):
    toppicks = PickStats.objects.get_top_picks_summary()
    return {'toppicks': toppicks}

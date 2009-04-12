from django import template
from pooled.models import PlayerStat

register = template.Library()

@register.inclusion_tag('pooled/templatetags/scoring_leaders.html')
def scoring_leaders(num=5):
    leaders = PlayerStat.objects.filter(current=True)[:num]
    last_updated = leaders[0].created
    return {'leaders': leaders, 'last_updated': last_updated}
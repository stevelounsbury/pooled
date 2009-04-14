import os
import logging
import sys
import datetime
from optparse import make_option
from datetime import date

from django.core.management.base import AppCommand, NoArgsCommand
from pooled.models import *

class Command(AppCommand):
    help = "Updates the leaderboard for pooled"
    
    option_list = AppCommand.option_list + (
        make_option('--debug', action='store_true', dest='debug',
                    help='Dont actually update the leaderboard, just test'),
    )
    
    debug = False

    def handle_app(self, app, **options):
        self.debug = options.get('debug', False)
        
        # we're updating the stats, so all the old stats are not current
        if not self.debug:
            print "Setting all Player and Goalie stats to old."

        for user in User.objects.all():
            print user
            for pick in user.pick_set.all():
                if pick.player.position.upper() == 'G':
                    print self.get_goalie_stats(pick.player, date(2009, 4, 11))
                else:
                    print self.get_player_stats(pick.player, date(2009, 4, 11))


    def get_player_stats(self, player, previous_round):
        current = player.playerstat_set.filter(current=True)[0]
        if not previous_round:
            return {'g': current.g, 'a': current.a, 'gwg': current.gwg}
        else:
            last_round = player.playerstat_set.filter(created__range=(datetime.datetime.combine(previous_round, datetime.time.min), datetime.datetime.combine(previous_round, datetime.time.max)))[0]
            return {'g': current.g-last_round.g,
                    'a': current.a-last_round.a,
                    'gwg': current.gwg-last_round.gwg}

    def get_goalie_stats(self, player, previous_round):
        current = player.goaliestat_set.filter(current=True)[0]
        if not previous_round:
            return {'w': current.w, 'so': current.so}
        else:
            last_round = player.goaliestat_set.filter(created__range=(datetime.datetime.combine(previous_round, datetime.time.min), datetime.datetime.combine(previous_round, datetime.time.max)))[0]
            return {'w': current.w-last_round.w,
                    'so': current.so-last_round.so}

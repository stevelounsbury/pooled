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
        this_pool = Pool.objects.get(pk=1)
        
        round = Round.objects.filter(active=True)
        if round.count() != 1:
            print "ERROR: Either there is no current round set or there is more than one active round, please check."
            return
        
        round = round[0]
        print "Active round is %s" % round
        if round.previous is None:
            print "    This round does not have a previous round."
        else:
            print "    The previous round was %s" % round.previous
        
        scoring_model = PointsScheme.objects.filter(current=True)
        if scoring_model.count() == 0:
            print "Oops, couldn't find a current points scheme. Please create one"
            return
        scoring_model = scoring_model[0]
        # we're updating the stats, so all the old stats are not current
        if not self.debug:
            LeaderboardStat.objects.all().update(current=False)
        print "Updating pool stats, using the following scoring model:"
        print scoring_model

        for user in User.objects.all():
            print user
            if round.previous is None:
                total_stats = {'gwg': 0, 'g': 0, 'a': 0, 'so': 0, 'w': 0, 'pts': 0}
            else:
                # if we have a previous round, starting points are those at the
                # end of the previous round.
                last_round = user.pick_set.filter(created__range=(datetime.datetime.combine(round.previous.end_date, datetime.time.min),
                                                                  datetime.datetime.combine(round.previous.end_date, datetime.time.max)))
            
            for pick in user.pick_set.all():
                if pick.player.position.upper() == 'G':
                    stat = self.get_goalie_stats(pick.player, round.previous)
                    if stat:
                        total_stats['so'] += stat['so']
                        total_stats['w'] += stat['w']
                else:
                    stat = self.get_player_stats(pick.player, round.previous)
                    if stat:
                        total_stats['gwg'] += stat['gwg']
                        total_stats['g'] += stat['g']
                        total_stats['a'] += stat['a']
                        
            total_stats['pts'] += total_stats['gwg'] * scoring_model.gwg
            total_stats['pts'] += total_stats['g'] * scoring_model.g
            total_stats['pts'] += total_stats['a'] * scoring_model.a
            total_stats['pts'] += total_stats['w'] * scoring_model.win
            total_stats['pts'] += total_stats['so'] * scoring_model.so
            if self.debug:
                print total_stats
            else:
                stat = LeaderboardStat(user=user,
                                       pool=this_pool,
                                       round=round,
                                       points_scheme=scoring_model,
                                       current=True,
                                       is_final=False,
                                       is_leader=False,
                                       is_worst=False,
                                       change=0,
                                       rank=0,
                                       points_behind=0,
                                       g=total_stats['g'],
                                       a=total_stats['a'],
                                       gwg=total_stats['gwg'],
                                       win=total_stats['w'],
                                       so=total_stats['so'],
                                       pts=total_stats['pts'])
                stat.save()
        
        all_stats = LeaderboardStat.objects.filter(current=True).order_by('-pts')
        all_stats[0].is_leader=True
        all_stats[all_stats.count()-1].is_worst=True
        
        leader = all_stats[0]
        
        i = 0
        for stat in all_stats:
            i = i+1
            stat.rank = i
            stat.points_behind = leader.pts - stat.pts
            if leader.pts == stat.pts:
                stat.is_leader = True
            old_stat = LeaderboardStat.objects.filter(user=stat.user, current=False).order_by('-created')
            if old_stat.count() == 0:
                stat.change = 0
            else:
                old_stat = old_stat[0]
                stat.change = old_stat.rank - stat.rank
            stat.save()

    def get_player_stats(self, player, previous_round):
        current = player.playerstat_set.filter(current=True)
        if current.count() == 0:
            print "WARN :: Could not find a current player stat for %s" % player.name
            return False
        current = current[0]
        if previous_round is None:
            return {'g': current.g, 'a': current.a, 'gwg': current.gwg}
        else:
            last_round = player.playerstat_set.filter(created__range=(datetime.datetime.combine(previous_round.end_date, datetime.time.min),
                                                                      datetime.datetime.combine(previous_round.end_date, datetime.time.max)))
            if last_round.count() == 0:
                print "ERROR :: Could not find last stat for player: %s" % player.name
                return False
            else:
                last_round = last_round[0]
            
            return {'g': current.g-last_round.g,
                    'a': current.a-last_round.a,
                    'gwg': current.gwg-last_round.gwg}

    def get_goalie_stats(self, player, previous_round):
        current = player.goaliestat_set.filter(current=True)
        if current.count() == 0:
            print "WARN :: Could not find a current goalie stat for %s" % player.name
            return False
        current = current[0]
        if previous_round is None:
            return {'w': current.w, 'so': current.so}
        else:
            last_round = player.goaliestat_set.filter(created__range=(datetime.datetime.combine(previous_round.end_date, datetime.time.min),
                                                                      datetime.datetime.combine(previous_round.end_date, datetime.time.max)))
            if last_round.count() == 0:
                print "ERROR :: Could not find last stat for goalie: %s" % player.name
                return False
            else:
                last_round = last_round[0]
            return {'w': current.w-last_round.w,
                    'so': current.so-last_round.so}

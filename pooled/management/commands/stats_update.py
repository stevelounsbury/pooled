import os
import logging
import sys
from mechanize import Browser
from BeautifulSoup import BeautifulSoup
from optparse import make_option

from django.core.management.base import AppCommand, NoArgsCommand
from pooled.models import *

logger = logging.getLogger("mechanize")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

PLAYER_TABLE_OFFSET = 7
GOALIE_TABLE_OFFSET = 6

class Command(AppCommand):
    help = "Updates the player and goalie stats for pooled"
    
    option_list = AppCommand.option_list + (
        make_option('--debug', action='store_true', dest='debug',
                    help='Dont actually fetch the stats update, just test'),
    )
    
    debug = False

    def handle_app(self, app, **options):
        self.debug = options.get('debug', False)
        print self.debug
        player_stats = self.get_mechanized_browser("http://www.sportsnet.ca/hockey/nhl/stats/playoffs/skaters")
        goalie_stats = self.get_mechanized_browser("http://www.sportsnet.ca/hockey/nhl/stats/playoffs/goalies")
        # we're updating the stats, so all the old stats are not current
        if not self.debug:
            print "Setting all Player and Goalie stats to old."
            PlayerStat.objects.all().update(current=False)
            GoalieStat.objects.all().update(current=False)
        
        limit = False
        if self.debug:
            limit = 1
        self.iterate_pages(player_stats, self.get_player_stats, limit)
        self.iterate_pages(goalie_stats, self.get_goalie_stats, limit)
        
        if not self.debug:
            updated = GoalieStat.objects.filter(current=True)
            print 'Updated a total of %d goalies' % updated.count()
            updated = PlayerStat.objects.filter(current=True)
            print 'Updated a total of %d players' % updated.count()

    def get_player(self, col):
        # Figure out which player we are dealing
        # with what position they place, and which
        # team they are on.
        links = col[0].findAll('a')
        player_name = links[0].string.strip()
        player_slug = links[0]['href'].strip('/').rsplit('/')[-1]
        team = links[1].string.strip()
        team_slug = links[1]['href'].strip('/').rsplit('/')[-1]
        pos = col[1].string.strip()
        
        p = Player.objects.filter(sportsnet=player_slug)
        if (p.count() == 0):
            t = Team.objects.filter(slug=team_slug)
            if (t.count() == 0):
                t = Team(name=team, slug=team_slug)
                t.save()
            else:
                t = t[0]
            p = Player(team=t, name=player_name, nhlcom=1, position=pos, sportsnet=player_slug)
            p.save()
        else:
            p=p[0]
        
        return p
    
    def get_player_stats(self, soup):
        table = soup.findAll('table')[PLAYER_TABLE_OFFSET]
        records = list()
        for tr in table.findAll('tr')[1:]:
            col = tr.findAll('td')
            player = self.get_player(col)
            
            gp = int(col[2].string.strip())
            g = int(col[3].string.strip())
            a = int(col[4].string.strip())
            pts = int(col[5].string.strip())
            plus_minus = int(col[7].string.strip())
            ppg = int(col[8].string.strip())
            ppa = int(col[10].string.strip())
            ppp = int(col[11].string.strip())
            shg = int(col[12].string.strip())
            gwg = int(col[13].string.strip())
            pim = int(col[14].string.strip())
            sh = int(col[15].string.strip())
            
            result = (player.name, g, a, pts)
            if self.debug:
                print "%s: %d g, %d assists, %d points" % result
            else:
                stat = PlayerStat(
                    player=player,
                    current=True,
                    gp=gp,
                    g=g,
                    a=a,
                    pts=pts,
                    plus_minus=plus_minus,
                    ppg=ppg,
                    ppa=ppa,
                    ppp=ppp,
                    shg=shg,
                    gwg=gwg,
                    pim=pim,
                    sh=sh)
                stat.save()
            
    def get_goalie_stats(self, soup):
        table = soup.findAll('table')[GOALIE_TABLE_OFFSET]
        records = list()
        for tr in table.findAll('tr')[1:]:
            col = tr.findAll('td')
            player = self.get_player(col)
            
            gp = int(col[2].string.strip())
            w = int(col[3].string.strip())
            l = int(col[4].string.strip())
            otl = int(col[5].string.strip())
            gaa = col[6].string.strip()
            save_pct = col[7].string.strip()
            so = int(col[8].string.strip())
            en = int(col[9].string.strip())
            ga = int(col[10].string.strip())
            sha = int(col[11].string.strip())
            starts = int(col[12].string.strip())
            
            result = (player.name, w, l, so)
            if self.debug:
                print "%s: %d wins, %d losses, %d so" % result
            else:
                stat = GoalieStat(
                    player=player,
                    current=True,
                    gp=gp,
                    w=w,
                    l=l,
                    otl=otl,
                    gaa=gaa,
                    save_pct=save_pct,
                    so=so,
                    en=en,
                    ga=ga,
                    sha=sha,
                    starts=starts)
                stat.save()
    
    def iterate_pages(self, mech, callback, limit=False):
        i = 0
        while True:
            response = mech.response()
            html = response.read()
            soup = BeautifulSoup(html)
            callback(soup)
            i+=1
            print "Processed page %d" % i
            if limit != False and limit>=i:
                break
            try:
                mech.follow_link(text_regex="Next page")
            except:
                print 'done.'
                break
            
    def get_mechanized_browser(self, url):
        mech = Browser()
        mech.set_handle_robots(False)
        mech.open(url)
        assert mech.viewing_html()
        return mech

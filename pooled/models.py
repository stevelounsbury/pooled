from django.db import models
from django.contrib.auth.models import User 
# Create your models here.

CONFERENCE_CHOICES = (
    ('E', 'Eastern Conference'),
    ('W', 'Western Conference'),
)
POSITION_CHOICES = (
    ('C', 'Center'),
    ('G', 'Goalie'),
    ('D', 'Defense'),
    ('RW', 'Right Wing'),
    ('LW', 'Left Wing'),
)

class Team(models.Model):
    name = models.CharField(max_length=128)
    image = models.CharField(max_length=128)
    slug = models.CharField(max_length=128)
    conference = models.CharField(max_length=1, choices=CONFERENCE_CHOICES)
    active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.name

class Player(models.Model):
    class Meta:
        ordering = ['name']
    team = models.ForeignKey(Team)
    name = models.CharField(max_length=128)
    position = models.CharField(max_length=8)
    nhlcom = models.IntegerField('NHL.com player id')
    sportsnet = models.CharField('Sportsnet.ca slug', max_length=128)
    
    def __unicode__(self):
        return self.name

class Round(models.Model):
    name = models.CharField(max_length=30)
    active = models.BooleanField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    def get_current_round(self):
        return self.objects.filter(current=True)[0]
        
    def __unicode__(self):
        return self.name

class Pool(models.Model):
    name = models.CharField(max_length=30)
    registration_open = models.BooleanField()
    picks_open = models.DateTimeField()
    picks_closed = models.DateTimeField()
    
    def __unicode__(self):
        return self.name

class GoalieStat(models.Model):
    player = models.ForeignKey(Player)
    current = models.BooleanField()
    gp = models.IntegerField('games played')
    w = models.IntegerField('wins')
    l = models.IntegerField('losses')
    otl = models.IntegerField('overtime losses')
    gaa = models.CharField(name='goals against average', max_length=10)
    save_pct = models.CharField(name='save percentage', max_length=10)
    so = models.IntegerField('shutouts')
    en = models.IntegerField('empty net goals against')
    ga = models.IntegerField('goals against')
    sha = models.IntegerField('shots against')
    starts = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return "%s, %s: %d wins" % (self.player.name, self.created.strftime("%B %d %Y"), self.w)
        
class PlayerStat(models.Model):
    player = models.ForeignKey(Player)
    current = models.BooleanField()
    gp = models.IntegerField('games played')
    g = models.IntegerField('goals')
    a = models.IntegerField('assists')
    pts = models.IntegerField('points')
    plus_minus = models.IntegerField()
    ppg = models.IntegerField('powerplay goals')
    ppa = models.IntegerField('powerplay assists')
    ppp = models.IntegerField('powerplay points')
    shg = models.IntegerField('short-handed goals')
    gwg = models.IntegerField('game winning goals')
    pim = models.IntegerField('penalty minutes')
    sh = models.IntegerField('shots')
    created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return "%s, %s: %d pts" % (self.player.name, self.created.strftime("%B %d %Y"), self.pts)

class PickType(models.Model):
    name = models.CharField(max_length=30)
    position = models.CharField(max_length=8, choices=POSITION_CHOICES)
    conference = models.CharField(max_length=1, choices=CONFERENCE_CHOICES)
    
    def __unicode__(self):
        return self.name

class Pick(models.Model):
    user = models.ForeignKey(User)
    player = models.ForeignKey(Player)
    round = models.ForeignKey(Round)
    pool = models.ForeignKey(Pool)
    pick_type = models.ForeignKey(PickType)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    unique_together = ('user', 'round', 'pool', 'pick_type')
    
    def __unicode__(self):
        return "%s picked %s in %s" % (self.user.username, self.player.name, self.round.name)
    
    def get_eastern_picks(self, user, pool, round):
        return self.get_conference_players(user, pool, round, 'E')
    def get_eastern_goalies(self, user, pool, round):
        return self.get_conference_goalies(user, pool, round, 'E')
    def get_western_picks(self, user, pool, round):
        return self.get_conference_players(user, pool, round, 'W')
    def get_western_goalies(self, user, pool, round):
        return self.get_conference_goalies(user, pool, round, 'W')
    
    def get_conference_players(self, user, pool, round, conference):
        return Pick.objects.filter(
            user=user,
            round=round,
            pool=pool,
            player__team__conference=conference,
        ).exclude(player__position='G')
    def get_conference_goalies(self, user, pool, round, conference):
        return Pick.objects.filter(
            user=user,
            round=round,
            pool=pool,
            player__team__conference=conference,
            player__position='G'
        )

class CupPick(models.Model):
    user = models.ForeignKey(User)
    team = models.ForeignKey(Team)
    pool = models.ForeignKey(Pool)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return "%s picked %s to win" % (self.user.username, self.team.slug.upper())

class PickRound(models.Model):
    current_round = models.ForeignKey(Round)
    notes = models.TextField(blank=True)
    can_pick_cup = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

class PooledProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    favourite_team = models.ForeignKey(Team, blank=True)
    
    def __unicode__(self):
        return "%s's profile" % self.user.username

class PointsScheme(models.Model):
    pool = models.ForeignKey(Pool)
    current = models.BooleanField()
    g = models.IntegerField('points for a goal')
    a = models.IntegerField('points for an assist')
    gwg = models.IntegerField('extra points for a game winning goal')
    so = models.IntegerField('extra points for a shutout')
    win = models.IntegerField('points for a win')
    created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return "%s per goal, %s per assist, %s extra for gwg, %s for win, %s extra for shutout" % (self.g, self.a, self.gwg, self.win, self.so)
    
class LeaderboardStat(models.Model):
    user = models.ForeignKey(User)
    pool = models.ForeignKey(Pool)
    points_scheme = models.ForeignKey(PointsScheme)
    current = models.BooleanField()
    is_leader = models.BooleanField()
    is_worst = models.BooleanField()
    change = models.IntegerField('position change')
    rank = models.IntegerField()
    points_behind = models.IntegerField('points behind leader')
    g = models.IntegerField('goals')
    a = models.IntegerField('assists')
    gwg = models.IntegerField('game winning goals')
    so = models.IntegerField('shut outs')
    win = models.IntegerField('wins')
    pts = models.IntegerField('points')
    created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return "%s had %spts on %s" % (self.user.username, self.pts, self.created)
    

from django.db import models
from django.contrib.auth.models import User 
# Create your models here.

class Team(models.Model):
    name = models.CharField(max_length=128)
    image = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.name

class Player(models.Model):
    team = models.ForeignKey(Team)
    name = models.CharField(max_length=128)
    position = models.CharField(max_length=8)
    nhlcom = models.IntegerField('NHL.com player id')
    sportsnet = models.CharField('Sportsnet.ca slug', max_length=128)
    
class Round(models.Model):
    name = models.CharField(max_length=30)
    active = models.BooleanField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

class Pool(models.Model):
    name = models.CharField(max_length=30)
    registration_open = models.BooleanField()
    picks_open = models.DateTimeField()
    picks_closed = models.DateTimeField()

class PlayerStat(models.Model):
    player = models.ForeignKey(Player)
    round = models.ForeignKey(Round)
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

class Pick(models.Model):
    user = models.ForeignKey(User)
    player = models.ForeignKey(Player)
    round = models.ForeignKey(Round)
    pool = models.ForeignKey(Pool)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
class CupPick(models.Model):
    user = models.ForeignKey(User)
    player = models.ForeignKey(Player)
    pool = models.ForeignKey(Pool)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

 

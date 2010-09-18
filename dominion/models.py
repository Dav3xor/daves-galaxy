from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import models
from django.core.mail import send_mail
from django.db.models import Q
from pprint import pprint
import datetime
import math
import operator
import random
import aliens
import time

SVG_SCHEMA = "http://www.w3.org/Graphics/SVG/1.2/rng/"
DISPOSITIONS = (
    (0, 'Garrison'),
    (1, 'Planetary Defense'),
    (2, 'Scout'),
    (3, 'Screen'),
    (4, 'Diplomacy'),
    (5, 'Attack'),
    (6, 'Colonize'),
    (7, 'Move'),
    (8, 'Trade'),
    (9, 'Piracy'),
    )

instrumentalitytypes = [
  {'name': 'Long Range Sensors 1',
   'type': 0,
   'description': "Increases the radius over which this planet's sensors " +
                  "can see by .5 G.U.'s.  Does not increase sensor ranges " +
                  "for fleets.",
   'requires': -1,
   'minsociety': 10,
   'upkeep': .01,
   'minupkeep': 100,
   'required':   {'people': 1000, 'food': 1000, 'steel': 150, 
                 'antimatter': 5, 'quatloos': 400, 'hydrocarbon': 500,
                 'unobtanium':0, 'krellmetal':0}},

  {'name': 'Long Range Sensors 2',
   'type': 1,
   'description': "Increases the radius over which this planet's sensors " +
                  " can see by another .5 G.U.'s beyond the added range " +
                  "given by Long Range Sensors 1.",
   'requires': 0,
   'minsociety': 20,
   'upkeep': .02,
   'minupkeep': 100,
   'required':   {'people': 1000, 'food': 1000, 'steel': 300, 
                 'antimatter': 10, 'quatloos': 600, 'hydrocarbon': 1000,
                 'unobtanium':0, 'krellmetal':0}},

  {'name': 'Trade Incentives',
   'type': 2,
   'description': "Promotes trade by reducing the price of " +
                  "commodities that are in surplus, and raising the prices of " +
                  "commodities that are needed.  The Government subsidizes the difference " +
                  "in prices through its treasury.",
   'requires': -1,
   'minsociety': 1,
   'upkeep': .01,
   'minupkeep': 50,
   'required':   {'people': 100, 'food': 100, 'steel': 10, 
                 'antimatter': 0, 'quatloos': 100,
                 'unobtanium':0, 'krellmetal':0}},

  {'name': 'Regional Government',
   'type': 3,
   'description': "Allows this planet to collect taxes from it's neighbors.  This tax is " +
                  "fixed at 5%, and please note that if you set all your planets as " +
                  "regional goverments, you're just moving a lot of money around with no " +
                  "advantage.",
   'requires': -1,
   'minsociety': 30,
   'upkeep': .02,
   'minupkeep': 100,
   'required':   {'people': 5000, 'food': 5000, 'steel': 500, 
                 'antimatter': 200, 'quatloos': 10000, 'hydrocarbon': 1000,
                 'unobtanium':0, 'krellmetal':0}},

  {'name': 'Mind Control',
   'type': 4,
   'description': "Every inhabitant of this planet is issued an antenna " +
                  "beanie that turns them into a mindless automaton.  The " + 
                  "consequences of this enbeaniement are that the level of " +
                  "society on the planet does not change.  Naturally this " +
                  "technology is not looked upon favorably by the international " +
                  "community.  Also, certain elements in society resist the wearing " +
                  "of their handsome new headgear, and will have to be...eliminated.",
   'requires': -1,
   'minsociety': 40,
   'upkeep': .2,
   'minupkeep': 100,
   'required':   {'people': 20000, 'food': 500, 'steel': 2000, 
                 'antimatter': 10, 'quatloos': 5000,
                 'unobtanium':0, 'krellmetal':0}},

  {'name': 'Matter Synth 1',
   'type': 5,
   'description': "A matter synthesizer allows you to produce the artificial " +
                  "element *Krellenium*, (Krell Metal), which is used in building " +
                  "military ships beyond the most basic types.  If you wish to build " +
                  "these kinds of ships on this planet you will also need to build a " +
                  "military base.",
   'requires': -1,
   'minsociety': 50,
   'upkeep': .025,
   'minupkeep': 250,
   'required':   {'people': 5000, 'food': 5000, 'steel': 1000, 
                 'antimatter': 500, 'quatloos': 10000,
                 'unobtanium':0, 'krellmetal':0}},

  {'name': 'Matter Synth 2',
   'type': 6,
   'description': "Adds an Unobtanium extractor to the matter synthesizer " +
                  "already located on this planet.  Unobtanium is used in " + 
                  "the production of larger military ships.",
   'requires': 5,
   'minsociety': 70,
   'upkeep': .1,
   'minupkeep': 300,
   'required':   {'people': 5000, 'food': 5000, 'steel': 2000, 
                 'antimatter': 1000, 'quatloos': 20000,
                 'unobtanium':0, 'krellmetal':0}},

  {'name': 'Military Base',
   'type': 7,
   'description': "A military base, along with a matter synthesizer, allows you " +
                  "to build larger warships on this planet.",
   'requires': 5,
   'minsociety': 60,
   'upkeep': .15,
   'minupkeep': 500,
   'required':   {'people': 2000, 'food': 2000, 'steel': 1000, 
                 'antimatter': 100, 'quatloos': 10000,
                 'unobtanium':0, 'krellmetal':0}},

  {'name': 'Slingshot',
   'type': 8,
   'description': "A slingshot gives a speed boost to any fleet leaving this planet. ",
                  
   'requires': -1,
   'minsociety': 25,
   'upkeep': .1,
   'minupkeep': 200,
   'required':   {'people': 100, 'food': 100, 'steel': 500, 
                 'antimatter': 10, 'quatloos': 1000,
                 'unobtanium':0, 'krellmetal':0}},
                 
                 
                 ]

shiptypes = {
  'scouts':           {'singular': 'scout', 'plural': 'scouts', 
                       'nice': 'Scouts',
                       'accel': .4, 'att': 1, 'def': 0,'requiresbase':False, 
                       'sense': .5, 'effrange': .5,
                       'required':
                         {'people': 5, 'food': 5, 'steel': 10, 
                         'antimatter': 1, 'quatloos': 10,
                         'unobtanium':0, 'krellmetal':0}
                      },
  'blackbirds':       {'singular': 'blackbird', 'plural': 'blackbirds', 
                       'nice': 'Blackbirds',
                       'accel': .8, 'att': 0, 'def': 10,'requiresbase':False, 
                       'sense': 1.0, 'effrange': .5,
                       'required':
                         {'people': 5, 'food': 5, 'steel': 20, 
                         'antimatter': 5, 'quatloos': 10,
                         'unobtanium':0, 'krellmetal':1}
                      },
  'arcs':             {'singular': 'arc', 'plural': 'arcs', 'nice': 'Arcs',
                       'accel': .25, 'att': 0, 'def': 2, 'requiresbase':False,
                       'sense': .2, 'effrange': .25,
                       'required':
                         {'people': 500, 'food': 1000, 'steel': 200, 
                         'antimatter': 10, 'quatloos': 200,
                         'unobtanium':0, 'krellmetal':0}
                      },

  'merchantmen':      {'singular': 'merchantman', 'plural': 'merchantmen', 
                       'nice': 'Merchantmen',
                       'accel': .28, 'att': 0, 'def': 2, 'requiresbase':False,
                       'sense': .2, 'effrange': .25,
                       'required':
                         {'people': 20, 'food': 20, 'steel': 30, 
                         'antimatter': 2, 'quatloos': 10,
                         'unobtanium':0, 'krellmetal':0}
                      },
  'bulkfreighters':   {'singular': 'bulkfreighter', 'plural': 'bulkfreighters', 
                       'nice': 'Bulk Freighters',
                       'accel': .25, 'att': 0, 'def': 2, 'requiresbase':False,
                       'sense': .2, 'effrange': .25,
                       'required':
                         {'people': 20, 'food': 20, 'steel': 100, 
                         'antimatter': 2, 'quatloos': 100,
                         'unobtanium':0, 'krellmetal':0}
                      },
  'fighters':         {'singular': 'fighter', 'plural': 'fighters', 
                       'nice': 'Fighters',
                       'accel': 0.0,
                       'att': 5, 'def': 1, 'requiresbase':True,
                       'sense': 1.0, 'effrange': 2.0,
                       'required':
                         {'people': 0, 'food': 0, 'steel': 1, 
                         'antimatter': 0, 'quatloos': 10,
                         'unobtanium':0, 'krellmetal':0}
                      },
  'frigates':         {'singular': 'frigate', 'plural': 'frigates', 
                       'nice': 'Frigates',
                       'accel': .35, 'att': 10, 'def': 5, 'requiresbase':False,
                       'sense': .4, 'effrange': 1.0,
                       'required':
                         {'people': 50, 'food': 50, 'steel': 50, 
                         'antimatter': 10, 'quatloos': 100,
                         'unobtanium':0, 'krellmetal':0}
                      },
  'subspacers':       {'singular': 'subspacer', 'plural': 'subspacers', 
                       'nice': 'Sub Spacers',
                       'accel': .3, 'att': 10, 'def': 5, 'requiresbase':True,
                       'sense': .8, 'effrange': 1.0,
                       'required':
                         {'people': 50, 'food': 50, 'steel': 50, 
                         'antimatter': 10, 'quatloos': 100,
                         'unobtanium':0, 'krellmetal':1}
                      },
  'destroyers':       {'singular': 'destroyer', 'plural': 'destroyer', 
                       'nice': 'Destroyers',
                       'accel':.32, 'att': 15, 'def': 7, 'requiresbase':True,
                       'sense': .5, 'effrange': 1.2,
                       'required':
                         {
                         'people': 70, 'food': 70, 'steel': 100, 
                         'antimatter': 12, 'quatloos': 150,
                         'unobtanium':0, 'krellmetal':0}
                      },
  'cruisers':         {'singular': 'cruiser', 'plural': 'cruisers', 
                       'nice': 'Cruisers',
                       'accel': .32, 'att': 30, 'def': 6, 'requiresbase':True,
                       'sense': .7, 'effrange': 1.8,
                       'required':
                         {
                         'people': 100, 'food': 100, 'steel': 200, 
                         'antimatter': 20, 'quatloos': 500,
                         'unobtanium':0, 'krellmetal':1}
                      },
  'battleships':      {'singular': 'battleship', 'plural': 'battleships', 
                       'nice': 'Battleships',
                       'accel': .25, 'att': 50, 'def': 10, 'requiresbase':True,
                       'sense': .7, 'effrange': 2.0,
                       'required':
                         {
                         'people': 200, 'food': 200, 'steel': 1000, 
                         'antimatter': 50, 'quatloos': 2000,
                         'unobtanium':0, 'krellmetal':3}
                      },
  'superbattleships': {'singular': 'super battleship', 'plural': 'super battleships', 
                       'nice': 'Super Battleships',
                       'accel': .24, 'att': 100, 'def': 20, 'requiresbase':True,
                       'sense': 1.0, 'effrange': 2.0,
                       'required':
                         {
                         'people': 300, 'food': 300, 'steel': 5000, 
                         'antimatter': 150, 'quatloos': 5000,
                         'unobtanium':1, 'krellmetal':5}
                      },
  'carriers':         {'singular': 'carrier', 'plural': 'carriers', 
                       'nice': 'Carriers',
                       'accel': .2, 'att': 0, 'def': 10, 'requiresbase':True,
                       'sense': 1.2, 'effrange': .5,
                       'required':
                         {
                         'people': 500, 'food': 500, 'steel': 7500, 
                         'antimatter': 180, 'quatloos': 6000,
                         'unobtanium':5, 'krellmetal':10} 
                       }
  }
productionrates = {'people':        {'baseprice': 100, 'pricemod':.003, 'nice': 'People', 
                                     'baserate': 1.12, 'socmodifier': -0.00002, 'neededupgrade': -1,
                                     'initial': 150000},
                   'quatloos':      {'baseprice': 1, 'pricemod':1.0,  'nice': 'Quatloos',
                                     'baserate': 1.0, 'socmodifier': 0.0, 'neededupgrade': -1,

                                     'initial': 1000},
                   'food':          {'baseprice': 10, 'pricemod':-.00002,  'nice': 'Food',
                                     'baserate': 1.09, 'socmodifier': -.00108, 'neededupgrade': -1,

                                     'initial': 5000},
                   'consumergoods': {'baseprice': 30, 'pricemod':.02,  'nice': 'Consumer Goods',
                                     'baserate': .9999, 'socmodifier': .0000045, 'neededupgrade': -1,

                                     'initial': 2000},
                   'steel':         {'baseprice': 100, 'pricemod':-.05,  'nice': 'Steel',
                                     'baserate': 1.001, 'socmodifier': 0.0, 'neededupgrade': -1,

                                     'initial': 500},
                   'unobtanium':    {'baseprice': 20000, 'pricemod':10000.0, 'nice': 'Unobtanium',
                                     'baserate': .99999, 'socmodifier': .00000035, 
                                     'neededupgrade': 6, #Instrumentality.MATTERSYNTH2
                                     'initial': 0},
                   'krellmetal':    {'baseprice': 10000, 'pricemod':100.0,  'nice': 'Krell Metal',
                                     'baserate': .999995, 'socmodifier':.0000008, 
                                     'neededupgrade': 5, #Instrumentality.MATTERSYNTH1
                                     'initial': 0},
                   'antimatter':    {'baseprice': 5000, 'pricemod':4.0,  'nice': 'Antimatter',
                                     'baserate': .9999, 'socmodifier': .000008, 'neededupgrade': -1,
                                     'initial': 50},
                   'hydrocarbon':   {'baseprice': 100, 'pricemod':-.009,  'nice': 'Hydrocarbon',
                                     'baserate': 1.013, 'socmodifier': -.00014, 'neededupgrade': -1,

                                     'initial': 1000}
                  }
class PlanetUpgrade(models.Model):
  planet = models.ForeignKey('Planet')
  instrumentality = models.ForeignKey('Instrumentality')
  state = models.PositiveIntegerField(default=0)
  raised = models.ForeignKey('Manifest')
  BUILDING   = 0 
  ACTIVE     = 1
  DESTROYED  = 2
  INACTIVE   = 3
  states = ['Building','Active','Destroyed','Inactive']
  def currentcost(self,commodity):
    cost = 0
    if self.state == PlanetUpgrade.BUILDING:
      onefifth = getattr(self.instrumentality.required,commodity)/5
      alreadyraised = getattr(self.raised,commodity)
      totalneeded = self.instrumentality.required
      cost = onefifth if totalneeded >= alreadyraised+onefifth else totalneeded-alreadyraised 

    elif self.state in [PlanetUpgrade.ACTIVE, PlanetUpgrade.INACTIVE]:
      cost = self.planet.nexttaxation()*self.instrumentality.upkeep
      cost = cost if cost > self.instrumentality.minupkeep else self.instrumentality.minupkeep
    return cost

  def printstate(self):
    return self.states[self.state]

  def doturn(self,report):
    """
    >>> buildinstrumentalities()
    >>> u = User(username="updoturn")
    >>> u.save()
    >>> r = Manifest(people=5000, food=1000, steel=500, quatloos=1000)
    >>> r.save()
    >>> s = Sector(key=123125,x=101,y=101)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=615, y=625, r=.1, color=0x1234)
    >>> p.save()
    >>> up = PlanetUpgrade()
    >>> up.start(p,Instrumentality.TRADEINCENTIVES)
    >>> up.save()
    >>> up.doturn([])
    >>> up.doturn([])
    >>> up.percentdone()
    40
    >>> up.doturn([])
    >>> up.state
    0
    >>> up.printstate()
    'Building'
    >>> up.doturn([])
    >>> up.doturn([])
    >>> up.percentdone()
    100
    >>> up.state
    1
    >>> up.printstate()
    'Active'
    >>> r.quatloos=0
    >>> r.people=10
    >>> up.doturn([])
    >>> up.state
    3
    >>> up.printstate()
    'Inactive'
    >>> r.quatloos = 10000
    >>> r.people = 5000
    >>> up.doturn([])
    >>> up.state
    1 
    >>> r.quatloos == 10000 - up.instrumentality.minupkeep
    True


    """
    replinestart = "Planet Upgrade: " + str(self.planet.name) + " (" + str(self.planet.id) + ") "
    i = self.instrumentality
    p = self.planet

    if self.state in [PlanetUpgrade.ACTIVE, PlanetUpgrade.INACTIVE]:
      cost = self.currentcost('quatloos')
      if cost > self.planet.resources.quatloos:
        if self.state == PlanetUpgrade.ACTIVE:
          self.state = PlanetUpgrade.INACTIVE
          self.save()
      else:
        if self.state == PlanetUpgrade.INACTIVE:
          self.state = PlanetUpgrade.ACTIVE
          self.save()
        self.planet.resources.quatloos -= cost
        self.planet.resources.save()
    if self.state == PlanetUpgrade.BUILDING:
      for commodity in i.required.onhand():
        totalneeded = getattr(i.required,commodity)
        alreadyraised = getattr(self.raised, commodity)
        if alreadyraised < totalneeded:
          amount = self.currentcost(commodity)
          self.planet.resources.straighttransferto(self.raised, commodity, amount)
    
      # see if we are going from BUILDING to ACTIVE
      finished = 1
      for commodity in i.required.onhand():
        totalneeded = getattr(i.required,commodity)
        alreadyraised = getattr(self.raised, commodity)
        if alreadyraised < totalneeded:
          finished = 0
      if finished:
        report.append(replinestart+"Finished -- " + i.name)
        self.state = PlanetUpgrade.ACTIVE
        self.save()
      else:
        report.append(replinestart+"Building -- %s %d%% done. " % (i.name, self.percentdone()) )

  def percentdone(self):
    percentages = []
    if self.state == self.ACTIVE or self.state == self.INACTIVE:
      return 100
    for commodity in self.instrumentality.required.onhand():
      completed = float(getattr(self.raised,commodity))
      total     = float(getattr(self.instrumentality.required,commodity))
      if total > 0:
        percentages.append(completed/total)
    return int((sum(percentages)/len(percentages))*100)
  def scrap(self):
    for commodity in self.raised.onhand():
      remit = int(getattr(self.planet.resources,commodity)*.95)
      setattr(self.planet.resources,commodity,remit)
    self.planet.resources.save()
    self.planet.save()
    self.delete()
  def start(self,curplanet,insttype):
    curinstrumentality = Instrumentality.objects.get(type=insttype)
    # check to see if the planet already has this instrumentality
    if PlanetUpgrade.objects.filter(planet=curplanet, 
                                    instrumentality__type=insttype).count() > 0:
      print "planet already has instrumentality"
      return 0
    # check to make sure we have the prerequisite
    if curinstrumentality.requires and PlanetUpgrade.objects.filter(
       planet=curplanet,
       state=self.ACTIVE,
       instrumentality=curinstrumentality.requires).count() < 1:
      print "required instrumentality not attained -- " + str(curinstrumentality.requires)
      return 0
    
    # ok, we can start the upgrade
    self.state = self.BUILDING
    self.instrumentality = curinstrumentality
    raised = Manifest()
    raised.save()
    self.raised = raised
    self.planet = curplanet
    self.raised.save()
    self.save()

class UpgradeAttribute(models.Model):
  upgrade = models.ForeignKey('PlanetUpgrade')
  attribute = models.CharField(max_length=50)
  value = models.CharField(max_length=50)

class PlanetAttribute(models.Model):
  planet = models.ForeignKey('Planet')
  attribute = models.CharField(max_length=50)
  value = models.CharField(max_length=50)
  strings = {'people-advantage':        'Climate: ',
             'food-advantage':          'Food Production: ',
             'steel-advantage':         'Iron Deposits: ',
             'hydrocarbon-advantage':   'Petroleum Reserves: ',
             'lastvisitor':             'Last Visitor: ',
             'food-scarcity':           'Food Scarcity: '}

  def printattribute(self):
    outstring = self.strings[self.attribute]
    if 'advantage' in self.attribute:
      modifier = float(self.value)
      if modifier < 1.0:
        outstring += "Poor"
      elif modifier < 1.05:
        outstring += "Above Average"
      else:
        outstring += "Excellent"
    else:
      outstring += self.value
    return outstring

class FleetAttribute(models.Model):
  fleet = models.ForeignKey('Fleet')
  attribute = models.CharField(max_length=50)
  value = models.CharField(max_length=50)

class PlayerAttribute(models.Model):
  Player = models.ForeignKey('Player')
  attribute = models.CharField(max_length=50)
  value = models.CharField(max_length=50)

class Instrumentality(models.Model):
  """
  Instrumentality -- Planet upgrades are instances of Instrumentalities.
 
  >>> buildinstrumentalities()
  >>> i = Instrumentality.objects.get(type=Instrumentality.LRSENSORS1)
  >>> i.__unicode__()
  u'Long Range Sensors 1'
  """
  def __unicode__(self):
    return self.name
  
  LRSENSORS1       = 0 # done works
  LRSENSORS2       = 1 # done works
  TRADEINCENTIVES  = 2 #
  RGLGOVT          = 3 # done works
  MINDCONTROL      = 4 # done works
  MATTERSYNTH1     = 5 # done works
  MATTERSYNTH2     = 6 # done works
  MILITARYBASE     = 7 # done works
  SLINGSHOT        = 8 # done works



  INSTRUMENTALITIES = (
      (str(LRSENSORS1), 'Sensors 1'),
      (str(LRSENSORS2), 'Sensors 2'),
      (str(TRADEINCENTIVES), 'Trade Incentives'),
      (str(RGLGOVT), 'Regional Government'),
      (str(MINDCONTROL), 'Mind Control'),
      (str(MATTERSYNTH1), 'Matter Synthesizer 1'),
      (str(MATTERSYNTH2), 'Matter Synthesizer 2'),
      (str(MILITARYBASE), 'Military Base'),
      (str(SLINGSHOT), 'Slingshot')
      )

  

  requires = models.ForeignKey('self',null=True,blank=True)
  description = models.TextField()
  name = models.CharField(max_length=50)
  type = models.PositiveIntegerField(default=0, choices = INSTRUMENTALITIES)
  required = models.ForeignKey('Manifest')
  minsociety = models.PositiveIntegerField(default=0)
  upkeep = models.FloatField(default=0.0)
  minupkeep = models.PositiveIntegerField(default=0)

def buildinstrumentalities():
  """
  builds the Instrumentality table... 
  >>> buildinstrumentalities()
  >>> j = instrumentalitytypes[0]
  >>> i = Instrumentality.objects.get(type=j['type'])
  >>> i.description == j['description']
  True
  >>> i.name == j['name']
  True
  >>> i.type == j['type']
  True
  """
  for i in instrumentalitytypes:
    ins = 0
    if Instrumentality.objects.filter(type=i['type']).count():
      ins = Instrumentality.objects.get(type=i['type'])
    else:
      ins = Instrumentality(type=i['type'])
      r = Manifest()
      r.save()
      ins.required = r
    if i['requires'] != -1:
      req = Instrumentality.objects.get(type=i['requires'])
      ins.requires = req
    ins.description = i['description']
    ins.name = i['name']
    ins.minsociety = i['minsociety']
    ins.upkeep = i['upkeep']
    ins.minupkeep = i['minupkeep']
    r = ins.required
    for required in i['required']:
      setattr(r,required,i['required'][required])
    r.save()
    ins.save()
      

class Player(models.Model):
  def __unicode__(self):
    return self.user.username
  user = models.ForeignKey(User, unique=True)
  lastactivity = models.DateTimeField()
  capital = models.ForeignKey('Planet', unique=True)
  color = models.CharField(max_length=15)

  appearance = models.XMLField(blank=True, schema_path=SVG_SCHEMA)
  friends = models.ManyToManyField("self")
  enemies = models.ManyToManyField("self")
  neighbors = models.ManyToManyField("self")
  def getpoliticalrelation(self,otherid):
    if otherid in self.enemies.all():
      return "enemy"
    elif otherid in self.friends.all():
      return "friend"
    else:
      return "neutral"
  def setpoliticalrelation(self,otherid,state):
    if state in ["neutral","none"]:
      self.friends.remove(otherid)
      self.enemies.remove(otherid)
    elif state=="friend":
      self.enemies.remove(otherid)
      self.friends.add(otherid)
    elif state=="enemy":
      self.enemies.add(otherid)
      self.friends.remove(otherid)
  def create(self):
    if len(self.user.planet_set.all()) > 0:
      # cheeky fellow
      return
    narrative = []
    self.lastactivity = datetime.datetime.now()
    userlist = User.objects.exclude(id=self.user.id)
    random.seed()
    userorder = range(len(userlist))
    random.shuffle(userorder)
    for uid in userorder:
      narrative.append("looking at user " + str(uid))
      curuser= userlist[uid]
      planetlist = curuser.planet_set.all()
      if len(planetlist):
        planetorder = range(len(planetlist))
        random.shuffle(planetorder)
        for pid in planetorder:
          narrative.append("looking at planet " + str(pid) + "(" + str(planetlist[pid].id) + ")")
          curplanet = planetlist[pid]
          distantplanets = nearbysortedthings(Planet,curplanet)
          distantplanets.reverse()
          if len(distantplanets) < 6:
            narrative.append("not enough distant planets")
            continue
          for distantplanet in distantplanets:
            suitable = True
            #look at the 'distant planet' and its 5 closest 
            # neighbors and see if they are available
            if distantplanet.owner is not None:
              narrative.append("distant owner not none")
              continue 
            nearcandidates = nearbysortedthings(Planet,distantplanet)
            # make sure the 5 closest planets are free
            for nearcandidate in nearcandidates[:5]:
              if nearcandidate.owner is not None:
                narrative.append("near candidate not none")
                suitable = False
                break
            #if there is a nearby inhabited planet closer than 7
            #units away, continue...
            for nearcandidate in nearcandidates:
              distance = getdistanceobj(nearcandidate,distantplanet)
              narrative.append("d = " + str(distance))
              if nearcandidate.owner is not None:
                narrative.append("distance less than 7 owner = " + str(nearcandidate.owner))
                suitable = False
                break
              if distance > 7.9:
                break
                
            if suitable:
              narrative.append("found suitable")
              distantplanet.owner = self.user
              self.capital = distantplanet
              #self.color = "#ff0000"
              self.color = "#" + hex(((random.randint(64,255) << 16) + 
                            (random.randint(64,255) << 8) + 
                            (random.randint(64,255))))[2:]
              self.appearance = aliens.makealien(self.user.username,
                                                 int("0x"+self.color[1:],16))
              self.save()
              distantplanet.populate()
              distantplanet.save()
              return
    message = []
    message.append('Could not create new player planet for user: ')
    message.append(self.user.username + "("+str(self.user.id)+")")
    message.append('error follows...')
    message.append(' ')
    message.append("\n".join(narrative))
    message = "\n".join(message)
    print "---"
    print message
    print "---"
    send_mail("Dave's Galaxy Problem!", 
              message,
              'support@davesgalaxy.com',
              ['dav3xor@gmail.com'])

    print "did not find suitable"
class Manifest(models.Model):
  """
  Holds a list of resources on a planet, fleet, or required 
  for an upgrade, or whatever...
 
  >>> m1 = Manifest(people=5, food=10, quatloos=20)
  >>> m2 = Manifest(people=5, food=12)
  >>> pprint(m1.onhand())
  {'food': 10, 'people': 5, 'quatloos': 20}
  >>> pprint(m1.manifestlist())
  {'antimatter': 0,
   'consumergoods': 0,
   'food': 10,
   'hydrocarbon': 0,
   'krellmetal': 0,
   'people': 5,
   'quatloos': 20,
   'steel': 0,
   'unobtanium': 0}
  >>> m1.straighttransferto(m2, 'people', 20)
  >>> m1.people
  0
  >>> m2.people
  10
  >>> m2.straighttransferto(m1, 'people', 2)
  >>> m1.people
  2
  >>> m2.people
  8
  >>> pprint(m1.onhand(['id','quatloos']))
  {'food': 10, 'people': 2}
  >>> pprint(m1.manifestlist(['id','quatloos']))
  {'antimatter': 0,
   'consumergoods': 0,
   'food': 10,
   'hydrocarbon': 0,
   'krellmetal': 0,
   'people': 2,
   'steel': 0,
   'unobtanium': 0}
  """
  people = models.PositiveIntegerField(default=0)
  food = models.PositiveIntegerField(default=0)
  consumergoods = models.PositiveIntegerField(default=0)
  steel = models.PositiveIntegerField(default=0)
  krellmetal = models.PositiveIntegerField(default=0)
  unobtanium = models.PositiveIntegerField(default=0)
  antimatter = models.PositiveIntegerField(default=0)
  hydrocarbon = models.PositiveIntegerField(default=0)
  quatloos = models.PositiveIntegerField(default=0)
  def onhand(self, skip=['id']):
    mlist = {}
    for field in self._meta.fields:
      amount = getattr(self,field.name)
      if field.name not in skip and amount > 0: 
        mlist[field.name] = amount
    return mlist
      
  def manifestlist(self, skip=['id']):
    mlist = {}
    for field in self._meta.fields:
      if field.name not in skip: 
        mlist[field.name] = getattr(self,field.name)
    return mlist
  def straighttransferto(self, other, commodity, amount):
    """
    a = Manifest(quatloos=5)
    a.save()
    b = Manifest(quatloos=2)
    b.save()
    a.straighttransferto(b,'quatloos',1)
    a.quatloos
    4
    b.quatloos
    3
    a.straighttransferto(b,'quatloos',20)
    a.quatloos
    0
    b.quatloos
    7
    a.straighttransferto(b,'people',100)
    a.people
    0
    b.people
    0
    """
    selfavailable = getattr(self,commodity)
    otheravailable = getattr(other,commodity)
    if selfavailable < amount:
      setattr(self,commodity,0)
      setattr(other,commodity,otheravailable+selfavailable)
    else:
      setattr(self,commodity,selfavailable-amount)
      setattr(other,commodity,otheravailable+amount)
    self.save()
    other.save()

class Fleet(models.Model):
  owner            = models.ForeignKey(User)
  name             = models.CharField(max_length=50)
  inviewof         = models.ManyToManyField(User, related_name="inviewof")
  inviewoffleet    = models.ManyToManyField('Fleet', 
                                            related_name="viewable",
                                            symmetrical=False)
  disposition      = models.PositiveIntegerField(default=0, choices = DISPOSITIONS)
  homeport         = models.ForeignKey("Planet", null=True, 
                                       related_name="home_port", 
                                       editable=False)
  trade_manifest   = models.ForeignKey("Manifest", null=True, editable=False)
  sector           = models.ForeignKey("Sector", editable=False)
  speed            = models.FloatField(default=0, editable=False)
  direction        = models.FloatField(default=0, editable=False)

  inport           = models.BooleanField(default=True, editable=False)
  damaged          = models.BooleanField(default=False, editable=False)
  destroyed        = models.BooleanField(default=False, editable=False)

  x                = models.FloatField(default=0, editable=False)
  y                = models.FloatField(default=0, editable=False)

  source           = models.ForeignKey("Planet", related_name="source_port", 
                                       null=True, editable=False)
  destination      = models.ForeignKey("Planet", related_name="destination_port", 
                                       null=True, editable=False)
  #destination x/y
  dx               = models.FloatField(default=0, editable=False)
  dy               = models.FloatField(default=0, editable=False)
  
  scouts           = models.PositiveIntegerField(default=0)
  blackbirds       = models.PositiveIntegerField(default=0)
  subspacers       = models.PositiveIntegerField(default=0)
  arcs             = models.PositiveIntegerField(default=0)
  merchantmen      = models.PositiveIntegerField(default=0)
  bulkfreighters   = models.PositiveIntegerField(default=0)
  fighters         = models.PositiveIntegerField(default=0)
  frigates         = models.PositiveIntegerField(default=0)
  destroyers       = models.PositiveIntegerField(default=0)
  cruisers         = models.PositiveIntegerField(default=0)
  battleships      = models.PositiveIntegerField(default=0)
  superbattleships = models.PositiveIntegerField(default=0)
  carriers         = models.PositiveIntegerField(default=0)
  
  def __unicode__(self):
    numships = self.numships()
    return '(' + str(self.id) + ') '+ str(numships) + ' ship' + ('' if numships == 1 else 's')
  def printdisposition(self):
    return DISPOSITIONS[self.disposition][1] 
  def shiplist(self):
    ships = {}
    for type in self.shiptypeslist():
      numships = getattr(self, type.name)
      ships[type.name] = numships
    return ships
    
  def shiplistreport(self):
    output = []
    for type in self.shiptypeslist():
      numships = getattr(self, type.name)
      if numships == 0:
        continue
      name = type.name
      if numships == 1:
        name = shiptypes[name]['singular']
      output.append(str(numships) + " " + name)
    return ", ".join(output)
  def shortdescription(self, html=1):
    description = "Fleet #"+str(self.id)+", "
    curshiptypes = self.shiptypeslist()
    if len(curshiptypes) == 1:
      if getattr(self,curshiptypes[0].name) == 1:
        if html==1:
          description += "<span class=\"fleetnum\">" 
        description += str(getattr(self,curshiptypes[0].name))
        if html==1:
          description += "</span>"
        description += " " + shiptypes[curshiptypes[0].name]['singular']
      else:
        if html==1:
          description += "<span class=\"fleetnum\">" 
        description += str(getattr(self,curshiptypes[0].name))
        if html==1:
          description += "</span>"
        description += " " + shiptypes[curshiptypes[0].name]['plural']
    else:
      if html==1:
        description += "<span class=\"fleetnum\">" 
      description += str(self.numships())
      if html==1:
        description += "</span>" + " mixed ships"
    return description
  def description(self):
    desc = []
    desc.append(self.__unicode__() + ":")
    for type in self.shiptypeslist():
      desc.append(str(getattr(self,type.name)) + " --> " + type.name)
    desc.append("acceleration = " + str(self.acceleration()))
    desc.append("attack = " + str(self.numattacks()) + " defense = " + str(self.numdefenses()))
    return "\n".join(desc)


  def setattribute(self,curattribute,curvalue):
    """
    >>> u = User(username="fsetattribute")
    >>> u.save()
    >>> r = Manifest(people=5000, food=1000)
    >>> r.save()
    >>> s = Sector(key=101101,x=101,y=101)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=505.5, y=506.5, r=.1, color=0x1234)
    >>> p.save()
    >>> f = Fleet(owner=u, homeport=p, sector=s, x=p.x,y=p.y)
    >>> f.save()
    >>> f.setattribute("hello","hi")
    >>> f.getattribute("hello")
    u'hi'
    >>> f.setattribute("hello","hi2")
    >>> f.getattribute("hello")
    u'hi2'
    >>> f.setattribute("hello", None)
    >>> f.getattribute("hello")
    """
    attribfilter = FleetAttribute.objects.filter(fleet=self,attribute=curattribute)
    if curvalue == None:
      attribfilter.delete()
      return None
    if attribfilter.count():
      attribfilter.delete()
    pa = FleetAttribute(fleet=self,attribute=curattribute, value=curvalue)
    pa.save()
  def getattribute(self,curattribute):
    attribfilter = FleetAttribute.objects.filter(fleet=self,attribute=curattribute)
    if attribfilter.count():
      attrib = attribfilter[0]
      return attrib.value
    else:
      return None


  def json(self, playersship=0):
    json = {}
    json['x'] = self.x
    json['y'] = self.y
    json['i'] = self.id
    json['o'] = self.owner.id
    json['c'] = self.owner.get_profile().color
    json['s'] = self.senserange()
    json['sl'] = self.shiplistreport()
    json['n'] = self.numships()
    
    if self.destroyed == True:
      json['dmg'] = 1
    elif self.damaged == True:
      json['dst'] = 1
    #figure out what "type" of fleet it is...
    if self.scouts == json['n']:
      json['t'] = 's'
    elif self.arcs > 0:
      json['t'] = 'a'
    elif self.merchantmen > 0 or self.bulkfreighters > 0:
      json['t'] = 't'
    else:   
      # probably military
      json['t'] = 'm'

    if playersship == 1:
      json['ps'] = 1
    if self.dx != self.x or self.dy!=self.y:
      distanceleft = getdistance(self.x,self.y,self.dx,self.dy)
      angle = math.atan2(self.x-self.dx,self.y-self.dy)
      if distanceleft > .2:
        x2 = self.x - math.sin(angle) * (distanceleft-.2)
        y2 = self.y - math.cos(angle) * (distanceleft-.2)
      else:
        x2 = self.dx
        y2 = self.dy
      json['x2'] = x2
      json['y2'] = y2

    return json
  def setsourceport(self):
    if self.destination and getdistanceobj(self,self.destination) == 0.0:
      self.source = self.destination
    elif self.homeport and getdistanceobj(self,self.homeport) == 0.0:
      self.source = self.homeport
  def scrap(self):
    # can't scrap the fleet if it's not in port
    if not self.inport():
      return

    planetresources = []
    planet = []
    if self.homeport and getdistanceobj(self,self.homeport) == 0.0:
      planet = self.homeport
    elif self.source and getdistanceobj(self,self.source) == 0.0:
      planet = self.source
    elif self.destination and getdistanceobj(self,self.destination) == 0.0:
      planet = self.destination
    else:
      return

    if planet.resources == None:
      r = Manifest()
      r.save()
      planet.resources = r
    planetresources = planet.resources


    for shiptype in self.shiptypeslist():
      type = shiptype.name
      numships = getattr(self,type)

      for commodity in shiptypes[type]['required']:
        remit = shiptypes[type]['required'][commodity]
        # remove this after Nick scraps his scout fleets...
        onplanet = getattr(planetresources,commodity)
        setattr(planetresources,commodity, onplanet + numships * remit)

      setattr(self,type,0)

    if self.trade_manifest:
      manifest = self.trade_manifest.onhand()
      for item in manifest:
        onplanet = getattr(planetresources,item)
        setattr(planetresources,item, onplanet + manifest[item])
      self.trade_manifest.delete()
        
    

    planetresources.save()
    self.delete()
        
  def doinviewof(self,other):
    # tricky because it tells you if this
    # fleet is in view of the other fleet/planet
    # NOT VISE-VERSA...  ;)
    distance = getdistanceobj(self,other)
    srange = other.senserange()
    if distance < srange:
      if self.numships() != self.subspacers:
        return True
      elif srange > 0 and random.random() > (distance/srange)*1.2:
        return True
    return False

  def gotoplanet(self,destination):
    """
    >>> buildinstrumentalities()
    >>> u = User(username="gotoplanet")
    >>> u.save()
    >>> r = Manifest(people=5000, food=1000)
    >>> r.save()
    >>> s = Sector(key=123125,x=101,y=101)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=615, y=625, r=.1, color=0x1234)
    >>> p.save()
    >>> p2 = Planet(resources=r, society=1,owner=u, sector=s,
    ...             x=615, y=628, r=.1, color=0x1234)
    >>> p2.save()
    >>> f = Fleet(owner=u, sector=s, homeport=p, x=p.x, y=p.y, source=p, scouts=1)
    >>> f.save()
    >>> f.gotoplanet(p2)
    >>> f.speed
    0
    >>> up = PlanetUpgrade()
    >>> up.start(p,Instrumentality.SLINGSHOT)
    >>> up.state = PlanetUpgrade.ACTIVE
    >>> up.save()
    >>> f.gotoplanet(p2)
    >>> f.speed
    0.5
    """
    self.direction = math.atan2(self.x-destination.x,self.y-destination.y)
    self.dx = destination.x
    self.dy = destination.y
    self.setsourceport()
    if (self.x == self.source.x and 
       self.y == self.source.y and 
       self.source.hasupgrade(Instrumentality.SLINGSHOT) and
       getdistanceobj(self,destination) > .5):
      self.speed = .5
    self.destination = destination
    self.sector = Sector.objects.get(key=buildsectorkey(self.x,self.y))
    self.save()
  def gotoloc(self,dx,dy):
    self.dx = float(dx)
    self.dy = float(dy)
    self.direction = math.atan2(self.x-self.dx,self.y-self.dy)
    self.setsourceport()
    self.destination = None
    self.sector = Sector.objects.get(key=buildsectorkey(self.x,self.y))
    self.save()
  def arrive(self):
    self.speed=0
    self.x = self.dx
    self.y = self.dy
    self.save()
  def validdispositions(self):
    valid = []
    if self.arcs > 0:
      valid.append(DISPOSITIONS[6])
    if self.merchantmen > 0 or self.bulkfreighters > 0:
      valid.append(DISPOSITIONS[8])
    if self.scouts > 0 or self.blackbirds > 0:
      valid.append(DISPOSITIONS[2])
      valid.append(DISPOSITIONS[3])
    if self.numcombatants():
      valid.append(DISPOSITIONS[1])
      valid.append(DISPOSITIONS[5])
      valid.append(DISPOSITIONS[9])
    return tuple(valid)


  def defenselevel(self,shiptype):
    if type(shiptype) is str:
      return shiptypes[shiptype]['def']
    elif type(shiptype) is models.PositiveIntegerField and shiptype.name != 'disposition':
      
      return shiptypes[shiptype.name]['def']
    else:
      return -1

  def attacklevel(self,shiptype):
    if type(shiptype) is str:
      return shiptypes[shiptype]['att']
    elif type(shiptype) is models.PositiveIntegerField and shiptype.name != 'disposition':
      
      return shiptypes[shiptype.name]['att']
    else:
      return -1

  def hasshiptype(self, shiptype):
    typestr = ""
    if type(shiptype) is str:
      typestr = shiptype
    else:
      typestr = shiptype.name
    if not shiptypes.has_key(typestr):
      return False
    if getattr(self,typestr) > 0:
      return True
    else:
      return False
  def listrepr(self):
    shiplist = []
    for type in self.shiptypeslist():
      numships = getattr(self,type.name)
      shiptype = shiptypes[type.name]
      ship = {}
      ship['type'] = type.name
      ship['att'] = shiptype['att']
      ship['def'] = shiptype['def']
      ship['sense'] = shiptype['sense']
      ship['effrange'] = shiptype['effrange']
      for i in range(numships):
        shiplist.append(ship)
    return shiplist
  def shiptypeslist(self):
    return filter(lambda x: self.hasshiptype(x), self._meta.fields)
  def acceleration(self):
    try:
      accel =  min([shiptypes[x.name]['accel'] for x in self.shiptypeslist()])
      accel += min([self.homeport.society*.001, .1])
    except ValueError: 
      return 0
    return accel
  def numdefenses(self):
    return sum([getattr(self,x.name)*shiptypes[x.name]['def'] for x in self.shiptypeslist()])
  def numattacks(self):
    return sum([getattr(self,x.name)*shiptypes[x.name]['att'] for x in self.shiptypeslist()])
  def numcombatants(self):
    return sum([getattr(self,x.name) for x in filter(lambda y: self.attacklevel(y)>0, self.shiptypeslist())])
  def numnoncombatants(self):
    return sum([getattr(self,x.name) for x in filter(lambda y: self.attacklevel(y)==0, self.shiptypeslist())])
  def senserange(self):
    range = 0
    if not self.owner:
      return range
    if self.numships() > 0:
      range =  max([shiptypes[x.name]['sense'] for x in self.shiptypeslist()])
      range += min([self.homeport.society*.002, .2])
      range += min([self.numships()*.01, .2])
    return range
  def numships(self):
    return sum([getattr(self,x.name) for x in self.shiptypeslist()]) 
  def inport(self):
    if self.homeport and getdistanceobj(self,self.homeport) == 0.0:
      return 1
    elif self.destination and getdistanceobj(self,self.destination) == 0.0:
      return 1
    elif self.source and getdistanceobj(self,self.source) == 0.0:
      return 1
    else:
      return 0
  def dotrade(self,report):
    """
    >>> buildinstrumentalities()
    >>> Planet.objects.all().delete()
    >>> u = User(username="buildinstrumentalities")
    >>> u.save()
    >>> r = Manifest(people=5000, food=1000)
    >>> r.save()
    >>> s = Sector(key=125123,x=100,y=100)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=626, y=617, r=.1, color=0x1234, name="Planet X")
    >>> p.save()
    >>> pl = Player(user=u, capital=p, color=112233)
    >>> pl.lastactivity = datetime.datetime.now()
    >>> pl.save()
    >>> r2 = Manifest(people=5000, food=1000)
    >>> r2.save()
    >>> p2 = Planet(resources=r2, society=10,owner=u, sector=s,
    ...            x=627, y=616, r=.1, color=0x1234, name="Planet Y")
    >>> p2.save()
    >>> r3 = Manifest(quatloos=10)
    >>> r3.save()
    >>> f = Fleet(trade_manifest=r3, merchantmen=1, owner=u, sector=s,x=p.x,y=p.y)
    >>> f.source=p2
    >>> f.destination=p
    >>> f.homeport=p
    >>> f.save()
    >>> report = []
    >>> f.dotrade(report)
    >>> pprint(report)
    ['  Trading at Planet X (1) out of money, restocking.',
     '  Trading at Planet X (1) bought 25 steel',
     '  Trading at Planet X (1) leftover quatloos = 10',
     '  Trading at Planet X (1) new destination = 2']
    >>> f.trade_manifest.quatloos
    10
    """
    dontbuy = ['id','people']
    replinestart = "  Trading at " + self.destination.name + " ("+str(self.destination.id)+") "
    if self.trade_manifest is None:
      report.append(replinestart+"can't trade without trade goods.")
      return
    if self.destination.resources is None:
      report.append(replinestart+"planet doesn't support trade.")
      return
    # sell whatever is in the hold
    m = self.trade_manifest
    curplanet = self.destination

    foreign = False
    if curplanet.owner != self.owner: 
      foreign = True

    #
    # selling onboard commodities to planet here!
    #
    
    dontbuy += self.selltoplanet(curplanet)
    
    capacity = self.merchantmen*500 + self.bulkfreighters*1000
    
    # reset curprices to only ones that are available to sell...
    curprices = curplanet.getavailableprices(foreign)

    bestdif = -10000.0
    bestplanet = 0
    bestcommodity = 0 

    # should we pay taxes?
    if m.quatloos > 20000 and self.destination == self.homeport:
      self.homeport.resources.quatloos += m.quatloos - 5000
      m.quatloos = 5000
      m.save()
      self.homeport.resources.save()

    # something bad happened, transfer some money to the fleet so that it
    # doesn't aimlessly wander the universe, doing nothing...
    if m.quatloos < 500 and self.destination == self.homeport:
      # The fleet's owners are responsible for half...
      halfresupply = 2500 * (self.merchantmen+self.bulkfreighters)
      m.quatloos += halfresupply 
      # And the planet's government is responsible for the other half...
      self.homeport.resources.straighttransferto(m, 'quatloos', halfresupply)
      report.append(replinestart+"out of money, restocking.")




    # first see if we need to go home...
    if self.bulkfreighters > 0 and \
       curplanet.resources.food > 0 and \
       self.homeport.productionrate('food') < 1.0 and \
       self.destination != self.homeport:
      bestplanet = self.homeport
      bestcommodity = 'food'
      bestdif = 1
    elif m.quatloos > 20000 and self.destination != self.homeport:
      report.append(replinestart + 
                    " going home!")
      distance = getdistanceobj(self,self.homeport)

      nextforeign = False
      if self.owner != self.homeport.owner:
        nextforeign = True
      
      bestplanet = self.homeport
      bestcommodity, bestdif = findbestdeal(curplanet,bestplanet, 
                                            m.quatloos, capacity, dontbuy,
                                            nextforeign)

    # too poor to be effective, go home for resupply... (piracy?)
    elif m.quatloos < 500 and self.destination != self.homeport:
      bestplanet = self.homeport
      bestcommodity = 'food'
      bestdif = 1
    else: 
      # first build a list of nearby planets, sorted by distance
      plist = nearbysortedthings(Planet,self)[1:]
      
      for destplanet in plist:
        distance = getdistanceobj(self,destplanet)
        nextforeign = True
        if destplanet.owner == self.owner:
          nextforeign = False
        if destplanet == self.destination:
          print "shouldn't happen"
          continue
        if destplanet.owner == None:
          continue
        if not destplanet.opentrade and  not destplanet.owner == self.owner:
          continue
        if destplanet.resources == None:
          continue
        if self.owner.get_profile().getpoliticalrelation(destplanet.owner.get_profile()) == "enemy":
          continue

        commodity = "food"
        differential = -10000

        if destplanet.resources.food <= 0 and \
           'food' not in dontbuy and \
           curplanet.resources.food > 0 and \
           Fleet.objects.filter(Q(destination=destplanet)|Q(source=destplanet), disposition=8).count() < 2:
          #drop everything and do famine relief
          report.append(replinestart + 
                        " initiating famine relief mission to planet " +
                        str(destplanet.name)+
                        " (" + str(destplanet.id) + ")")
          bestplanet = destplanet
          bestcommodity = "food"
          break
        else:
          commodity, differential = findbestdeal(curplanet,
                                                 destplanet,
                                                 m.quatloos, capacity, 
                                                 dontbuy,
                                                 nextforeign)
          differential -= distance*.5
          #attempt to get ships to go between more than the 2 most
          #convenient planets...
          if destplanet.society < curplanet.society:
            competition = Fleet.objects.filter(Q(destination=destplanet)|Q(source=destplanet), disposition=8).count()
            differential -= competition*2.0
          if differential > bestdif:
            bestdif = differential 
            bestplanet = destplanet
            bestcommodity = commodity
          #print "dif = " + str(differential) + " com = " + commodity

    if bestplanet and bestcommodity and bestcommodity != 'none':
      self.gotoplanet(bestplanet)
      self.buyfromplanet(bestcommodity,curplanet)
      if bestcommodity == 'people':
        report.append(replinestart + "took on " + str(getattr(m,bestcommodity)) + " passengers.")
      else:
        report.append(replinestart + "bought " + str(getattr(m,bestcommodity)) + " " + bestcommodity)
      report.append(replinestart + "leftover quatloos = " + str(m.quatloos))
      report.append(replinestart + "new destination = " + str(bestplanet.id))
    else:
      report.append(replinestart + "could not find profitable route (fleet #" + str(self.id) + ")")
    # disembark passengers (if they want to disembark here, otherwise
    # they wait until the next destination)

  def buyfromplanet(self,item,planet):
    """
    >>> buildinstrumentalities()
    >>> u = User()
    >>> u.save()
    >>> r = Manifest(people=5000, food=1000)
    >>> r.save()
    >>> s = Sector(key=123123,x=100,y=100)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=100, y=100, r=.1, color=0x1234)
    >>> p.save()
    >>> r = Manifest(quatloos=1000)
    >>> r.save()
    >>> f = Fleet(trade_manifest=r, merchantmen=1, owner=u, sector=s)
    >>> f.buyfromplanet('food',p)
    125

    >>> p.owner=None
    >>> p.tariffrate=50.0
    >>> p.resources.food=1000
    >>> f.trade_manifest.quatloos=1000
    >>> f.trade_manifest.food=0
    >>> p.resources.people=5000
    >>> f.buyfromplanet('food',p)
    125 

    # test trade incentives.
    >>> up = PlanetUpgrade()
    >>> up.start(p,Instrumentality.TRADEINCENTIVES)
    >>> up.state = PlanetUpgrade.ACTIVE
    >>> up.save()
    >>> p.resources.food = 0
    >>> p.tariffrate=0.0
    >>> p.getprice('food',False)
    12 
    >>> p.resources.quatloos
    2000
    >>> f.trade_manifest.quatloos = 1000
    >>> f.buyfromplanet('food',p)
    83
    >>> f.trade_manifest.quatloos
    4    
    >>> p.resources.quatloos
    3195 
    """
    # ok, you are able to buy twice the current
    # surplus of any item...
    unitcost = int(planet.getprice(item, False))

    if unitcost == 0:
      unitcost = 1
    surplus = getattr(planet.resources,item)
    capacity = (500 * self.merchantmen) + (1000 * self.bulkfreighters)


    if unitcost > self.trade_manifest.quatloos:
      return 
    
    numtobuy = self.trade_manifest.quatloos/unitcost

    # ships are able to buy surplus * 2 + next turn's production of any commodity on a planet
    nextproduction = planet.nextproduction(item,planet.resources.people)
    available = surplus
    
    if nextproduction > 0:
      available += nextproduction

    if numtobuy/2 > available:
      numtobuy = available*2

    if numtobuy > capacity:
      numtobuy = capacity
    
    self.trade_manifest.quatloos = self.trade_manifest.quatloos-(numtobuy*unitcost)
    planet.resources.quatloos     += numtobuy*unitcost
    
    if planet.hasupgrade(Instrumentality.TRADEINCENTIVES):
      if surplus > 1000:
        # an incentive to buy here...
        planet.resources.quatloos -= int(.2 * (numtobuy*unitcost))
      if surplus == 0:
        # planet doesn't want to give up scarce resource 
        planet.resources.quatloos += int(.2 * (numtobuy*unitcost))

    if numtobuy/2 > getattr(planet.resources,item):
      setattr(planet.resources,item,0)
    else:
      setattr(planet.resources,
              item,
              getattr(planet.resources,item)-(numtobuy/2))

    setattr(self.trade_manifest,
            item,
            getattr(self.trade_manifest,item)+numtobuy)
   
    planet.resources.save()
    self.trade_manifest.save()
    planet.save()
    self.save()
    return numtobuy

  def selltoplanet(self,planet):
    """
    >>> u = User(username="selltoplanet")
    >>> u.save()
    >>> r = Manifest(people=5000, food=1000)
    >>> r.save()
    >>> s = Sector(key=123123,x=100,y=100)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=100, y=100, r=.1, color=0x1234)
    >>> p.save()
    >>> r = Manifest(quatloos=1000,food=1000)
    >>> r.save()
    >>> f = Fleet(trade_manifest=r, merchantmen=1, owner=u, sector=s)
    >>> f.selltoplanet(p)
    ['food']
    >>> f.trade_manifest.quatloos
    9000
    >>> f.trade_manifest.food
    0
    >>> r.quatloos
    9000
    >>> p.owner=None
    >>> p.tariffrate=50.0
    >>> f.trade_manifest.food=1000
    >>> f.trade_manifest.quatloos=1000
    >>> p.resources.people=5000
    >>> p.resources.food=1000
    >>> p.resources.quatloos=8000
    >>> p.getprice('food',True)
    4
    >>> p.getprice('food',False)
    8
    >>> f.selltoplanet(p)
    ['food']
    >>> p.resources.quatloos
    7000
    >>> p.resources.food
    2000
    >>> f.trade_manifest.quatloos
    5000
    >>> f.trade_manifest.food
    0
    
    # test trade incentives.
    >>> up = PlanetUpgrade()
    >>> up.start(p,Instrumentality.TRADEINCENTIVES)
    >>> up.state = PlanetUpgrade.ACTIVE
    >>> up.save()
    >>> f.trade_manifest.food = 1000
    >>> p.tariffrate=0.0
    >>> p.getprice('food',False)
    6
    >>> f.selltoplanet(p)
    ['food']
    >>> f.trade_manifest.quatloos
    11000
    >>> p.resources.quatloos
    5200

    """

    dontbuy = []
    m = self.trade_manifest
    r = planet.resources
    
    foreign = False
    if self.owner != planet.owner:
      foreign = True

    shipsmanifest = m.onhand(['id','quatloos'])

    for item in shipsmanifest:
      numtosell = getattr(m,item)
      onhand = getattr(r,item)
      if(numtosell > 0):
        dontbuy.append(item)
        profit = planet.getprice(item, foreign) * numtosell
        #if item == 'people':
        #  report.append(replinestart + 
        #                " disembarking " + str(numtosell) + " passengers.")
        #else:
        #  report.append(replinestart + 
        #                " selling " + str(numtosell) + " " + str(line) +
        #                " for " + str(profit) + ".")
        m.quatloos += profit
        setattr(m,item,0)
        setattr(r,item,getattr(r,item)+numtosell)

        # purchasing costs the local economy half, and the 
        # government half
        if r.quatloos - int(profit/2.0) < 0:
          r.quatloos = 0
        else:
          r.quatloos -= int(profit/2.0)  
        if foreign:
          tax = int((numtosell/2.0 * (planet.getprice(item,False) - planet.getprice(item, True)))/2.0)
          r.quatloos += tax
          if r.quatloos < 0:
            r.quatloos = 0

        if planet.hasupgrade(Instrumentality.TRADEINCENTIVES):
          if onhand > 1000:
            # an incentive not to sell here...
            r.quatloos += int(.2 * profit)
          if onhand == 0:
            # we want these, so sweeten the deal
            r.quatloos -= int(.2 * profit)
            if r.quatloos < 0:
              r.quatloos = 0
    planet.resources.save()
    self.trade_manifest.save()
    planet.save()
    self.save()
    return dontbuy
    
  def newfleetsetup(self,planet,ships):
    buildableships = planet.buildableships()
    notspent = buildableships['commodities']
    for shiptype in ships:
      if not buildableships['types'].has_key(shiptype):
        print "cannot build type " + shiptype
        continue
      for commodity in buildableships['types'][shiptype]:
        notspent[commodity] -= buildableships['types'][shiptype][commodity]*ships[shiptype]
      for commodity in notspent:
        if notspent[commodity] < 0:
          return "Not enough " + commodity + " to build fleet..."
    for shiptype in ships:
      setattr(self, shiptype, ships[shiptype])
    for commodity in notspent:
      setattr(planet.resources, commodity, notspent[commodity])
    planet.save()
    planet.resources.save()

    self.homeport = planet
    self.source = planet
    self.x = planet.x
    self.y = planet.y
    self.dx = planet.x
    self.dy = planet.y
    self.sector = planet.sector
    self.owner = planet.owner

    if self.arcs > 0:
      self.disposition = 6
    elif (self.merchantmen > 0 or self.bulkfreighters > 0):
      self.disposition = 8
      manifest = Manifest()
      manifest.quatloos  = 5000 * self.merchantmen
      manifest.quatloos += 5000 * self.bulkfreighters
      manifest.save()
      self.trade_manifest = manifest
      #self.trade_manifest.save() 
    self.save()
    self.inviewof.add(self.owner)
    return self
    
  def move(self):
    accel = self.acceleration()
    distancetodest = getdistance(self.x,self.y,self.dx,self.dy)
    if accel and distancetodest:
      daystostop = (math.ceil(self.speed/accel))
      distancetostop = .5*(self.speed)*(daystostop) # classic kinetics...
      if(distancetodest<=distancetostop):
        self.speed -= accel
        if self.speed <= 0:
          self.speed = 0
      elif self.speed < 5.0:
        self.speed += accel
        if self.speed > 5.0:
          self.speed = 5.0
      #now actually move the fleet...
      self.x = self.x - math.sin(self.direction)*self.speed
      self.y = self.y - math.cos(self.direction)*self.speed
      sectorkey = buildsectorkey(self.x,self.y)
      if Sector.objects.filter(key=sectorkey).count() == 0:
        sector = Sector(key=sectorkey, x=int(self.x), y=int(self.y))
        sector.save()
        self.sector = sector
        self.save()
      else:
        self.sector = Sector.objects.get(key=sectorkey)
        self.save()
  def doassault(self,destination,report):
    replinestart = "  Assaulting Planet " + self.destination.name + " ("+str(self.destination.id)+")"
    nf = nearbythings(Fleet,self.x,self.y).filter(owner = destination.owner)
    for f in nf:
      if f == self:
        continue
      if f.owner == self.owner:
        continue
      if f.numcombatants() == 0:
        continue
      distance = getdistanceobj(f,self)
      if distance < self.senserange() or distance < f.senserange():
        report.append(replinestart + "unsuccessful assault -- planet currently defended")
        # can't assault when there's a defender nearby...
        return
    # ok, we've made it through any defenders...
    if destination.resources:
      report.append(replinestart + "assault in progress -- raining death from space")
      potentialloss = self.numattacks()/1000.0
      if potentialloss > .5:
        potentialloss = .5
      for key in destination.resources.onhand():
        curvalue = getattr(destination.resources,key)
        if curvalue > 0:
          newvalue = curvalue - (curvalue*(random.random()*potentialloss))
          setattr(destination.resources,key,newvalue)
      destination.save()
    if random.random() < .2:
      report.append(replinestart + "planetary assault -- capitulation!")
      #capitulation -- planet gets new owner...
      destination.owner = self.owner
      destination.save()
        
  def doturn(self,report):
    replinestart = "Fleet: " + self.shortdescription(html=0) + " (" + str(self.id) + ") "
    # see if we need to move the fleet...
    distancetodest = getdistance(self.x,self.y,self.dx,self.dy)
    # figure out how fast the fleet can go
    
    if distancetodest < self.speed: 
      # we have arrived at our destination
      if self.destination:
        report.append(replinestart +
                      "Arrived at " +
                      self.destination.name + 
                      " ("+str(self.destination.id)+")")
        if not self.destination.owner and \
           not self.destination.planetattribute_set.filter(attribute="lastvisitor").count():
          # this planet hasn't been visited...
          self.destination.createadvantages(report)
        if not self.destination.owner or self.destination.owner != self.owner:
          for attrib in self.destination.planetattribute_set.all():
            report.append("  " + attrib.printattribute())
        self.destination.setattribute('lastvisitor',self.owner.username) 
      else:
        report.append(replinestart +
                      "Arrived at X = " + str(self.dx) +
                      " Y = " + str(self.dy))
        
      self.arrive()
      if self.disposition == 6 and self.arcs > 0 and self.destination:
        self.destination.colonize(self,report)
      # handle trade disposition
      if self.disposition == 8 and self.destination and self.trade_manifest:   
        self.dotrade(report)
    elif distancetodest != 0.0:
      report.append(replinestart + 
                    "enroute -- distance = " + 
                    str(distancetodest) + 
                    " speed = " + 
                    str(self.speed))
    if distancetodest < .05 and self.destination and self.destination.owner:
      # always do the following if nearby, not just when arriving
      if self.owner.get_profile().getpoliticalrelation(self.destination.owner.get_profile())=='enemy':
        if self.disposition in [0,1,2,3,5,7,9]:
          self.doassault(self.destination, report)
        else:
          self.gotoplanet(self.homeport)
          

    else:
      self.move()
      
class Message(models.Model):
  def __unicode__(self):
    return self.subject
  subject = models.CharField(max_length=80)
  message = models.TextField()
  replyto = models.ForeignKey('Message', related_name="reply_to", null=True)
  fromplayer = models.ForeignKey(User, related_name='from_player')
  toplayer = models.ForeignKey(User, related_name='to_player')
  
class Sector(models.Model):
  def __unicode__(self):
    return str(self.key)
  key = models.IntegerField(primary_key=True)
  controllingplayer = models.ForeignKey(User, null=True)
  x = models.IntegerField()
  y = models.IntegerField()

class Planet(models.Model):
  """
  A planet/star -- the names are interchangable
  >>> u = User(username="test")
  >>> u.save()
  >>> player = Player(user=u)
  >>> p = Planet(name="testplanet",x=1.0,y=1.0,owner=u)
  """
  def __unicode__(self):
    return self.name + "-" + str(self.id)
  name = models.CharField('Planet Name', max_length=50)
  owner = models.ForeignKey(User, null=True)
  sector = models.ForeignKey('Sector')
  x = models.FloatField()
  y = models.FloatField()
  r = models.FloatField()
  color = models.PositiveIntegerField()
  society = models.PositiveIntegerField()

  resources = models.ForeignKey('Manifest', null=True)
  tariffrate = models.FloatField('External Tariff Rate', default=0)
  inctaxrate = models.FloatField('Income Tax Rate', default=0)
  openshipyard = models.BooleanField('Allow Others to Build Ships', default=False)
  opencommodities = models.BooleanField('Allow Trading of Rare Commodities',default=False)
  opentrade = models.BooleanField('Allow Others to Trade Here',default=False)
  
  def createadvantages(self, report):
    replinestart = "New Planet Survey: " + self.name + " (" + str(self.id) + "): "
    print "creating advantages"
    if not self.owner:
      potentialadvantages = ['people',
                             'food',        
                             'steel',       
                             'hydrocarbon']
      random.shuffle(potentialadvantages)
      red = self.color>>16
      green = (self.color>>8)&255
      blue =  (self.color)&255
      if random.randint(1,5) == 5:
        curadvantage = random.choice(potentialadvantages)  
        numadvantage = random.normalvariate(1.0005,.0007)
        self.setattribute(curadvantage+"-advantage",str(numadvantage))

  def hasupgrade(self, upgradetype):
    return PlanetUpgrade.objects.filter(planet=self, 
                                        state=PlanetUpgrade.ACTIVE, 
                                        instrumentality__type=upgradetype).count()
  def buildableupgrades(self):
    # quite possibly the most complex Django query I've written...

    # first exclude the ones we already have...
    notbought = Instrumentality.objects.exclude(planetupgrade__planet=self)

    #then filter for the ones we can start
    return notbought.filter(Q(minsociety__lt=self.society)&(Q(requires=None)|
                            Q(requires__planetupgrade__planet=self,
                              requires__planetupgrade__state=PlanetUpgrade.ACTIVE)))

 
  def upgradeslist(self, curstate=-1):
    if curstate != -1:
      return PlanetUpgrade.objects.filter(planet=self, state__in=curstate)
    else:
      return PlanetUpgrade.objects.filter(planet=self)
      
  def colonize(self, fleet,report):
    if self.owner != None and self.owner != fleet.owner:
      # colonization doesn't happen if the planet is already colonized
      # (someone beat you to it, sorry...)
      report.append("Cancelled Colony: Fleet #" + str(fleet.id) + 
                    " returning home from" + str(self.name) + 
                    " ("+str(self.id)+") -- Planet already owned.")
      fleet.gotoplanet(fleet.homeport)
    else:
      if self.owner == None:
        report.append("New Colony: Fleet #" + str(fleet.id) + 
                      " started colony at " + str(self.name) + 
                      " ("+str(self.id)+")")
      else:
        report.append("Bolstered Colony: Fleet #" + str(fleet.id) + 
                      " bolstered colony at " + str(self.name) + 
                      " ("+str(self.id)+")")
        
      resources = ""
      if self.resources == None:
        resources = Manifest()
      else:
        resources = self.resources
      numarcs = fleet.arcs


      for commodity in shiptypes['arcs']['required']:
        numtoadd = shiptypes['arcs']['required'][commodity]*numarcs
        numcurrently = getattr(resources,commodity)
        setattr(resources,commodity,numcurrently+numtoadd)
      # some of the steel is wasted in the process
      # (stops people from colonizing, and then building
      # an arc and going to the next planet...)
      resources.steel = resources.steel-5
      self.owner = fleet.owner
      resources.save()
      self.resources = resources
      self.inctaxrate = 7.0
      fleet.arcs = 0
      fleet.save()
      self.save()
  def canbuildships(self):
    for needed in shiptypes['scouts']['required']:
      if shiptypes['scouts']['required'][needed] > getattr(self.resources,needed):
        return False
    return True
  def buildableships(self):
    """
    returns a list of ships that can be built at this planet
    >>> u = User()
    >>> s = Sector(key="100100")
    >>> p = Planet(sector=s, owner=u,x=500,y=500,r=.1,color=0xff0000)
    >>> p.populate()
    >>> pprint(p.buildableships()['types']['scouts'])
    {'antimatter': 1, 'food': 5, 'people': 5, 'quatloos': 10, 'steel': 10}

    >>> r = p.resources
    >>> r.antimatter += 10
    >>> r.krellmetal += 1
    >>> r.save()
    
    >>> up = PlanetUpgrade()
    >>> i = Instrumentality.objects.get(type=Instrumentality.MATTERSYNTH1)
    >>> PlanetUpgrade.objects.filter(planet=p, 
    ...                              instrumentality=i,
    ...                              state=PlanetUpgrade.ACTIVE).count()
    1
    >>> p.upgradeslist([PlanetUpgrade.ACTIVE,PlanetUpgrade.INACTIVE]).count()
    3 
    >>> pprint(p.buildableships()['types']['subspacers'])
    {'antimatter': 10,
     'food': 50,
     'krellmetal': 1,
     'people': 50,
     'quatloos': 100,
     'steel': 50}
    """
    buildable = {}
    buildable['types'] = {}
    buildable['commodities'] = {}
    buildable['available'] = []
    hasmilitarybase = self.hasupgrade(Instrumentality.MILITARYBASE)
    # this is a big imperative mess, but it's somewhat readable
    # (woohoo!)
    for type in shiptypes:
      isbuildable = True
      # turn off fighters for now, too confusing...
      if type == 'fighters':
        isbuildable = False
      for needed in shiptypes[type]['required']:
        if shiptypes[type]['required'][needed] > getattr(self.resources,needed):
          isbuildable = False
          break 
      if hasmilitarybase == False and shiptypes[type]['requiresbase'] == True:
        isbuildable = False
      if isbuildable:
        for needed in shiptypes[type]['required']:
          if shiptypes[type]['required'][needed] != 0 and needed not in  buildable['commodities']:
            buildable['commodities'][needed] = getattr(self.resources,needed)
            #buildable['available'].append(getattr(self.resources,needed))
        buildable['types'][type] = {} 

    for type in buildable['types']:
      for i in buildable['commodities'].keys():
        buildable['types'][type][i]=shiptypes[type]['required'][i]
    return buildable
    

  def populate(self):
    """
    >>> u = User(username="populate")
    >>> u.save()
    >>> r = Manifest()
    >>> r.save()
    >>> s = Sector(key=123126,x=101,y=101)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=615, y=625, r=.1, color=0x1234)
    >>> p.save()
    >>> p.populate()
    """
    # populate builds a new capital (i.e. a player's first
    # planet, the one he comes from...)
    if self.resources == None:
      resources = Manifest()
    else:
      resources = self.resources
    for resource in productionrates:
      setattr(resources,resource,productionrates[resource]['initial'])
    resources.save()

    self.society = 50
    self.inctaxrate = 7.0
    self.tariffrate = 0.0
    self.openshipyard = False
    self.opencommodities = False
    self.opentrade = False
    self.resources = resources
    self.save()
    if not self.hasupgrade(Instrumentality.MATTERSYNTH1):
      ms1 = PlanetUpgrade()
      ms1.start(self,Instrumentality.MATTERSYNTH1)
      ms1.state = PlanetUpgrade.ACTIVE
      ms1.save()

    if not self.hasupgrade(Instrumentality.MATTERSYNTH2):
      ms2 = PlanetUpgrade()
      ms2.start(self,Instrumentality.MATTERSYNTH2)
      ms2.state = PlanetUpgrade.ACTIVE
      ms2.save()
    
    if not self.hasupgrade(Instrumentality.MILITARYBASE):
      milbase = PlanetUpgrade()
      milbase.start(self,Instrumentality.MILITARYBASE)
      milbase.state = PlanetUpgrade.ACTIVE
      milbase.save()

  def senserange(self):
    if not self.owner:
      return 0 
    range = .5 
    if self.hasupgrade(Instrumentality.LRSENSORS1):
      range += .5
    if self.hasupgrade(Instrumentality.LRSENSORS2):
      range += .5
    range += min(self.society*.01, 1.0)
    return range
  def getprice(self, commodity, includetariff):
    """ 
    computes the current price for a commodity on a planet
    >>> u = User(username="getprice")
    >>> u.save()
    >>> r = Manifest()
    >>> r.save()
    >>> s = Sector(key=123125,x=101,y=101)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=615, y=625, r=.1, color=0x1234)
    >>> p.save()
    >>> p.getprice('food',True)
    10
    >>> p.tariffrate=50.0
    >>> p.getprice('food',True)
    5
    >>> p.resources.food = 1000
    >>> p.resources.people = 5000
    >>> p.getprice('food',True)
    4
    >>> p.getprice('food',False)
    8
    >>> p.resources.food = 0
    >>> p.getprice('food',False)
    10
    >>> p.resources.food = 100000
    >>> p.getprice('food',False)
    2
    >>> up = PlanetUpgrade()
    >>> up.start(p,Instrumentality.TRADEINCENTIVES)
    >>> up.state = PlanetUpgrade.ACTIVE
    >>> up.save()
    >>> p.getprice('food',False)
    1
    >>> p.getprice('food',True)
    1
    >>> p.resources.food = 0
    >>> p.getprice('food',True)
    6
    >>> p.getprice('food',False)
    12

    """
    nextprod = self.nextproduction(commodity, self.resources.people)
    onhand = getattr(self.resources,commodity)
    nextsurplus = (nextprod-self.resources.people)
    baseprice = productionrates[commodity]['baseprice']
    productionrate = self.productionrate(commodity)
    pricemod = productionrates[commodity]['pricemod']
    price = baseprice - ((nextsurplus * pricemod)/baseprice)
    # if there's a surplus, that affects the price.  the
    # more surplus the lower the price
    if onhand > 0 and abs(nextsurplus)>1:
      price -= ((baseprice*max(2.0,1.0*onhand/nextsurplus))/20.0)


    # keep prices between min/max values...
    price = max(price,baseprice*.2)

    if self.hasupgrade(Instrumentality.TRADEINCENTIVES):
      if onhand > 1000:
        price *= .8
      if onhand == 0:
        price *= 1.2


    # and add the tariff if needed
    if includetariff:
      price = price - price*(self.tariffrate/100.0)
    
    # price must always be non-zero -- 
    if price <= 1:
      price = 1.0
   
    return int(price)
    

  def sellfrommarkettogovt(self,  commodity, amount):
    """
    >>> u = User(username="sellfrommarkettogovt")
    >>> u.save()
    >>> r = Manifest(quatloos=100, food=15)
    >>> r.save()
    >>> s = Sector(key=123126,x=101.5,y=101.5)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=615, y=625, r=.1, color=0x1234)
    >>> p.save()
    >>> p.getprice('food', False)
    10
    >>> p.sellfrommarkettogovt('food',1)
    1
    >>> p.resources.food
    16
    >>> p.resources.quatloos
    90
    >>> p.getprice('food',False)
    10
    >>> p.sellfrommarkettogovt('food',100)
    9
    >>> p.resources.food
    25 
    >>> p.resources.quatloos
    0
    """
    curprice = self.getprice(commodity, False)
    numtobuy = min(amount, int(self.resources.quatloos/curprice))
    commodityonhand = getattr(self.resources,commodity)
    setattr(self.resources,
            commodity,
            commodityonhand+numtobuy)
    self.resources.quatloos -= curprice*numtobuy
    self.resources.save()
    return numtobuy

  def getprices(self, foreign):
    pricelist = {}
    if self.resources != None:
      resourcelist = self.resources.manifestlist(['id','quatloos'])
      for resource in resourcelist:
        pricelist[resource] = self.getprice(resource, foreign) 
    return pricelist 

  def getavailableprices(self, foreign):
    pricelist = {}
    if self.resources != None:
      resourcelist = self.resources.manifestlist(['id','quatloos'])
      for resource in resourcelist:
        pricelist[resource] = self.getprice(resource,foreign) 
    return pricelist

  def json(self,playersplanet=0):
    json = {}

    if self.owner:
      json['o'] = self.owner.id
      json['h'] = self.owner.get_profile().color

      scarcity = self.getattribute('food-scarcity')
      if scarcity:
        if scarcity == 'subsidized': 
          json['scr'] = 1
        if scarcity == 'famine': 
          json['scr'] = 2
      if self.hasupgrade(Instrumentality.MATTERSYNTH1):
        json['mil'] = 1
        if self.hasupgrade(Instrumentality.MILITARYBASE):
          json['mil'] += 1 
        if self.hasupgrade(Instrumentality.MATTERSYNTH2):
          json['mil'] += 1 
      if self.owner.get_profile().capital == self:
        json['cap'] = "1"
      json['s'] = self.senserange()
    else:
      json['h'] = 0
    
    json['x'] = self.x
    json['y'] = self.y
    json['c'] = "#" + hex(self.color)[2:]
    json['r'] = self.r
    json['i'] = self.id
    json['n'] = self.name
    if playersplanet == 1:
      json['pp'] = 1
    return json

  def productionrate(self,resource):
    advantageattrib =  self.planetattribute_set.filter(attribute=resource+'-advantage')
    advantage = 1.0
    if len(advantageattrib):
      advantage = float(advantageattrib[0].value)
    return ((productionrates[resource]['baserate']+
            (productionrates[resource]['socmodifier']*self.society))*advantage)
  
  def nextproduction(self, resource, population):
    produced = self.productionrate(resource) * population
    return produced
  
  def nexttaxation(self):
    return (self.resources.people * (self.inctaxrate/100.0))/6.0
  
  def resourcereport(self,foreign):
    report = []
    if self.resources:
      mlist = self.resources.manifestlist(['people','id','quatloos'])
      for resource in mlist:
        res = {}
        res['name'] = resource
        res['amount'] = mlist[resource]
        res['price'] = self.getprice(resource,foreign)
        res['nextproduction'] = self.nextproduction(resource,self.resources.people)
        res['nextproduction'] = int(res['nextproduction'] -
                                    self.resources.people)
        if res['nextproduction'] < 0:
          res['nextproduction'] = 0
        res['negative'] = 0
        report.append(res)
    return report   
  
  def doproductionforresource(self, curpopulation, resource):
    # skip this resource if we can't produce it on this planet
    #print resource 
    if (productionrates[resource]['neededupgrade'] != -1 and 
       not self.hasupgrade(productionrates[resource]['neededupgrade'])):
      return 0      
    oldval = getattr(self.resources, resource)
    pretax = self.nextproduction(resource,curpopulation)
    surplus = pretax-curpopulation
    if resource == 'people':
      return int(pretax)
      #setattr(self.resources, resource, int(pretax)) 
    else:        
      if surplus >= 0:
        aftertax = oldval + (surplus - math.floor(surplus*((self.inctaxrate/100.0)/2.0)))
        return int(aftertax)
      else:
        # no taxes, just reduce by half
        return int(oldval+surplus)


  def doproduction(self,replinestart,report):
    """
    >>> u = User(username="doproduction")
    >>> u.save()
    >>> r = Manifest(people=5000, food=1000)
    >>> r.save()
    >>> s = Sector(key=123124,x=101,y=101)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=100, y=100, r=.1, color=0x1234)
    >>> p.save()
    >>> pl = Player(user=u,color=0,capital=p)
    >>> pl.lastactivity = datetime.datetime.now()
    >>> pl.save()
    >>> r.people
    5000
    >>> x = []
    >>> p.doproduction('blah',x)
    >>> r.people
    5599
    >>> r.food
    1444
    >>> r.krellmetal
    0
    >>> r.unobtanium
    0
    >>> p.society = 100 
    >>> r.people = 100000
    >>> p.save()
    >>> up = PlanetUpgrade()
    >>> up.start(p,Instrumentality.MATTERSYNTH1)
    >>> up.state = PlanetUpgrade.ACTIVE
    >>> up.save()
    >>> p.hasupgrade(Instrumentality.MATTERSYNTH1)
    1
    >>> p.resources.food
    1444
    >>> p.doproduction('hi',[])
    >>> r.krellmetal
    7
    >>> up = PlanetUpgrade()
    >>> up.start(p,Instrumentality.MATTERSYNTH2)
    >>> up.state = PlanetUpgrade.ACTIVE
    >>> up.save()
    >>> p.doproduction('hi',[])
    >>> r.unobtanium
    2
    """
    curpopulation = self.resources.people
    curfood = self.resources.people
    enoughfood = self.productionrate('food')


    for resource in productionrates.keys():
      newval = self.doproductionforresource(curpopulation,resource)
      
      if resource == 'food' and newval < 0:
        # attempt to buy enough food to cover the
        # discrepency...
        foodprice = self.getprice('food',False)
        quatloos = self.resources.quatloos
        # only have to buy 10% of discrepency to subsidize
        numtobuy = (abs(newval)/10)+min(curpopulation/1000,200)
         
        # artificially set the food value so that it ends up as
        # min(curpopulation/1000, 200)
        self.resources.food = newval/10

        # make the purchase
        numbought = self.sellfrommarkettogovt('food', numtobuy)
        #self.resources.food += newval
        #self.resources.food = max(0,self.resources.food)
        if numbought > 0 and curfood in [0,199,200]: 
          # we are still able to subsidize food production
          report.append(replinestart + "Govt. Subsidizing Food Prices")
          self.setattribute('food-scarcity','subsidized')
        
        # check to see if there's no food available on the planet
        elif numbought == 0:
          # uhoh, famine...
          report.append(replinestart + "Reports Famine!")
          self.population = int(curpopulation * .9)
          self.setattribute('food-scarcity','famine')



      else:
        setattr(self.resources, resource, max(0,newval))

    self.resources.quatloos += self.nexttaxation()

    if self.resources.food > 0 or enoughfood > 1.0:
      # increase the society count if the player has played
      # in the last 2 days.
      if not self.hasupgrade(Instrumentality.MINDCONTROL) and \
         self.owner.get_profile().lastactivity > \
         (datetime.datetime.today() - datetime.timedelta(hours=36)):
        self.society += 1

      elif self.owner.get_profile().lastactivity < \
         (datetime.datetime.today() - datetime.timedelta(days=10)) and \
         self.resources.people > 70000:
        # limit population growth on absentee landlords... ;)
        self.resources.people = curpopulation * (enoughfood*.9)
      self.setattribute('food-scarcity',None)






    self.save()


  def setattribute(self,curattribute,curvalue):
    """
    >>> u = User(username="psetattribute")
    >>> u.save()
    >>> r = Manifest(people=5000, food=1000)
    >>> r.save()
    >>> s = Sector(key=101101,x=101,y=101)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=505.5, y=506.5, r=.1, color=0x1234)
    >>> p.save()
    >>> p.setattribute("hello","hi")
    >>> p.getattribute("hello")
    u'hi'
    >>> p.setattribute("hello","hi2")
    >>> p.getattribute("hello")
    u'hi2'
    >>> p.setattribute("hello", None)
    >>> p.getattribute("hello")
    """
    attribfilter = PlanetAttribute.objects.filter(planet=self,attribute=curattribute)
    if curvalue == None:
      attribfilter.delete()
      return None
    if attribfilter.count():
      attribfilter.delete()
    pa = PlanetAttribute(planet=self,attribute=curattribute, value=curvalue)
    pa.save()
  def getattribute(self,curattribute):
    attribfilter = PlanetAttribute.objects.filter(planet=self,attribute=curattribute)
    if attribfilter.count():
      attrib = attribfilter[0]
      return attrib.value
    else:
      return None

  def doturn(self, report):
    """
    >>> u = User(username="planetdoturn")
    >>> u.save()
    >>> r = Manifest(people=5000, food=1000)
    >>> r.save()
    >>> s = Sector(key=101101,x=101,y=101)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s, name="1",
    ...            x=505.5, y=506.5, r=.1, color=0x1234)
    >>> p.save()
    >>> pl = Player(user=u, capital=p, color=112233)
    >>> pl.lastactivity = datetime.datetime.now()
    >>> pl.save()
    >>> report=[]
    >>> p.doturn(report)
    >>> p.resources.food
    1444
    >>> up = PlanetUpgrade()
    >>> up.start(p,Instrumentality.MATTERSYNTH1)
    >>> up.save()
    >>> p.doturn(report)
    >>> print report
    [u'Planet Upgrade: 1 (9) Building -- Matter Synth 1 8% done. ']
    >>> up.scrap()
    >>> r = Manifest(people=5000, food=1000, quatloos=1000)
    >>> r.save()
    >>> p2 = Planet(resources=r, sector=s, x=505.2, y=506.0, r=.1, name="2",
    ...             inctaxrate=5.0, owner=u, color=0x1234, society=1)
    >>> p2.save()
    >>> up = PlanetUpgrade()
    >>> up.start(p,Instrumentality.RGLGOVT)
    >>> up.state=PlanetUpgrade.ACTIVE
    >>> up.save()
    >>> report = []
    >>> p.resources.quatloos = 1000
    >>> p.resources.save()
    >>> p.doturn(report)
    >>> print report
    ['Planet: 1 (9) Regional Taxes Collected -- 20']
    >>> p.resources.quatloos
    1020
    >>> p2 = Planet.objects.get(name="2")
    >>> p2.resources.quatloos
    980
    """
    replinestart = "Planet: " + str(self.name) + " (" + str(self.id) + ") "
    # first build on upgrades
    for upgrade in self.upgradeslist():
      upgrade.doturn(report)
    # only owned planets produce
    if self.owner != None and self.resources != None:

     
      # do population cap for all planets
      if self.resources.people > 15000000:
        self.resources.people = 15000000
      self.doproduction(replinestart,report)
    
      # handle regional taxation
      if self.hasupgrade(Instrumentality.RGLGOVT):
        totaltax = self.nextregionaltaxation()
        report.append(replinestart + "Regional Taxes Collected -- %d" % (totaltax))
  
      self.save()
      self.resources.save()

  def nextregionaltaxation(self,debit=True):
    totaltax = 0
    if self.hasupgrade(Instrumentality.RGLGOVT):
      planets = nearbythings(Planet,self.x,self.y).filter(owner=self.owner)
      planets = planets.exclude(id=self.id)
      for i in planets:
        if self == i:
          continue
        if i.hasupgrade(Instrumentality.RGLGOVT):
          continue
        if getdistanceobj(self,i) < 5 and self != i:
          tax = i.nexttaxation()*.5
          if tax > i.resources.quatloos:
            tax = i.resources.quatloos
          if debit:
            i.resources.quatloos -= int(tax)
            i.save()
            i.resources.save()
          totaltax += tax
      totaltax = int(totaltax)
      if debit:
        self.resources.quatloos += totaltax
        self.resources.save()

    return totaltax

def nearbythingsbybbox(thing, bbox, otherowner=None):
  xmin = int(bbox.xmin/5.0)
  ymin = int(bbox.ymin/5.0)
  xmax = int(bbox.xmax/5.0)
  ymax = int(bbox.ymax/5.0)
  xr = xrange(xmin-1,xmax+1)
  yr = xrange(ymin-1,ymax+1)
  sectorkeys = []
  for i in xr:
    for j in yr:
      sectorkeys.append(i*1000 + j)
  #print "sector keys = " + str(sectorkeys)
  return thing.objects.filter(sector__in=sectorkeys,
                              owner = otherowner)

def nearbythings(thing,x,y):
  sx = int(x)/5
  sy = int(y)/5
  return thing.objects.filter(
    Q(sector=((sx-1)*1000)+sy-1)|
    Q(sector=((sx-1)*1000)+sy-1)|
    Q(sector=((sx-2)*1000)+sy)|
    Q(sector=((sx-1)*1000)+sy)|
    Q(sector=((sx-1)*1000)+sy+1)|
    Q(sector=(sx*1000)+sy-2)|
    Q(sector=(sx*1000)+sy-1)|
    Q(sector=(sx*1000)+sy)|
    Q(sector=(sx*1000)+sy+1)|
    Q(sector=(sx*1000)+sy+2)|
    Q(sector=((sx+1)*1000)+sy-1)|
    Q(sector=((sx+2)*1000)+sy)|
    Q(sector=((sx+1)*1000)+sy)|
    Q(sector=((sx+1)*1000)+sy+1))

class Announcement(models.Model):
  def __unicode__(self):
      return self.subject
  time = models.DateTimeField(auto_now_add=True)
  subject = models.CharField(max_length=50)
  message = models.TextField()

class Event(models.Model):
  def __unicode__(self):
      return self.event[:20]
  time = models.DateTimeField(auto_now_add=True)
  event = models.TextField()

def getdistanceobj(o1,o2):
  return getdistance(o1.x,o1.y,o2.x,o2.y)
def getdistance(x1,y1,x2,y2):
  return math.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))

def nearbysortedthings(Thing,curthing):
  nearby = list(nearbythings(Thing,curthing.x,curthing.y))
  nearby.sort(lambda x,y:int((getdistanceobj(curthing,x) -
                              getdistanceobj(curthing,y))*100000 ))
  return nearby

def setextents(x,y,extents):
  x *= 5
  y *= 5
  if x < extents[0]:
    extents[0] = x
  if x > extents[2]:
    extents[2] = x
  if y < extents[1]:
    extents[1] = y
  if y > extents[3]:
    extents[3] = y
  return extents


def cullneighborhood(neighborhood):
  player = neighborhood['player']
  neighborhood['fbys'] = {}
  playersensers = []
  for planet in neighborhood['planets']:
    if planet.owner and planet.owner.id == player.id:
      playersensers.append({'x': planet.x, 'y': planet.y, 'r': planet.senserange()})

  for fleet in neighborhood['fleets']:
    if fleet.owner == player:
      playersensers.append({'x': fleet.x, 'y': fleet.y, 'r': fleet.senserange()})
    
  for f in neighborhood['fleets']:
    f.keep=0
    if f.owner == player:
      f.keep=1
      continue
    f.keep=0
    for s in playersensers:
      d = math.sqrt((s['x']-f.x)**2 + (s['y']-f.y)**2)
      if d < s['r']:
        f.keep=1
  
  for f in neighborhood['fleets']:
    if f.keep == 1:
      if f.sector.key not in neighborhood['fbys']:
        neighborhood['fbys'][f.sector.key] = []
      neighborhood['fbys'][f.sector.key].append(f)
  return neighborhood



def findbestdeal(curplanet, destplanet, quatloos, capacity, dontbuy, nextforeign):
  bestprofit = -10000.0
  bestitem = "none"
  curprices = curplanet.getprices(False)
  destprices = destplanet.getprices(nextforeign)
  #print "---"
  #print str(curprices)
  #print str(destprices)
  #print "---"
  numavailable = 0
  numbuyable = 0

  for item in destprices:
    if curprices < 0:
      print "curprice < 0..."
      continue
    if item in dontbuy:
      continue
    if not curprices.has_key(item):
      continue
    elif curprices[item] >= quatloos:
      continue
    #    10                  8
    else:
      numavailable = getattr(curplanet.resources,item)*2
      if curprices[item] > 0:
        numbuyable = quatloos/curprices[item]
      else:
        numbuyable = 0
      if numbuyable > numavailable:
        numbuyable = numavailable

      profit = destprices[item]*numbuyable - curprices[item]*numbuyable
      #print item + " - " + str(profit)
      if profit > bestprofit:
        bestprofit = profit
        bestitem = item
  #print "bi=" + str(bestitem) + " bd=" + str(bestprofit)
  return bestitem, bestprofit

def buildsectorkey(x,y):
  return (int(x/5.0) * 1000) + int(y/5.0)
class BoundingBox():
  xmin = 10000.0
  ymin = 10000.0
  xmax = -10000.0
  ymax = -10000.0
  def __init__(self,stuff):
    if stuff[0] != None:
      self.xmin = stuff[0]
      self.ymin = stuff[1]
      self.xmax = stuff[2]
      self.ymax = stuff[3]
    else:
      self.xmin = 10000.0
      self.ymin = 10000.0
      self.xmax = -10000.0
      self.ymax = -10000.0
    

  def expand(self,expand):
    self.xmin -= expand
    self.xmax += expand
    self.ymin -= expand
    self.ymax += expand
  def printbb(self):
    print "bb = (" + str(self.xmin) + "," + str(self.ymin) + ")  (" + str(self.xmax) + "," + str(self.ymax) + ")"
  def addpoint(self,x,y):
    if x == None or y == None:
      return
    if x < self.xmin:
      self.xmin = x
    if y < self.ymin:
      self.ymin = y
    if x > self.xmax:
      self.xmax = x
    if y > self.ymax:
      self.ymax = y
  def intersection(self,other):
    minx = self.xmin if self.xmin > other.xmin else other.xmin
    miny = self.ymin if self.ymin > other.ymin else other.ymin
    maxx = self.xmax if self.xmax < other.xmax else other.xmax
    maxy = self.ymax if self.ymax < other.ymax else other.ymax
    return (minx,miny,maxx,maxy)

  def overlaps(self,other):
    if self.xmin == 10000 or self.ymin == 10000:
      return 0
    if self.xmin >= other.xmin and self.xmin <= other.xmax:
      if self.ymin >= other.ymin and self.ymin <= other.ymax:
        return 1
      if self.ymax >= other.ymin and self.ymax <= other.ymax:
        return 1
    if self.xmax >= other.xmin and self.xmax <= other.xmax:
      if self.ymin >= other.ymin and self.ymin <= other.ymax:
        return 1
      if self.ymax >= other.ymin and self.ymax <= other.ymax:
        return 1
    
    if other.xmin >= self.xmin and other.xmin <= self.xmax:
      if other.ymin >= self.ymin and other.ymin <= self.ymax:
        return 1
      if other.ymax >= self.ymin and other.ymax <= self.ymax:
        return 1
    if other.xmax >= self.xmin and other.xmax <= self.xmax:
      if other.ymin >= self.ymin and other.ymin <= self.ymax:
        return 1
      if other.ymax >= self.ymin and other.ymax <= self.ymax:
        return 1

    return 0



def print_timing(func):
  def wrapper(*arg):
    t1 = time.time()
    res = func(*arg)
    t2 = time.time()
    print '----- %s took %0.3f ms -----' % (func.func_name, (t2-t1)*1000.0)
    return res
  return wrapper

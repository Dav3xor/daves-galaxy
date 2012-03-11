from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import models, connection, transaction
from django.core.mail import send_mail
from django.db.models import Q, Avg, Sum, Min, Max, Count
from django.utils.html import escape

from pprint import pprint
import datetime
import math
import operator
import random
import aliens
import time
import sys
from newdominion.dominion.util import *
from newdominion.dominion.constants import *
from util import dprint
from operator import itemgetter
from pprint import pprint
import simplejson

#        class: PlanetUpgrade
#  description: represents an instance of a Planet Upgrade (sensor array, 
#               mind control, etc...)
#         note:

localcache = {}


class PlanetUpgrade(models.Model):
  planet = models.ForeignKey('Planet')
  instrumentality = models.ForeignKey('Instrumentality')
  state = models.PositiveIntegerField(default=0)
  raised = models.ForeignKey('Manifest')
  BUILDING   = 0 
  ACTIVE     = 1
  DESTROYED  = 2
  INACTIVE   = 3
  DAMAGED    = 4
  states = ['Building','Active','Destroyed','Inactive','Damaged']
  def currentcost(self,commodity):
    cost = 0
    if self.state in [PlanetUpgrade.BUILDING, PlanetUpgrade.DAMAGED]:
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
    >>> localcache['costs'] = {}
    >>> localcache['costs'][p.id] = {}
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
    >>> pprint (localcache['costs'][p.id])
    {'food': 80, 'people': 80, 'quatloos': 80, 'steel': 8}
    >>> up.doturn([])
    >>> pprint (localcache['costs'][p.id])
    {'food': 100, 'people': 100, 'quatloos': 100, 'steel': 10}
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
    >>> localcache['costs'][p.id] = {}
    >>> up.doturn([])
    >>> up.state
    1 
    >>> localcache['costs'][p.id]['quatloos'] == up.instrumentality.minupkeep
    True
    >>> p.society = 100
    >>> p.resources.people = 10000
    >>> p.resources.food = 10000
    >>> p.resources.steel =  2000
    >>> p.resources.antimatter = 1000
    >>> p.resources.quatloos = 20000
    >>> p.save()
    >>> localcache['costs'][p.id] = {}
    >>> up2 = PlanetUpgrade()
    >>> up2.start(p,Instrumentality.MATTERSYNTH1)
    >>> up2.save()
    >>> up2.doturn([])
    >>> pprint (localcache['costs'][p.id])
    {'antimatter': 100,
     'food': 1000,
     'people': 1000,
     'quatloos': 2000,
     'steel': 200}
    >>> up2.doturn([])
    >>> up2.percentdone()
    40
    >>> up2.doturn([])
    >>> up2.doturn([])
    >>> up2.percentdone()
    80
    >>> up2.state
    0
    >>> up2.doturn([])
    >>> up2.percentdone()
    100
    >>> up2.state
    1
    >>> pprint (localcache['costs'][p.id])
    {'antimatter': 500,
     'food': 5000,
     'people': 5000,
     'quatloos': 10000,
     'steel': 1000}
    >>> p.resources.quatloos = 100
    >>> p.resources.krellmetal = 100
    >>> up2.doturn([])
    >>> up2.state
    3
    >>> pprint (localcache['costs'][p.id])
    {'antimatter': 500,
     'food': 5000,
     'people': 5000,
     'quatloos': 10000,
     'steel': 1000}
    >>> report = []
    >>> otherreport = []
    >>> random.seed(1)
    >>> up2.dodamage(2000,1.0,report,otherreport)
    1
    >>> pprint(report)
    ['   Upgrade Damaged: Matter Synthesizer 1',
     '      lost 123 of 500 antimatter']
    >>> report = []
    >>> otherreport = []
    >>> random.seed(1)
    >>> up2.dodamage(2000,.5,report,otherreport)
    1
    >>> pprint(report)
    ['   Upgrade Damaged: Matter Synthesizer 1', '      lost 46 of 377 antimatter']
    >>> up2.state
    4
    >>> up2.raised.antimatter
    331 
    >>> up2.percentdone()
    93    
    >>> up2.doturn([])
    >>> up2.percentdone()
    97
    >>> up2.state
    4
    >>> up2.doturn([])
    >>> up2.percentdone()
    100 
    >>> up2.state
    1
    """
    replinestart = "Planet Upgrade: " + self.planet.name + " (" + str(self.planet.id) + ") "
    i = self.instrumentality
    p = self.planet
    
    if not localcache['costs'].has_key(self.planet_id):
      localcache['costs'][self.planet_id] = {}
    
    if self.state in [PlanetUpgrade.ACTIVE, PlanetUpgrade.INACTIVE]:
      cost = self.currentcost('quatloos')
      if not localcache['costs'][self.planet_id].has_key('quatloos'):
        localcache['costs'][self.planet_id]['quatloos'] = 0
      avail = self.planet.resources.quatloos - localcache['costs'][self.planet_id]['quatloos']
      if cost > avail:
        if self.state == PlanetUpgrade.ACTIVE:
          self.state = PlanetUpgrade.INACTIVE
          self.save()
      else:
        if self.state == PlanetUpgrade.INACTIVE:
          self.state = PlanetUpgrade.ACTIVE
          self.save()
        localcache['costs'][self.planet_id]['quatloos'] += cost
    elif self.state in (PlanetUpgrade.DAMAGED, PlanetUpgrade.BUILDING):
      for commodity in i.required.onhand():
        if not localcache['costs'][self.planet_id].has_key(commodity):
          localcache['costs'][self.planet_id][commodity] = 0

        avail = getattr(self.planet.resources, commodity) - localcache['costs'][self.planet_id][commodity]
        totalneeded = getattr(i.required,commodity)
        alreadyraised = getattr(self.raised, commodity)

        if alreadyraised < totalneeded:
          amount = self.currentcost(commodity)
          if amount > avail:
            amount = avail
          if amount > 0:
            if not localcache:
              self.planet.resources.straighttransferto(self.raised, commodity, amount)
            else:
              setattr(self.raised, commodity, alreadyraised+amount)
              localcache['costs'][self.planet_id][commodity] += amount
      self.raised.save()
          
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

  def dodamage(self, attackstrength, fleetdef, report, otherreport):
    i = self.instrumentality
    fulldamage = attackstrength/3000.0
    if fulldamage > .5:
      fulldamage = .5
    damages = []
    for commodity in i.required.onhand():
      chancetohit = .1+(fulldamage/2.0)
      if random.random() > chancetohit:
        continue
      if commodity in ['food','quatloos']:
        continue

      onhand = getattr(self.raised,commodity)
      damaged = int(onhand * (random.random()*fulldamage))
      damaged = int(damaged*fleetdef)
      if damaged > 0:
        setattr(self.raised,commodity,onhand-damaged)
        damages.append("      lost %d of %d %s" % (damaged,onhand,commodity))
    if len(damages):
      if self.state in [PlanetUpgrade.ACTIVE, PlanetUpgrade.INACTIVE]:
        self.state = PlanetUpgrade.DAMAGED
      report.append("   Upgrade Damaged: %s" % i.INSTRUMENTALITIES[i.type][1])
      otherreport.append("   Upgrade Damaged: %s" % i.INSTRUMENTALITIES[i.type][1])
      for i in damages:
        report.append(i) 
        otherreport.append(i) 
      self.save()
      return 1
    else:
      return 0

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
    curinstrumentality = Instrumentality.objects\
                                        .select_related('requires')\
                                        .get(type=insttype)
    # check to make sure we have the prerequisite
    if curinstrumentality.requires and PlanetUpgrade.objects.filter(
       planet=curplanet,
       state=self.ACTIVE,
       instrumentality=curinstrumentality.requires).count() < 1:
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

#        class: UpgradeAttribute
#  description: holds attribute info for Planet Upgrades, for named things, or
#               upgrades that need state (tax rates, or whatnot)
#         note:

class UpgradeAttribute(models.Model):
  upgrade = models.ForeignKey('PlanetUpgrade')
  attribute = models.CharField(max_length=50)
  value = models.CharField(max_length=50)

#        class: PlanetAttribute
#  description: holds attribute info for rare attributes (last visitor, advantages, etc)
#         note:

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

#        class: FleetAttribute
#  description: similar to PlanetAttribute, etc.
#         note:

class FleetAttribute(models.Model):
  fleet = models.ForeignKey('Fleet')
  attribute = models.CharField(max_length=50)
  value = models.CharField(max_length=50)

#        class: PlayerAttribute
#  description: similar to PlanetAttribute, et al...
#         note:

class PlayerAttribute(models.Model):
  Player = models.ForeignKey('Player')
  attribute = models.CharField(max_length=50)
  value = models.CharField(max_length=50)

#        class: Instrumentality
#  description: An Instrumentality is a type of PlanetUpgrade 
#               (PlanetUpgrade is an instance of one).
#         note:

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
  
  LRSENSORS1         = 0 # done works
  LRSENSORS2         = 1 # done works
  TRADEINCENTIVES    = 2 # done works
  RGLGOVT            = 3 # done works
  MINDCONTROL        = 4 # done works
  MATTERSYNTH1       = 5 # done works
  MATTERSYNTH2       = 6 # done works
  MILITARYBASE       = 7 # done works
  SLINGSHOT          = 8 # done works
  FARMSUBSIDIES      = 9
  DRILLINGSUBSIDIES  = 10
  PLANETARYDEFENSE   = 11


  INSTRUMENTALITIES = (
      (str(LRSENSORS1), 'Sensors 1'),
      (str(LRSENSORS2), 'Sensors 2'),
      (str(TRADEINCENTIVES), 'Trade Incentives'),
      (str(RGLGOVT), 'Regional Government'),
      (str(MINDCONTROL), 'Mind Control'),
      (str(MATTERSYNTH1), 'Matter Synthesizer 1'),
      (str(MATTERSYNTH2), 'Matter Synthesizer 2'),
      (str(MILITARYBASE), 'Military Base'),
      (str(SLINGSHOT), 'Slingshot'),
      (str(FARMSUBSIDIES), 'Farm Subsidies'),
      (str(DRILLINGSUBSIDIES), 'Drilling Subsidies'),
      (str(PLANETARYDEFENSE), 'Planetary Defense')
      )
  FLAGS = {RGLGOVT:4, 
           MATTERSYNTH1:8, 
           MILITARYBASE:16,
           MATTERSYNTH2:32,
           PLANETARYDEFENSE:256,
           FARMSUBSIDIES:512,
           DRILLINGSUBSIDIES:1024}
  

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
      

def inhabitedsectors():
  inhabited = Planet.objects.exclude(owner=None).values_list('sector_id')
  inhabited = set([i[0] for i in inhabited])
  return inhabited


class TurnReport(models.Model):
  user          = models.ForeignKey(User, unique=True)
  report    = models.TextField(null=True)



#        class: Player
#  description: DG specific player/user profile.
#         note:
class Player(models.Model):
  """
  >>> u = User(username="classplayer")
  >>> u.save()
  >>> r = Manifest(people=5000, food=1000)
  >>> r.save()
  >>> s = Sector(key=125150,x=100,y=100)
  >>> s.save()
  >>> p = Planet(resources=r, society=1,owner=u, sector=s,
  ...            x=626, y=617, r=.1, color=0x1234, name="Planet X")
  >>> p.save()
  >>> pl = Player(user=u, capital=p, color=112233)
  >>> pl.lastactivity = datetime.datetime.now()
  >>> pl.save()
  >>> pl.footprint()
  [125150]
  """
  def __unicode__(self):
    return self.user.username
  user = models.ForeignKey(User, unique=True)
  lastactivity = models.DateTimeField()
  capital      = models.ForeignKey('Planet', unique=True, editable=False)
  color        = models.CharField(max_length=15)

  appearance = models.XMLField(blank=True, schema_path=SVG_SCHEMA)
  friends    = models.ManyToManyField("self")
  enemies    = models.ManyToManyField("self")
  neighbors  = models.ManyToManyField("self", symmetrical=True)

  emailreports  = models.BooleanField('Recieve Email Turn Reports', default=True)
  showcountdown = models.BooleanField('Show Countdown Timer', default=True)
  paidthrough   = models.DateField(null=True)
  paidtype      = models.IntegerField(null=True, choices=PAID_TYPES, default=0)

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

  
  def purge(self):
    """
    >>> u = User(username="purge")
    >>> u.save()
    >>> r = Manifest(people=5000, food=1000)
    >>> r.save()
    >>> s = Sector(key=301101,x=301,y=101)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=505.5, y=506.5, r=.1, color=0x1234)
    >>> p.save()
    >>> pl = Player(user=u, capital=p, color=112233)
    >>> pl.lastactivity = datetime.datetime.now()
    >>> pl.save()
    >>> f = Fleet(owner=u, homeport=p, sector=s, x=p.x,y=p.y)
    >>> f.save()
    >>> u2 = User(username="purge2")
    >>> u2.save()
    >>> r2 = Manifest(people=5000, food=1000)
    >>> r2.save()
    >>> p2 = Planet(resources=r2, society=1,owner=u2, sector=s, name="x",
    ...            x=505.5, y=506.5, r=.1, color=0x1234)
    >>> p2.save()
    >>> pl2 = Player(user=u2, capital=p2, color=112233)
    >>> pl2.lastactivity = datetime.datetime.now()
    >>> pl2.save()
    >>> pl.neighbors.add(pl2)
    >>> pl2.neighbors.count()
    1
    >>> pl.purge()
    >>> pl2 = Player.objects.get(user__username="purge2")
    >>> pl2.neighbors.count()
    0
    >>> pl2.capital.name
    u'x'
    """
    ps = self.user.planet_set.all()
    fs = self.user.fleet_set.all()

    for p in ps:
      p.connections.clear()
      p.society /= 3

      p.sensorrange     = 0.0
      p.tariffrate      = 0.0
      p.inctaxrate      = 0.0
      p.openshipyard    = False
      p.opencommodities = False
      p.opentrade       = False
      p.save()
      if p.resources:
        for type in productionrates:
          onhand = getattr(p.resources,type)
          onhand /= 3
          setattr(p.resources,type,onhand)
        p.resources.save()
    for f in fs:
      f.inviewof.clear()
      f.inviewoffleet.clear()
      f.delete()
    self.enemies.clear()
    self.friends.clear()
    self.neighbors.clear()
    self.user.planet_set.clear()
      
  def footprint(self):
    return list(Sector.objects\
                      .filter(Q(fleet__owner=self.user)|
                              Q(planet__owner=self.user))\
                      .distinct()\
                      .values_list('key',flat=True))


  def create(self):
    """
    >>> u = User(username='create')
    >>> u.save()
    >>> p = Player(user=u)
    >>> x = p.create()
    did not find suitable
    >>> #p.capital
    """
    if len(self.user.planet_set.all()) > 0:
      # cheeky fellow
      return
    narrative = []
    self.lastactivity = datetime.datetime.now()
    
    random.seed()
   
    inhabited = inhabitedsectors()
    expanded = expandsectors(expandsectors(inhabited))
    potentials = expandsectors(expanded)
    potentials = potentials.difference(expanded)
   
    center = Point(1500.0,1500.0)

    sectors = list(potentials)
    random.shuffle(sectors)

    for sectorid in sectors:
      planetlist = Planet.objects.filter(sector=sectorid)
      
      p = Point((sectorid/1000*5)+2.5,((sectorid%1000)*5)+2.5)
      numlocal = nearbythings(Planet, p.x, p.y).filter(owner=None).count()
      if numlocal < 20:
        narrative.append("not enough distant planets")
        continue
      if getdistanceobj(center,p) < 140:
        continue

      for curplanet in planetlist: 
        distantplanets = nearbysortedthings(Planet,curplanet,2)
        distantplanets.reverse()

        for distantplanet in distantplanets:
          suitable = True
          #look at the 'distant planet' and its 5 closest 
          # neighbors and see if they are available
          if distantplanet.owner is not None:
            narrative.append("distant owner not none")
            continue 
          nearcandidates = nearbysortedthings(Planet,distantplanet,1)
          # make sure the 5 closest planets are free
          for nearcandidate in nearcandidates[:15]:
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
            if distance > 12:
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
    send_mail("Dave's Galaxy Problem!", 
              message,
              'support@davesgalaxy.com',
              ['dav3xor@gmail.com'])

    print "did not find suitable"
    return message



#        class: Manifest
#  description: represents a list of commodities/people/money attached
#               to a planet or fleet.
#         note:

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
  >>> m1.consume('food',3)
  3 
  >>> m1.consume('food',8)
  7
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
  

  def consume(self,commodity,amount):
    onhand = getattr(self,commodity)
    if amount > onhand:
      amount = onhand
      setattr(self,commodity,0)
    else:
      setattr(self,commodity,onhand-amount)
    return amount

  def manifestlist(self, skip=['id']):
    """
    >>> m = Manifest(people=1, food=2, consumergoods=3, steel=4, krellmetal=5,
    ...              unobtanium=6, antimatter=7, hydrocarbon=8, quatloos=9)
    >>> pprint(m.manifestlist())
    {'antimatter': 7,
     'consumergoods': 3,
     'food': 2,
     'hydrocarbon': 8,
     'krellmetal': 5,
     'people': 1,
     'quatloos': 9,
     'steel': 4,
     'unobtanium': 6}
    >>> pprint(m.manifestlist(['id','people']))
    {'antimatter': 7,
     'consumergoods': 3,
     'food': 2,
     'hydrocarbon': 8,
     'krellmetal': 5,
     'quatloos': 9,
     'steel': 4,
     'unobtanium': 6}
    
    """
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

#        class: Fleet
#  description: represents a fleet of ships and it's state.
#         note:

class Fleet(models.Model):
  owner            = models.ForeignKey(User)
  name             = models.CharField(max_length=50)
  inviewof         = models.ManyToManyField(User, related_name="inviewof")
  inviewoffleet    = models.ManyToManyField('Fleet', 
                                            related_name="viewable",
                                            symmetrical=False)
  sensorrange      = models.FloatField(default=0, null=True, editable=False)

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

  route            = models.ForeignKey('Route', null=True)
  curleg           = models.PositiveIntegerField(default=0)
  routeoffsetx     = models.FloatField(default=0)
  routeoffsety     = models.FloatField(default=0)

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
    """
    >>> f = Fleet(scouts=1,blackbirds=1,arcs=1)
    >>> f.shiplist()
    {'blackbirds': 1, 'arcs': 1, 'scouts': 1}
    """
    ships = {}
    for type in self.shiptypeslist():
      numships = getattr(self, type.name)
      ships[type.name] = numships
    return ships



  def upkeepcost(self):
    """
    >>> f = Fleet()
    >>> f.upkeepcost()
    {}
    >>> f = Fleet(scouts=5)
    >>> f.upkeepcost()
    {'food': 5, 'quatloos': 100}
    >>> f = Fleet(scouts=1,blackbirds=1,arcs=1,
    ...           merchantmen=1,bulkfreighters=1,
    ...           fighters=1,frigates=1, subspacers=1,
    ...           destroyers=1, cruisers=1, battleships=1,
    ...           superbattleships=1, carriers=1)
    >>> f.upkeepcost()
    {'food': 201, 'quatloos': 992}
    """
    ships = self.shiplist()
    costs = {}
    for type in ships:
      upkeep = shiptypes[type]['upkeep']
      for commodity in upkeep:
        if not costs.has_key(commodity):
          costs[commodity] = 0
        costs[commodity] += upkeep[commodity]*ships[type]
    return costs 




  def shiplistreport(self):
    """
    >>> f = Fleet()
    >>> f.shiplistreport()
    'no ships'
    >>> f.destroyed = True
    >>> f.shiplistreport()
    'destroyed'
    >>> f = Fleet(scouts=1,blackbirds=1,arcs=1)
    >>> f.shiplistreport()
    '1 scout, 1 blackbird, 1 arc'
    """
    output = []
    if self.numships() == 0:
      if self.destroyed == True:
        return "destroyed"
      else:
        return "no ships"
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



  def json(self, routes, playersship=0):
    json = {}
    json['x'] = self.x
    json['y'] = self.y
    json['i'] = self.id
    if self.owner_id:
      json['o'] = self.owner_id
    json['s'] = self.senserange()
    json['sl'] = self.shiplistreport()
    json['n'] = self.numships()
  
    json['f'] = 0
    if self.destroyed == True:
      json['f'] += 1
    elif self.damaged == True:
      json['f'] += 2
    #figure out what "type" of fleet it is...
    if self.scouts == json['n']:
      json['f'] += 4
    elif self.arcs > 0:
      json['f'] += 8
    elif self.merchantmen > 0 or self.bulkfreighters > 0:
      json['f'] += 16
    else:   
      # probably military
      json['f'] += 32

    if playersship and self.route:
      json['r'] = self.route_id
      json['cl'] = self.curleg
      if self.route_id not in routes:
        routes[self.route_id] = self.route.json()

    if playersship == 1:
      json['ps'] = 1
    if self.dx != self.x or self.dy!=self.y:
      distanceleft = getdistance(self.x,self.y,self.dx,self.dy)
      angle = math.atan2(self.x-self.dx,self.y-self.dy)
      if distanceleft > .2 and not self.route:
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
    """
    >>> buildinstrumentalities()
    >>> u = User(username="scrapfleet")
    >>> u.save()
    >>> r = Manifest(food=200000)
    >>> r.save()
    >>> s = Sector(key=123125,x=101,y=101)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            name="scrapfleet",
    ...            x=615, y=625, r=.1, color=0x1234)
    >>> p.save()
    >>> r2 = Manifest()
    >>> r2.save()
    >>> p2 = Planet(resources=r2, society=100,owner=u, sector=s,
    ...            name="scrapfleet2",
    ...            x=615, y=625, r=.1, color=0x1234)
    >>> p2.save()
    >>> pl = Player(user=u, capital=p, color=112233)
    >>> pl.lastactivity = datetime.datetime.now()
    >>> pl.save()
    >>> r2 = Manifest(quatloos=5000, unobtanium=1)
    >>> r2.save()
    >>> f = Fleet(owner=u, sector=s, homeport=p, x=p.x+5, y=p.y+5, 
    ...           trade_manifest=r2, source=p, bulkfreighters=1)
    >>> f.save()
    >>> # you can only scrap if the fleet is in port, so this fails
    >>> f.scrap()
    0
    >>> f.x = p.x
    >>> f.y = p.y
    >>> f.save()
    >>> pprint(f.trade_manifest.manifestlist())
    {'antimatter': 0,
     'consumergoods': 0,
     'food': 0,
     'hydrocarbon': 0,
     'krellmetal': 0,
     'people': 0,
     'quatloos': 5000,
     'steel': 0,
     'unobtanium': 1}
    >>> p.getprice('unobtanium',False)
    20000
    >>> f.scrap()
    1
    >>> f.trade_manifest.food
    0
    >>> f.trade_manifest.quatloos
    0
    >>> p.resources.quatloos
    25000
    >>> p.resources.unobtanium
    1
    >>> p.resources.people
    20
    >>> p.resources.food
    200020
    >>> p.resources.steel
    2500
    >>> p.resources.antimatter
    50 
    >>> # test trade fleet scrapping...
    >>> p.resources.antimatter=50
    >>> p.resources.food=2020
    >>> p.resources.consumergoods=0
    >>> p.resources.hydrocarbon=0
    >>> p.resources.krellmetal=0
    >>> p.resources.people=20
    >>> p.resources.quatloos=25000
    >>> p.resources.steel=2500
    >>> p.resources.unobtanium=1
    >>> pprint(p.resources.manifestlist())
    {'antimatter': 50,
     'consumergoods': 0,
     'food': 2020,
     'hydrocarbon': 0,
     'krellmetal': 0,
     'people': 20,
     'quatloos': 25000,
     'steel': 2500,
     'unobtanium': 1}
    >>> f = Fleet()
    >>> f.newfleetsetup(p,{'bulkfreighters':1})
    <Fleet: (7) 1 ship>
    >>> r=[]
    >>> p.prices.food = 2
    >>> p2.getprice('food',False)
    10
    >>> f.dotrade(r,f.inport(),p2)
    >>> print r
    ['  Trading at scrapfleet (10)  bought 1000 food with 2000 quatloos', '  Trading at scrapfleet (10)  new destination = scrapfleet2 (11)']

    >>> pprint(p.resources.manifestlist())
    {'antimatter': 0,
     'consumergoods': 0,
     'food': 1000,
     'hydrocarbon': 0,
     'krellmetal': 0,
     'people': 0,
     'quatloos': 20500,
     'steel': 0,
     'unobtanium': 1}
    >>> pprint(f.trade_manifest.manifestlist())
    {'antimatter': 0,
     'consumergoods': 0,
     'food': 1000,
     'hydrocarbon': 0,
     'krellmetal': 0,
     'people': 0,
     'quatloos': 3000,
     'steel': 0,
     'unobtanium': 0}
    >>> f.scrap()
    1
    >>> pprint(p.resources.manifestlist())
    {'antimatter': 50,
     'consumergoods': 0,
     'food': 2020,
     'hydrocarbon': 0,
     'krellmetal': 0,
     'people': 20,
     'quatloos': 25000,
     'steel': 2500,
     'unobtanium': 1}
    """
    # can't scrap the fleet if it's not in port
    if not self.inport():
      return 0

    planetresources = []
    planet = self.inport()
    if not planet:
      return 0

    if planet.resources == None:
      r = Manifest()
      r.save()
      planet.resources = r


    for shiptype in self.shiptypeslist():
      type = shiptype.name
      numships = getattr(self,type)

      for commodity in shiptypes[type]['required']:
        remit = shiptypes[type]['required'][commodity]
        if commodity == 'quatloos':
          if type == 'merchantmen':
            remit -= 5000
          elif type == 'bulkfreighters':
            remit -= 5000
        onplanet = getattr(planet.resources,commodity)
        setattr(planet.resources,commodity, onplanet + numships * remit)

      setattr(self,type,0)
    
    if self.trade_manifest:
      self.selltoplanet(planet,[],'')
      #return money to home port's treasury
      if self.homeport_id == planet.id:
        planet.resources.quatloos += self.trade_manifest.quatloos
      else : 
        self.homeport.resources.quatloos += self.trade_manifest.quatloos
        self.homeport.resources.save()
      self.trade_manifest.quatloos = 0
      self.trade_manifest.delete()
    planet.resources.save()
    self.delete()
    return 1



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



  def gotoplanet(self,destination, resettrade = False):
    """
    >>> buildinstrumentalities()
    >>> u = User(username="gotoplanet")
    >>> u.save()
    >>> r = Manifest(people=5000, food=10000, hydrocarbon=50000)
    >>> r.save()
    >>> s = Sector(key=123125,x=101,y=101)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=615, y=625, r=.1, color=0x1234)
    >>> p.save()
    >>> pl = Player(user=u, capital=p, color=112233)
    >>> pl.lastactivity = datetime.datetime.now()
    >>> pl.save()
     
    >>> r2 = Manifest(people=5000, steel=10000, consumergoods=10000, food=1)
    >>> r2.save()
    >>> p2 = Planet(resources=r2, society=50,owner=u, sector=s,
    ...             x=615, y=628, r=.1, color=0x1234)
    >>> p2.save()
    >>> r3 = Manifest(people=1600000, consumergoods=20000, food=10000000000)
    >>> r3.save()
    >>> p3 = Planet(resources=r3, society=100,owner=u, sector=s,
    ...             x=615, y=627, r=.1, color=0x1234)
    >>> p3.save()
    >>> f = Fleet()
    >>> f.newfleetsetup(p,{'bulkfreighters':1})
    <Fleet: (3) 1 ship>
    >>> f.bulkfreighters
    1
    >>> f.disposition
    8
    >>> f.trade_manifest.quatloos
    5000
    >>> p.getprice('food',False)
    3 
    >>> p.getprice('hydrocarbon',False)
    25 
    >>> f.save()
    >>> f.gotoplanet(p2,True)
    >>> pprint(f.trade_manifest.manifestlist())
    {'antimatter': 0,
     'consumergoods': 0,
     'food': 0,
     'hydrocarbon': 200,
     'krellmetal': 0,
     'people': 0,
     'quatloos': 0,
     'steel': 0,
     'unobtanium': 0}


    >>> f.speed
    0
    >>> p.startupgrade(Instrumentality.SLINGSHOT)
    1
    >>> p.setupgradestate(Instrumentality.SLINGSHOT)
    >>> f.gotoplanet(p3,True)
    >>> pprint(f.trade_manifest.manifestlist())
    {'antimatter': 0,
     'consumergoods': 0,
     'food': 0,
     'hydrocarbon': 200,
     'krellmetal': 0,
     'people': 0,
     'quatloos': 0,
     'steel': 0,
     'unobtanium': 0}

    >>> f.speed
    0.5
    >>> f.gotoplanet(p2,True)
    >>> pprint(f.trade_manifest.manifestlist())
    {'antimatter': 0,
     'consumergoods': 0,
     'food': 0,
     'hydrocarbon': 200,
     'krellmetal': 0,
     'people': 0,
     'quatloos': 0,
     'steel': 0,
     'unobtanium': 0}
    """
    self.direction = math.atan2(self.x-destination.x,self.y-destination.y)
    self.dx = destination.x
    self.dy = destination.y
    self.setsourceport()
    self.destination = destination
    if (self.x == self.source.x and 
      self.y == self.source.y and 
      self.source.hasupgrade(Instrumentality.SLINGSHOT) and
      getdistanceobj(self,destination) > .5):
      self.speed = .5
    if (resettrade and 
        self.disposition == 8 and 
        self.destination and 
        self.destination.resources and 
        self.inport()):
      report = []
      self.dotrade(report,self.inport(),destination)
    self.updatesector()
    self.save()


  def offroute(self):

    """
    >>> x1 = 1998.0
    >>> y1 = 506.0
    >>> u = User(username="offroute")
    >>> u.save()
    >>> s = Sector(key=buildsectorkey(x1,y1),x=199,y=101)
    >>> s.save()
    >>> r = Manifest(people=5000, food=1000)
    >>> r.save()
    >>> p = Planet(society=1,owner=u, sector=s,
    ...            x=x1, y=y1, r=.1, color=0x1234)
    >>> p.save()
    >>> f = Fleet(owner=u, sector=s, homeport=p, 
    ...           x=x1, y=y1, source=p, scouts=1)
    >>> f.save()
    >>> r1 = Route(owner = u)
    >>> r1.setroute('%d,1/2,3/4,%d,5/6,7/8,%d'%(p.id,p.id,p.id))
    1
    >>> r1.save()
    >>> r1id = r1.id
    >>> fid = f.id
    >>> f.ontoroute(r1)
    >>> f.save()
    >>> f.route
    <Route: Unnamed Route -- (2)>
    >>> f.offroute()
    >>> f.route
    >>> Route.objects.filter(id=r1id).count()
    0
    >>> Fleet.objects.filter(id=fid).count()
    1
    >>> r1.name = "haha"
    >>> r1.save()
    >>> f.ontoroute(r1)
    >>> f.save()
    >>> f.offroute()
    >>> f.route
    >>> Route.objects.filter(id=r1id).count()
    1
    >>> Fleet.objects.filter(id=fid).count()
    1
    """
    if self.route and self.route.name == "":
      oldroute = self.route
      self.route.fleet_set.remove(self)
      if oldroute.fleet_set.count() == 0:
        oldroute.delete()
      self.curleg = 0
    elif self.route:
      #self.route = None
      self.route.fleet_set.remove(self)
      self.curleg = 0


  def ontoroute(self, route, x=False, y=False, resettrade=False):
    """
    >>> x1 = 1999.0
    >>> y1 = 506.0
    >>> u = User(username="ontoroute")
    >>> u.save()
    >>> s = Sector(key=buildsectorkey(x1,y1),x=199,y=101)
    >>> s.save()
    >>> r = Manifest(people=5000, food=1000)
    >>> r.save()
    >>> p = Planet(society=1,owner=u, sector=s,
    ...            x=x1, y=y1, r=.1, color=0x1234)
    >>> p.save()
    >>> f = Fleet(owner=u, sector=s, homeport=p, 
    ...           x=x1, y=y1, source=p, scouts=1)
    >>> f.save()
    >>> r1 = Route(owner = u)
    >>> r1.setroute('%d,1/2,3/4,%d,5/6,7/8,%d'%(p.id,p.id,p.id))
    1
    >>> f.ontoroute(r1)
    >>> f.dx
    1.0
    >>> f.dy
    2.0
    >>> f.curleg
    1
    >>> r1.setroute('10/11,%d,1/2,3/4,%d,5/6,7/8,%d'%(p.id,p.id,p.id))
    1
    >>> f.route = None
    >>> f.ontoroute(r1)
    >>> f.dx
    10.0
    >>> f.dy
    11.0
    >>> f.curleg
    0 
    """
    if self.route != route:
      self.offroute()
    self.route = route
    waypoints = self.route.getroute()
    firstpoint = waypoints[0]
    fx = firstpoint[-2]
    fy = firstpoint[-1]
    if x and y:
      closest = self.route.closestleg(Point(x,y))
      self.curleg = closest
      self.gotoloc(x,y)
    else:
      if abs(self.x-fx) < .0001 and abs(self.y-fy) < .0001 and len(waypoints)>1:
        self.curleg = 1
        firstpoint = waypoints[1]
      else:
        self.curleg = 0
      if len(firstpoint) == 2:
        self.gotoloc(firstpoint[0],firstpoint[1])
      elif len(firstpoint) == 3:
        self.gotoplanet(Planet.objects.get(id=firstpoint[0]))
    self.routeoffsetx = 0
    self.routeoffsety = 0
    np = self.route.nextplanet(self.curleg)
    if (resettrade and 
        self.disposition == 8 and 
        np and
        np.resources and
        self.inport()):
      # NOTE: if the fleet is in port at the first planet
      # in the route, it won't buy anything (should probably fix this)
      self.destination = np
      self.dotrade([],self.inport(),np)
    self.save()
  
  def gotoloc(self,dx,dy):
    """
    >>> u = User(username="gotoloc")
    >>> u.save()
    >>> r = Manifest(people=5000, food=1000)
    >>> r.save()
    >>> s = Sector(key=123125,x=101,y=101)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=615, y=625, r=.1, color=0x1234)
    >>> p.save()
    >>> f = Fleet(owner=u, sector=s, homeport=p, x=p.x, y=p.y, source=p, scouts=1)
    >>> f.save()
    >>> f.gotoloc(625,635)
    >>> f.offroute()
    >>> f.cruisers=6
    >>> f.frigates=6
    >>> f.merchantmen=30
    >>> f.subspacers=1
    >>> f.arcs=15
    >>> f.save()
    >>> f.offroute()
    >>> f.x = 1000
    >>> f.y = 1000
    >>> f.gotoloc(626,636)
    >>> f.sector_id
    200200
    """
    self.dx = float(dx)
    self.dy = float(dy)
    self.direction = math.atan2(self.x-self.dx,self.y-self.dy)
    self.setsourceport()
    if (self.x == self.source.x and 
      self.y == self.source.y and 
      self.source.hasupgrade(Instrumentality.SLINGSHOT) and
      getdistance(self.x,self.y,self.dx,self.dy) > .5):
      self.speed = .5
    self.destination = None
    self.updatesector()
    self.save()

  def updatesector(self):
    sectorkey = buildsectorkey(self.x,self.y)
    if self.sector_id != sectorkey:
      if Sector.objects.filter(key=sectorkey).count() == 0:
        sector = Sector(key=sectorkey, x=int(self.x), y=int(self.y))
        sector.save()
        self.sector = sector
      else:
        self.sector = Sector.objects.get(key=sectorkey)


  def arrive(self, replinestart, report, planet):
    """
    >>> random.seed(1)
    >>> repstart = "-->"
    >>> report = []
    >>> u = User(username="arrive")
    >>> u.save()
    >>> s = Sector(buildsectorkey(1001,1071),x=101,y=101)
    >>> s.save()
    >>> p = Planet(society=1, sector=s,
    ...            x=1001, y=1071, r=.1, color=0x1234)
    >>> p.save()
    >>> f = Fleet(owner=u, sector=s, homeport=p, x=p.x, y=p.y, 
    ...           source=p, destination=p, scouts=1)
    >>> f.save()
    >>> f.gotoplanet(p)
    >>> f.arrive(repstart,report,p)
    >>> pprint (report)
    ['-->Arrived at  (1)']
    >>> f.x
    1001
    >>> p.getattribute('lastvisitor')
    'arrive'
    >>> f.arcs = 1
    >>> f.disposition = 6
    >>> f.save()
    >>> report = []
    >>> f.arrive(repstart,report,p)
    >>> pprint (report)
    ['-->Arrived at  (1)',
     '  Last Visitor: arrive',
     'New Colony: Fleet #1 started colony at  (1)']
    >>> f.arcs = 1
    >>> f.disposition = 6
    >>> f.save()
    >>> report = []
    >>> f.arrive(repstart,report,p)
    >>> pprint (report)
    ['-->Arrived at  (1)', 'Bolstered Colony: Fleet #1 bolstered colony at  (1)']
    >>> m = Manifest(consumergoods=50, quatloos=10)
    >>> m.save()
    >>> f.trade_manifest = m
    >>> f.disposition = 8
    >>> f.merchantmen=1
    >>> f.save()
    >>> report = []
    >>> f.arrive(repstart,report,p)
    >>> pprint (report)
    ['-->Arrived at  (1)',
     '  Trading at  (1)  selling 50 consumergoods for 1500 quatloos.',
     '  Trading at  (1)  bought 377 food with 1508 quatloos',
     '  Trading at  (1)  new destination =  (1)']

    """
    
    if self.route:
      r = self.route.getroute()
      if not self.route.circular and self.curleg == len(r)-1:
        self.offroute()

    if planet and \
       self.x == planet.x and \
       self.y == planet.y:
      report.append(replinestart +
                    "Arrived at " +
                    planet.name + 
                    " ("+str(planet.id)+")")
      if not planet.getattribute('lastvisitor'):
        # this planet hasn't been visited...
        planet.createadvantages(report)
      if not planet.owner_id or planet.owner_id != self.owner_id:
        attributes = planet.getattributes()
        for attrib in attributes:
          if attrib == -1:
            continue
          report.append("  " + PlanetAttribute(attribute=attrib,
                                               value=attributes[attrib]).printattribute())
      planet.setattribute('lastvisitor',self.owner.username) 
      
      if self.disposition == 6 and self.arcs > 0:
        planet.colonize(self,report)
      # handle trade disposition
      if self.disposition == 8 and self.trade_manifest:   
        self.dotrade(report,planet)
    else:
      report.append(replinestart +
                    "Arrived at X = %4.2f Y = %4.2f " % (self.dx, self.dy))
      self.save()
    if self.route:
      self.nextleg()



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
      valid.append(DISPOSITIONS[7])
      valid.append(DISPOSITIONS[9])
      valid.append(DISPOSITIONS[10])
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
      for i in range(numships):
        ship = {}
        ship['type'] = type.name
        ship['att'] = int(shiptype['att'])
        ship['def'] = int(shiptype['def'])
        ship['sense'] = shiptype['sense']
        ship['effrange'] = shiptype['effrange']
        shiplist.append(ship)
    return sorted(shiplist, key=itemgetter('att'), reverse=True)



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



  def calculatesenserange(self):
    """
    >>> u = User(username="fleetcalculatesenserange")
    >>> u.save()
    >>> r = Manifest()
    >>> r.save()
    >>> s = Sector(key=123126,x=101,y=101)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=615, y=625, r=.1, color=0x1234)
    >>> p.save()
    >>> f = Fleet(sector=s, owner=u, homeport=p, scouts=1)
    >>> f.calculatesenserange()
    0.512
    >>> f.senserange()
    0.512
    """
    range = 0
    if not self.owner_id:
      return range
    if self.numships() > 0:
      range =  max([shiptypes[x.name]['sense'] for x in self.shiptypeslist()])
      range += min([self.homeport.society*.002, .2])
      range += min([self.numships()*.01, .2])
    self.sensorrange = range
    return range

  def senserange(self):
    return self.sensorrange

  def numships(self):
    return sum([getattr(self,x.name) for x in self.shiptypeslist()]) 



  def inport(self):
    port = False
    if self.homeport and getdistanceobj(self,self.homeport) == 0.0:
      port = self.homeport 
    elif self.destination and getdistanceobj(self,self.destination) == 0.0:
      port = self.destination 
    elif self.source and getdistanceobj(self,self.source) == 0.0:
      port = self.source 
    return port
    
    

  def dotrade(self,report, curplanet, forcedestination = None):
    """
    >>> buildinstrumentalities()
    >>> Planet.objects.all().delete()
    >>> u = User(username="dotrade")
    >>> u.save()
    >>> r = Manifest(quatloos=1000, people=5000, food=10, steel=5000)
    >>> r.save()
    >>> s = Sector(key=125123,x=100,y=100)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=626, y=617, r=.1, color=0x1234, name="Planet X")
    >>> p.save()
    >>> pl = Player(user=u, capital=p, color=112233)
    >>> pl.lastactivity = datetime.datetime.now()
    >>> pl.save()
    >>> r2 = Manifest(people=5000, food=1000, consumergoods=5)
    >>> r2.save()
    >>> p2 = Planet(resources=r2, society=100,owner=u, sector=s,
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
    >>> p.resources.quatloos
    1000
    >>> f.dotrade(report,p)
    >>> f.trade_manifest.save()
    >>> p.resources.save()
    >>> f.destination
    <Planet: Planet Y-2>
    >>> pprint(report)
    ['  Trading at Planet X (1)  out of money, restocking.',
     '  Trading at Planet X (1)  bought 43 steel with 989 quatloos',
     '  Trading at Planet X (1)  bought 2 food with 18 quatloos',
     u'  Trading at Planet X (1)  new destination = Planet Y (2)']
    >>> print p.resources.quatloos
    1007
    >>> pprint(f.trade_manifest.manifestlist())
    {'antimatter': 0,
     'consumergoods': 0,
     'food': 2,
     'hydrocarbon': 0,
     'krellmetal': 0,
     'people': 0,
     'quatloos': 3,
     'steel': 43,
     'unobtanium': 0}


    >>> f.x = p2.x
    >>> f.y = p2.y
    >>> report = []
    >>> p2.getprice('consumergoods',False)
    29
    >>> p2.availablefortrade('consumergoods')
    5
    >>> f.trade_manifest.quatloos
    3 
    >>> p2.resources.consumergoods
    5 
    >>> f.dotrade(report,p2)
    >>> f.trade_manifest.save()
    >>> pprint(report)
    ['  Trading at Planet Y (2)  selling 2 food for 20 quatloos.',
     '  Trading at Planet Y (2)  selling 43 steel for 4300 quatloos.',
     '  Trading at Planet Y (2)  bought 5 consumergoods with 145 quatloos',
     u'  Trading at Planet Y (2)  new destination = Planet X (1)']
    >>> p2 = Planet.objects.get(name="Planet Y")
    >>> p2.resources.consumergoods
    0
    >>> f.trade_manifest.consumergoods
    5
    >>> f.trade_manifest.quatloos
    4178    
    >>> f.x = p.x
    >>> f.y = p.y
    >>> report = []
    >>> f.dotrade(report,p)
    >>> f.trade_manifest.save()
    >>> p.resources.save()
    >>> pprint(report)
    ['  Trading at Planet X (1)  selling 5 consumergoods for 150 quatloos.',
     '  Trading at Planet X (1)  bought 188 steel with 4324 quatloos',
     u'  Trading at Planet X (1)  new destination = Planet Y (2)']

    >>> f.x = p2.x
    >>> f.y = p2.y
    >>> report = []
    >>> f.dotrade(report, p2)
    >>> f.trade_manifest.save()
    >>> p2.resources.save()
    >>> pprint(report)
    [u'  Trading at Planet Y (2)  selling 188 steel for 18800 quatloos.',
     u'  Trading at Planet Y (2) could not find profitable route (fleet #1)']

    """
    if not curplanet:
      return
    dontbuy = ['id','people']
    replinestart = "  Trading at " + curplanet.name + " ("+str(curplanet.id)+") "

    if self.trade_manifest is None:
      report.append(replinestart+"can't trade without trade goods.")
      self.gotoplanet(self.homeport)
      return
    if curplanet.resources is None:
      report.append(replinestart+"planet doesn't support trade.")
      self.gotoplanet(self.homeport)
      return

    if curplanet == forcedestination:  
      print "destination = forcedestination"


    foreign = False
    if curplanet.owner_id != self.owner_id: 
      foreign = True

    #
    # selling onboard commodities to planet here!
    #
    
    if forcedestination:
      self.selltoplanet(curplanet,report,
                        replinestart)
    else:
      dontbuy += self.selltoplanet(curplanet,report,
                                   replinestart)

    capacity = self.holdcapacity()
    
    bestdif = -10000.0
    bestplanet = 0
    bestcommodities = 0 

    # should we pay taxes? (curplanet is homeport)
    if (not forcedestination) \
       and self.trade_manifest.quatloos > capacity*50 \
       and curplanet.id == self.homeport_id:
      curplanet.resources.quatloos += self.trade_manifest.quatloos - capacity*40
      self.trade_manifest.quatloos = capacity*40 

    # something bad happened, transfer some money to the fleet so that it
    # doesn't aimlessly wander the universe, doing nothing...
    elif self.trade_manifest.quatloos < 500 and \
       curplanet.id == self.homeport_id:
      resupplyamt = 5000 * (self.merchantmen+self.bulkfreighters)

      curplanet.resources.straighttransferto(self.trade_manifest, 
                                                 'quatloos', 
                                                 resupplyamt)
      report.append(replinestart+" out of money, restocking.")

    # first see if we're being forced somewhere
    if forcedestination:
      bestplanet = forcedestination 
      nextforeign = True
      if bestplanet.owner == self.owner:
        nextforeign = False
      bestcommodities, bestdif = findbestdeal(curplanet,
                                              bestplanet, 
                                              self, 
                                              dontbuy)
      
    # then see if we need to go home...
    elif self.bulkfreighters > 0 and \
       curplanet.resources.food > 0 and \
       self.homeport.productionrate('food') < 1.0 and \
       curplanet != self.homeport:
      bestplanet = self.homeport
      bestcommodities = [['food',-1]]
      bestdif = 1
    elif capacity and \
         self.trade_manifest.quatloos > capacity*50 and \
         curplanet.id != self.homeport_id:
      report.append(replinestart + 
                    " going home!")
      distance = getdistanceobj(self,self.homeport)

      nextforeign = False
      if self.owner != self.homeport.owner:
        nextforeign = True
      
      bestplanet = self.homeport
      bestcommodities, bestdif = findbestdeal(curplanet,
                                              bestplanet, 
                                              self,
                                              dontbuy)

    # too poor to be effective, go home for resupply... (piracy?)
    elif self.trade_manifest.quatloos < 500 and curplanet != self.homeport:
      bestplanet = self.homeport
      bestcommodities = [['food',-1]]
      bestdif = 1

    # we're on a route, so continue on the route  
    elif self.route and self.route.numplanets() > 1:
      bestplanet = self.route.nextplanet(self.curleg)
      nextforeign = True
      if bestplanet.owner == self.owner:
        nextforeign = False
      bestcommodities, bestdif = findbestdeal(curplanet,
                                              bestplanet, 
                                              self, 
                                              dontbuy)
    else: 
      (bestplanet,bestcommodities) = self.findbesttradeplanet(curplanet, dontbuy)

    if bestplanet and bestcommodities and bestcommodities != 'none':
      if (not self.route) and (curplanet != bestplanet) and (not forcedestination):
        self.gotoplanet(bestplanet)
      results = self.buyfromplanet(bestcommodities,curplanet)
      for commodity,numbought,price in results:
        # depecrated, but a place holder...
        if commodity == 'people':
          report.append(replinestart + "took on " + str(getattr(m,commodity)) + " passengers.")
        else:
          report.append("%s bought %d %s with %d quatloos" % 
                        (replinestart, numbought, commodity, price))
      report.append("%s new destination = %s (%d)" % (replinestart,bestplanet.name,bestplanet.id))
      
      bestplanet.bumpcompetition()
      curplanet.bumpcompetition()
      
    else:
      report.append(replinestart + "could not find profitable route (fleet #" + str(self.id) + ")")
    self.trade_manifest.save()
    self.save()
    curplanet.resources.save()
    # disembark passengers (if they want to disembark here, otherwise
    # they wait until the next destination)
    
    
  
  def holdcapacity(self):
    return self.merchantmen*500 + self.bulkfreighters*1000
  
  def findbesttradeplanet(self,curplanet,dontbuy):
    # first build a list of nearby planets, sorted by distance
    plist = nearbythings(Planet.objects.filter(owner__isnull=False,
                                               resources__isnull=False,
                                               resources__people__gt=0)\
                                       .exclude(Q(opentrade=False) & ~Q(owner=self.owner))\
                                       .select_related('owner','resources',
                                                       'prices','foreignprices'),
                         self.x,self.y)

    capacity = self.holdcapacity()
    bestplanet = None
    bestcommodity = ""
    scores = []
    #bestdif = -10000
    bestscore = -1000000
    for destplanet in plist.iterator():
      if destplanet.id == curplanet.id:
        continue



      if atwar(self, destplanet):
        continue

      commodity = "food"
      differential = -10000

      (score,commodity) = destplanet.tradescore(self, dontbuy, curplanet)
      if score > bestscore:
        bestscore = score
        bestcommodity = commodity
        bestplanet = destplanet
    if bestplanet:
      return (bestplanet, bestcommodity)
    else:
      return (self.homeport, [['food',-1]])






  def buyfromplanet(self,items,planet):
    """
    >>> buildinstrumentalities()
    >>> u = User()
    >>> u.save()
    >>> r = Manifest(people=5000, food=1000)
    >>> r.save()
    >>> s = Sector(key=123123,x=100,y=100)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s, tariffrate=50.0,
    ...            x=100, y=100, r=.1, color=0x1234)
    >>> p.save()
    >>> p.getprice('food',False)
    7 
    >>> r = Manifest(quatloos=1000)
    >>> r.save()
    >>> f = Fleet(trade_manifest=r, merchantmen=1, owner=u, sector=s)
    >>> f.buyfromplanet([['food',-1]],p)
    [('food', 142, 994)]

    >>> p.owner=None
    >>> p.resources.food=1000
    >>> p.resources.save()
    >>> p.save()
    >>> f.trade_manifest.quatloos=1000
    >>> f.trade_manifest.food=0
    >>> p.getprice('food',False)
    7 
    >>> p.getprice('food',True)
    3 
    >>> p.resources.people=5000
    >>> f.buyfromplanet([['food',-1]],p)
    [('food', 333, 999)]
    
    # test trade incentives.
    >>> up = PlanetUpgrade()
    >>> p.startupgrade(Instrumentality.TRADEINCENTIVES)
    1
    >>> p.setupgradestate(Instrumentality.TRADEINCENTIVES)
    >>> p.resources.food = 0
    >>> p.tariffrate=0.0
    >>> p.computeprices()
    1 
    >>> p.getprice('food',False)
    12 
    >>> p.resources.quatloos
    1993 
    >>> f.trade_manifest.quatloos = 1000
    >>> f.buyfromplanet([['food',-1]],p)
    [('food', 0, 0)]
    >>> f.trade_manifest.quatloos
    1000    
    >>> p.resources.quatloos
    1993
    """
    results = []
    capacity = self.holdcapacity()

    # tariffs only happen when selling from planet

    
    foreign = False
    if self.owner != planet.owner:
      foreign = True
    
    for item, amount in items:
      unitcost = int(planet.getprice(item, foreign))
      if unitcost == 0:
        unitcost = 1
      
      # ok, you are able to buy twice the current
      # surplus of any item...
      surplus = getattr(planet.resources,item)


      if unitcost > self.trade_manifest.quatloos:
        continue
     
      if amount == -1:
        numtobuy = self.trade_manifest.quatloos/unitcost
      else:
        numtobuy = amount

      # ships are able to buy surplus * 2 + next turns
      # production of any commodity on a planet
      available = planet.availablefortrade(item)
      

      if numtobuy > capacity:
        numtobuy = capacity
      if numtobuy > available:
        numtobuy = available
      
      self.trade_manifest.quatloos = self.trade_manifest.quatloos-(numtobuy*unitcost)
      planet.resources.quatloos     += numtobuy*unitcost
      
      if planet.hasupgrade(Instrumentality.TRADEINCENTIVES):
        if surplus > 1000:
          # an incentive to buy here...
          planet.resources.quatloos -= int(.2 * (numtobuy*unitcost))
        if surplus == 0:
          # planet doesn't want to give up scarce resource 
          planet.resources.quatloos += int(.2 * (numtobuy*unitcost))
      
      setattr(planet.resources, item, available-numtobuy)

      setattr(self.trade_manifest,
              item,
              getattr(self.trade_manifest,item)+numtobuy)
      results.append((item,numtobuy,numtobuy*unitcost))
    return results



  def selltoplanet(self,planet,report,replinestart):
    """
    >>> report = []
    >>> u = User(username="selltoplanet")
    >>> u.save()
    >>> r = Manifest(quatloos=10000, people=5000, food=1000)
    >>> r.save()
    >>> s = Sector(key=123123,x=100,y=100)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=100, y=100, r=.1, color=0x1234)
    >>> p.save()
    >>> r2 = Manifest(quatloos=1000,food=1000)
    >>> r2.save()
    >>> f = Fleet(trade_manifest=r2, merchantmen=1, owner=u, sector=s)
    >>> p.getprice('food',False)
    7    
    >>> f.selltoplanet(p,report,"-->")
    ['food']
    >>> p.getprice('food',False)
    7    
    >>> f.trade_manifest.quatloos
    8000
    >>> f.trade_manifest.food
    0
    >>> pprint (report)
    ['--> selling 1000 food for 7000 quatloos.']
    >>> p.resources.quatloos
    3000
    >>> p.owner=None
    >>> p.tariffrate=50.0
    >>> f.trade_manifest.food=1000
    >>> f.trade_manifest.quatloos=1000
    >>> p.resources.people=5000
    >>> p.resources.food=1000
    >>> p.resources.quatloos=8000
    >>> p.computeprices()
    1
    >>> p.getprice('food',True)
    3 
    >>> p.getprice('food',False)
    7 
    >>> f.selltoplanet(p,[],"-->")
    ['food']
    >>> p.resources.quatloos
    3000
    >>> p.resources.food
    2000
    >>> f.trade_manifest.quatloos
    4000
    >>> f.trade_manifest.food
    0    
    
    # test trade incentives.
    >>> p.startupgrade(Instrumentality.TRADEINCENTIVES)
    1
    >>> p.setupgradestate(Instrumentality.TRADEINCENTIVES)
    >>> f.trade_manifest.food = 1000
    >>> p.tariffrate=0.0
    >>> p.computeprices()
    1 
    >>> p.getprice('food',False)
    4 
    >>> f.selltoplanet(p,[],"-->")
    ['food']
    >>> f.trade_manifest.quatloos
    8000
    >>> p.resources.quatloos
    800

    """
    # modifies planet and fleet manifests
    # but not the planet or fleet themselves
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
        
        if report != None and replinestart:
          report.append(replinestart + 
                        " selling " + str(numtosell) + " " + str(item) +
                        " for " + str(profit) +' quatloos.')
        m.quatloos += profit
        setattr(m,item,0)
        setattr(r,item,getattr(r,item)+numtosell)

        if r.quatloos - int(profit) < 0:
          r.quatloos = 0
        else:
          r.quatloos -= int(profit)  
        if foreign:
          pretax = planet.getprice(item,False)
          posttax = planet.getprice(item,True)
          tax = int(numtosell/2.0 * (posttax-pretax))
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

    return dontbuy



  def newfleetsetup(self,planet,ships):
    buildableships = planet.buildableships()
    spent = {}
    for shiptype in ships:
      if not buildableships['types'].has_key(shiptype):
        continue
      for commodity in buildableships['types'][shiptype]:
        if not spent.has_key(commodity):
          spent[commodity] = 0
        spent[commodity] += buildableships['types'][shiptype][commodity]*ships[shiptype]
      for commodity in buildableships['commodities']:
        if buildableships['commodities'][commodity] < spent[commodity]:
          return "Not enough " + commodity + " to build fleet..."
    for shiptype in ships:
      setattr(self, shiptype, ships[shiptype])
    
    planet.gathercommodities(spent)
    
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

    elif (self.holdcapacity()):
      self.disposition = 8
      manifest = Manifest()
      manifest.quatloos  = 5000 * self.merchantmen
      manifest.quatloos += 5000 * self.bulkfreighters
      manifest.save()
      self.trade_manifest = manifest
      #self.trade_manifest.save() 
    elif self.scouts + self.blackbirds == self.numships():
      self.disposition = 2
    else:
      # must be a military fleet...
      self.disposition = 5

    self.calculatesenserange()
    self.save()
    self.inviewof.add(self.owner)
    return self
        
  def distancetonextstop(self):
    """
    >>> x1 = 1989.0
    >>> y1 = 506.0
    >>> u = User(username="distancetonextstop")
    >>> u.save()
    >>> s = Sector(key=buildsectorkey(x1,y1),x=199,y=101)
    >>> s.save()
    >>> r = Manifest(people=5000, food=1000)
    >>> r.save()
    >>> p = Planet(society=1,owner=u, sector=s,
    ...            x=x1, y=y1, r=.1, color=0x1234)
    >>> p.save()
    >>> f = Fleet(owner=u, sector=s, homeport=p, 
    ...           dx = 1989.0, dy = 507.0,
    ...           x=1988.0, y=506.0, source=p, scouts=1)
    >>> f.save()
    >>> f.distancetonextstop()
    1.4142135623730951
    >>> r1 = Route(owner = u)
    >>> r1.setroute('1988.0/506.0,1988.5/506.0,%d,1990.0/506.0,1991.0/506.0,2000.0/506.0'%(p.id))
    1
    >>> f.ontoroute(r1)
    >>> f.distancetonextstop()
    1.0
    >>> f.curleg=3
    >>> f.distancetonextstop()
    12.0
    >>> r1.circular = True
    >>> f.curleg = 1
    >>> f.distancetonextstop()
    1.0
    >>> f.curleg = 3
    >>> f.distancetonextstop()
    25.0
    """
    if self.route:
      waypoints = self.route.getroute()
      distance =  getdistance(self.x, self.y, self.dx, self.dy)
      distance += getdistance(self.dx,self.dy,
                              waypoints[self.curleg][-2],
                              waypoints[self.curleg][-1])

      if self.route.circular:
        for i in xrange(0,len(waypoints)):
          j = (i+self.curleg)%len(waypoints)
          k = (j+1)%len(waypoints)
          if len(waypoints[j]) == 3:
            return distance
          distance += getdistance(waypoints[j][-2],
                                  waypoints[j][-1],
                                  waypoints[k][-2],
                                  waypoints[k][-1])
        
      else:
        for i in xrange(self.curleg,len(waypoints)-1):
          if len(waypoints[i]) == 3:
            return distance
          distance += getdistance(waypoints[i][-2],
                                  waypoints[i][-1],
                                  waypoints[i+1][-2],
                                  waypoints[i+1][-1])
        return distance
      # if we've reached this point, there is no next stop,
      # so return a large number, because the route doesn't
      # have stops.
      return 1000.0
    else:
      # no route, so distance is simply...
      return getdistance(self.x,self.y,self.dx,self.dy)
 
  def nextleg(self):
    if self.route:
      r = self.route.getroute()
      numlegs = len(r)
      if r[self.curleg][-2] == self.dx and r[self.curleg][-1] == self.dy:
        if self.route.circular:
          self.curleg = (self.curleg+1)%numlegs
        elif self.curleg < numlegs-1:
          self.curleg += 1
      if len(r[self.curleg]) == 3:   # planet
        p = Planet.objects.get(id=int(r[self.curleg][0]))
        self.gotoplanet(p)
      else:
        self.gotoloc(r[self.curleg][0],r[self.curleg][1])

  def consumelegs(self,distance):
    """
    >>> x1 = 1979.0
    >>> y1 = 506.0
    >>> u = User(username="consumelegs")
    >>> u.save()
    >>> s = Sector(key=buildsectorkey(x1,y1),x=199,y=101)
    >>> s.save()
    >>> r = Manifest(people=5000, food=1000)
    >>> r.save()
    >>> p = Planet(society=1,owner=u, sector=s,
    ...            x=x1, y=y1, r=.1, color=0x1234)
    >>> p.save()
    >>> f = Fleet(owner=u, sector=s, homeport=p, 
    ...           dx = 1989.0, dy = 507.0,
    ...           x=1978.0, y=506.0, source=p, scouts=1)
    >>> f.save()
    >>> r1 = Route(owner = u)
    >>> r1.setroute('1978.0/506.0,1978.5/506.0,%d,1980.0/506.0,1981.0/506.0,1981.5/506.0'%(p.id))
    1
    >>> f.ontoroute(r1)
    >>> f.consumelegs(.01)
    0.01
    >>> f.consumelegs(5.0)
    4.5
    >>> f.curleg
    2
    >>> f.curleg = 3
    >>> f.x = 1979.0
    >>> f.dx = 1980.0
    >>> f.consumelegs(5.0)
    3.0
    >>> f.curleg
    5
    >>> f.route.circular = True
    >>> f.route.save()
    >>> f.curleg = 3
    >>> f.x = 1979.0
    >>> f.dx = 1980.0
    >>> f.consumelegs(.01)
    0.01
    >>> f.consumelegs(10.0)
    3.5
    >>> f.curleg
    2
    >>> # test fast ships on small circular routes:
    >>> r1.setroute('1.0/1.0, 1.1/1.1, 1.0/1.1')
    1
    >>> r1.circular = True
    >>> r1.save()
    >>> f.speed = 5
    >>> f.curleg = 0
    >>> f.x = 0
    >>> f.y = 0
    >>> f.dx = .8
    >>> f.dy = 1.0
    >>> f.consumelegs(5.0)
    0.105161590140332
    """
    if not self.route:
      return distance
    else:
      waypoints = self.route.getroute()
      endleg = self.curleg
      # if we need to move some before getting onto the route, and 
      # the destination (self.dx,self.dy) is not a node on the route
      if self.dx != waypoints[endleg][-2] or self.dy != waypoints[endleg][-1]:
        tonext = getdistance(self.x,self.y,self.dx,self.dy)
        if tonext > distance:
          return distance 
        else:
          # turn the corner, so the rest of the algorithm can work.
          distance -= tonext
          self.x = self.dx
          self.y = self.dy
          self.dx = waypoints[endleg][-2]
          self.dy = waypoints[endleg][-1]
      if self.route.circular:
        if self.route.length() == 0.0:
          return distance
        pleasecontinue = True
        i = 0
        while pleasecontinue:
          j = (i+self.curleg)%len(waypoints)
          k = (j+1)%len(waypoints)
          tonext = getdistance(self.x,self.y,self.dx,self.dy)
          if tonext > distance:
            # not travelling far enough to consume this leg
            break
          if len(waypoints[j]) == 3:
            # don't pass a planet
            break
          else:
            distance -= tonext
            endleg = k
            self.x = waypoints[j][-2]
            self.y = waypoints[j][-1]
            self.dx = waypoints[k][-2]
            self.dy = waypoints[k][-1]
          i += 1
      else:
        for i in xrange(self.curleg,len(waypoints)-1):
          tonext = getdistance(self.x,self.y,self.dx,self.dy)
          if tonext > distance:
            # not travelling far enough to consume this leg
            break
          if len(waypoints[i]) == 3:
            break
          else:
            distance -= tonext
            endleg = i+1 
            self.x = waypoints[i][-2]
            self.y = waypoints[i][-1]
            self.dx = waypoints[i+1][-2]
            self.dy = waypoints[i+1][-1]
      if self.curleg != endleg:
        self.curleg = endleg
        self.direction = math.atan2(self.x-self.dx,self.y-self.dy)
      return distance

  def move(self, report, replinestart):
    """
    >>> localcache['planetarrivals'] = {}
    >>> u = User(username="move")
    >>> u.save()
    >>> r = Manifest(people=5000, food=1000)
    >>> r.save()
    >>> s = Sector(key=240240,x=1200,y=1200)
    >>> s.save()
    >>> p = Planet(resources=r, society=1, sector=s,
    ...            x=1202, y=1202, r=.1, color=0x1234)
    >>> p.save()
    >>> pl = Player(user=u, capital=p, color=112233)
    >>> pl.lastactivity = datetime.datetime.now()
    >>> pl.save()
    >>> r = Manifest(quatloos=1000,food=1000)
    >>> r.save()
    >>> f = Fleet(trade_manifest=r, merchantmen=1, owner=u, sector=s,
    ...           x=p.x,y=p.y,homeport=p, source=p)
    >>> f.gotoloc(1220,1220)
    >>> f.speed=5.0
    >>> f.x
    1202
    >>> f.y
    1202
    >>> f.sector_id
    240240
    >>> report = []
    >>> f.move(report, "")
    >>> f.x
    1205.3368369004193
    >>> f.y
    1205.3368369004193
    >>> f.sector_id
    241241
    >>> f.speed = 0
    >>> f.move(report,"")
    >>> f.x
    1205.5355339059327
    >>> f.y
    1205.5355339059327
    >>> f.sector_id
    241241
    >>> f.speed
    0.281

    """
    
    
    # see if we need to move the fleet...
    accel = self.acceleration()
    distancetodest = self.distancetonextstop()
    
    if distancetodest and \
       distancetodest < accel and \
       self.speed < accel*2.0: 
      # we have arrived at our destination
      self.speed=0
      self.x = self.dx
      self.y = self.dy
      if self.destination:
        if not localcache['planetarrivals'].has_key(self.destination_id):
          localcache['planetarrivals'][self.destination_id] = []
        localcache['planetarrivals'][self.destination_id].append(self.id)
      else:
        localcache['arrivals'].append(self.id)

    
    elif accel and distancetodest:
      
      topspeed = 5.0
      
      # if patrolling, we want to go senserange per turn
      if self.disposition == 7: 
        topspeed = self.senserange()

      daystostop = self.speed/accel
      distancetostop = .5*(self.speed)*(daystostop) # classic kinetics...

      # determine if we are speeding up, slowing down, or constant speed.
      if distancetodest<=distancetostop+self.speed-accel:
        # decelerating
        self.speed -= accel
        if self.speed <= 0:
          self.speed = 0
      elif distancetodest<=distancetostop+self.speed+accel:
        # turnover
        self.speed = self.speed
      elif self.speed < topspeed:
        # accelerating
        self.speed += accel
        if self.speed > topspeed:
          self.speed = topspeed
      elif self.speed > topspeed:
        self.speed -= accel
        if self.speed < topspeed:
          self.speed = topspeed
      else:
        # cruising
        self.speed = self.speed
      
      #now actually move the fleet...
      distanceleft = self.speed
      distanceleft = self.consumelegs(distanceleft)
      self.direction = math.atan2(self.x-self.dx,self.y-self.dy)
      self.x = self.x - math.sin(self.direction)*distanceleft
      self.y = self.y - math.cos(self.direction)*distanceleft
      report.append(replinestart + 
                    "enroute -- distance = %4.2f speed = %4.2f" % 
                    (distancetodest,self.speed)) 
    self.updatesector()
    self.save()

  def capitulationchance(self, society, population):
    """
    >>> f = Fleet(cruisers=100)
    >>> f.capitulationchance(50,8000000)
    0.060692013084810814
    >>> f.capitulationchance(50,16000000)
    0.05078991050538306
    >>> f.capitulationchance(100,16000000)
    0.05
    >>> f.capitulationchance(1,2000)
    0.3356593567319657
    
    >>> f.cruisers = 5
    >>> f.capitulationchance(50,8000000)
    0.05
    >>> f.capitulationchance(1,2000)
    0.21583006578980604
    >>> f.battleships = 1
    >>> f.cruisers = 0
    >>> f.capitulationchance(50,8000000)
    0.05
    >>> f.battleships = 2
    >>> f.capitulationchance(50,8000000)
    0.05
    >>> f.battleships = 0
    >>> f.scouts = 1
    >>> f.capitulationchance(50,8000000)
    0.005

    
    """
    attacks = self.numattacks()
    attackstrength = 0
    defensestrength = 0

    if attacks > 0:
      attackstrength = log(attacks)/25.0
      if attackstrength > .5:
        attackstrength = .5
    else:
      return 0.0

    if population > 0 and society > 0:
      defensestrength = log(population/1500.0)/70.0 + log(society)/25.0

    chance = .05 + attackstrength - defensestrength 
    if chance < .05:
      chance = .05
    
    # if the fleet is really small, trail off chances (to prevent
    # nuisance attacks from succeeding)
    if attacks<=20:
      chance = .0025*attacks

    return chance

  def doassault(self,destination,report,otherreport):
    """
    >>> buildinstrumentalities()
    >>> random.seed(1)
    >>> u = User(username="doassault1")
    >>> u.save()
    >>> u2 = User(username="doassault2")
    >>> u2.save()
    >>> r = Manifest(people=50000, food=1000)
    >>> r.save()
    >>> s = Sector(key=251251,x=1255,y=1255)
    >>> s.save()
    >>> p = Planet(resources=r, society=20, sector=s, owner=u,
    ...            name="holyshitland",               
    ...            x=1257, y=1257, r=.1, color=0x1234)
    >>> p.save()
    >>> p2 = Planet(resources=r, society=1, sector=s, owner=u2,
    ...            x=1258, y=1258, r=.1, color=0x1234)
    >>> p2.save()
    >>> pl = Player(user=u, capital=p, color=112233)
    >>> pl.lastactivity = datetime.datetime.now()
    >>> pl.save()
    >>> pl2 = Player(user=u2, capital=p2, color=112233)
    >>> pl2.lastactivity = datetime.datetime.now()
    >>> pl2.save()
    >>> f = Fleet(owner=u2, sector=s, cruisers=5,
    ...           destination=p, sensorrange=.5,
    ...           x=1257.1,y=1257.1,homeport=p2, source=p2)
    >>> f.save()
    >>> f2 = Fleet(owner=u, sector=s, cruisers=5,
    ...           destination=p, sensorrange=.5,
    ...           x=1257.1,y=1257.1,homeport=p, source=p)
    >>> f2.save()
    >>> report = []
    >>> otherreport = []
    >>> pl.setpoliticalrelation(pl2,'enemy')
    >>> f.inviewoffleet.add(f2)
    >>> f2.inviewoffleet.add(f)
    >>> f.doassault(p,report,otherreport)
    False
    >>> print str(report)
    ['  Assaulting Planet holyshitland (6): unsuccessful assault -- planet heavily defended']
    >>> f2.damaged = True
    >>> f2.save()
    >>> report = []
    >>> f.doassault(p,report,otherreport)
    True
    >>> pprint(report)
    ['  Assaulting Planet holyshitland (6): assault in progress -- raining death from space',
     '   destroyed 9 of 1000 food',
     '   destroyed 2966 of 50000 people',
     '  -- current capitulation chance -- 5.1% (failed)']
    >>> p.resources.food
    991
    >>> p.resources.people
    47034
    >>> p.startupgrade(Instrumentality.MINDCONTROL)
    1
    >>> p.setupgradestate(Instrumentality.MINDCONTROL)
    >>> p.startupgrade(Instrumentality.MATTERSYNTH1)
    1
    >>> p.setupgradestate(Instrumentality.MATTERSYNTH1)
    >>> p.startupgrade(Instrumentality.MATTERSYNTH2)
    1
    >>> p.setupgradestate(Instrumentality.MATTERSYNTH2)
    >>> p.startupgrade(Instrumentality.MILITARYBASE)
    1
    >>> p.setupgradestate(Instrumentality.MILITARYBASE)
    >>> p.startupgrade(Instrumentality.SLINGSHOT)
    1
    >>> p.setupgradestate(Instrumentality.SLINGSHOT)
    >>> report = []
    >>> f.cruisers = 1000
    >>> f.save()
    >>> f.doassault(p,report,otherreport)
    True
    >>> pprint(report)
    ['  Assaulting Planet holyshitland (6): assault in progress -- raining death from space',
     '   Upgrade Damaged: Mind Control',
     '      lost 283 of 20000 people',
     '   Upgrade Damaged: Matter Synthesizer 1',
     '      lost 111 of 500 antimatter',
     '   Upgrade Damaged: Matter Synthesizer 2',
     '      lost 12 of 1000 antimatter',
     '   Upgrade Damaged: Military Base',
     '      lost 221 of 2000 people',
     '   Upgrade Damaged: Slingshot',
     '      lost 1 of 10 antimatter',
     '   destroyed 143 of 991 food',
     '   destroyed 505 of 47034 people',
     '  -- current capitulation chance -- 26.3% (failed)']
    >>> report = []
    >>> f.cruisers = 20
    >>> f.save()
    >>> f.doassault(p,report,otherreport)
    True
    >>> pprint(report)
    ['  Assaulting Planet holyshitland (6): assault in progress -- raining death from space',
     '   Upgrade Damaged: Mind Control',
     '      lost 621 of 20000 people',
     '   destroyed 88 of 848 food',
     '   destroyed 5718 of 46529 people',
     '   society level reduced 3 of 20',
     '  -- current capitulation chance -- 11.5% (failed)']

    """
    replinestart = "  Assaulting Planet " + destination.name + " ("+str(destination.id)+"): "
    oreplinestart = "  Planet Assaulted " + destination.name + " ("+str(destination.id)+"): "
    
    damaged = False

    nf = self.inviewoffleet.filter(damaged=False,destroyed=False)
    if self.owner_id == destination.owner_id:
      return
    fleetdefenses=0
    defendingfleets=0
    for f in nf.iterator():
      if f == self:
        continue
      if f.numcombatants() == 0:
        continue
      # allied fleets provide added planetary defense
      if f.owner_id != destination.owner_id:
        if not localcache['allies'].has_key(destination.owner_id):
          continue
        if localcache['allies'][destination.owner_id].has_key(f.owner_id) == False:
          continue
      distance = getdistanceobj(f,self)
      if distance < self.senserange() or distance < f.senserange():
        defenses = f.numdefenses()
        fleetdefenses += defenses
        if defenses > 0:
          defendingfleets += 1
    if fleetdefenses > (self.numattacks()/10.0):  
      # can't assault when there's a good defense nearby...
      report.append(replinestart + "unsuccessful assault -- planet heavily defended")
      otherreport.append(oreplinestart + "unsuccessful assault -- planet is heavily defended")
      return False
    else: 
      # ok, we've made it through any defenders...
      report.append(replinestart + "assault in progress -- raining death from space")
      otherreport.append(oreplinestart + "assault in progress -- they are raining death from space")

    if fleetdefenses > 100:
      fleetdefenses = 100.0
    fleetdeffactor = 1.0-math.log(1+fleetdefenses,200)

    for u in destination.planetupgrade_set.all():
      if u.dodamage(self.numattacks(), fleetdeffactor, report, otherreport):
        damaged = True
   


    if destination.resources:
      potentialloss = self.numattacks()/1000.0
      if potentialloss > .5:
        potentialloss = .5
      for key in destination.resources.onhand():
        if key in ['quatloos']:
          continue
        curvalue = getattr(destination.resources,key)
        if curvalue > 0:
          destroyed = int(curvalue*(random.random()*potentialloss)*fleetdeffactor)
          newvalue = curvalue - destroyed
          if destroyed > 0:
            setattr(destination.resources,key,newvalue)
            damaged = True
            report.append("   destroyed %d of %d %s" % (destroyed,curvalue,key))
            otherreport.append("   destroyed %d of %d %s" % (destroyed,curvalue,key))
    
    if destination.society:
      potentialloss = self.numattacks()/1000.0
      if potentialloss > .2:
        potentialloss = .2
      if random.random() < potentialloss*3.0:
        lost = int(destination.society*(random.random()*potentialloss)*fleetdeffactor)
        if lost > 0 and destination.society - lost > 0:
          damaged = True
          report.append("   society level reduced %d of %d" % (lost, destination.society))
          destination.society -= lost
    
    capchance = self.capitulationchance(destination.society,
                                        destination.resources.people)
    if random.random() < capchance:
      damaged = True
      report.append("  -- capitulation!")
      otherreport.append("  -- capitulation!")
      #capitulation -- planet gets new owner...
      destination.owner = self.owner
      destination.makeconnections()
    else:
      text = "  -- current capitulation chance -- %3.1f%% (failed)" % (capchance*100.0)
      report.append(text)
      otherreport.append(text)
   
    return damaged


#        class: Route 
#  description: A multi leg route that a Fleet can follow 
#         note:

class Route(models.Model):
  """
  A Multi Leg route, allows you to go around things. 
  >>> r = Route()
  >>> p1 = Planet.objects.get(id=1)
  >>> p2 = Planet.objects.get(id=2)
  >>> r.setroute('%d,127.5/128.2,%d'%(p1.id,p2.id))
  1
  >>> r.circular
  False
  >>> r.name
  ""
  >>> pprint(r.legs)
  '[["1", 626.0, 617.0], [127.5, 128.2], ["2", 627.0, 616.0]]'
  >>> pprint(r.json())
  {'c': False,
   'p': '[["1", 626.0, 617.0], [127.5, 128.2], ["2", 627.0, 616.0]]'}
  >>> pprint(r.getroute())
  [['1', 626.0, 617.0], [127.5, 128.2], ['2', 627.0, 616.0]]
  >>> r.closestleg(Point(600,600))
  1 
  >>> r.closestleg(Point(700,600))
  2
  >>> r.numplanets()
  2
  >>> r.nextplanet(0).id
  2
  >>> r.length()
  1396.3204360031405
  >>> r.circular = True
  >>> r.length()
  1397.7499753922846
  >>> r.closestleg(Point(700,600))
  2
  >>> r.closestleg(Point(626.5,616.5))
  0
  >>> # test bad routes
  >>> r.setroute('safjsfdjsdgsjdgsadf')
  0
  >>> r.length()
  1396.3204360031405
  """
  def __unicode__(self):
    if self.name:
      return "Named Route -- " + self.name + "("+str(self.id)+")"
    else:
      return "Unnamed Route -- " + "("+str(self.id)+")"
  name       = models.CharField(max_length=20)
  owner      = models.ForeignKey(User)
  circular   = models.BooleanField(default=False)
  legs       = models.TextField()

  def __init__(self, *args, **kwargs):
      super(Route, self).__init__(*args, **kwargs)
      if self.legs:
        self.route = simplejson.loads(self.legs)
      else:
        self.route = []
  # set route format: 
  # planet id   location       location        planet id
  # 12345,      127.5/128.2, 128.7/120.0, 789123
  def setroute(self, route, circular=False, name=""):
    newroute = []
    route = route.split(',')
    
    if len(route)>50:
      # too long, spurious?
      return 0
    
    self.circular = circular
    self.name = name

    try:
      for r in route:
        if '/' in r:    # location
          (x,y) = r.split('/')
          x = float(x)
          y = float(y)
          newroute.append([x,y])
        else:           # planet
          p = Planet.objects.get(id=int(r))
          newroute.append([r,p.x,p.y])
      self.route = newroute
      self.legs = simplejson.dumps(newroute) 
    except:
      return 0
    return 1

  def json(self):
    json = {'p': self.legs, 'c': self.circular}
    if self.name != "":
      json['n'] = escape(self.name)
    return json

  def getroute(self):
    return self.route 

  def getlegxy(self, leg):
    if len(self.route[leg]) == 3:
      return (self.route[leg][1:])
    if len(self.route[leg]) == 2:
      return (self.route[leg])
  
  def length(self):
    routelen = len(self.route)
    if not self.circular:
      routelen -= 1
    length = 0
    for i in xrange(routelen):
      p1 = self.route[i%routelen]
      p2 = self.route[(i+1)%routelen]
      length += getdistance(p1[-2],p1[-1],
                            p2[-2],p2[-1])
    return length

  def closestleg(self, p):
    route = self.getroute()
    numlegs = numnodes = len(route)
    if not self.circular:
      numlegs -= 1
    mindistance = 100000
    closestleg = -1
    
    for i in xrange(0,numlegs):
      start = Point(self.getlegxy(i%numnodes))
      end = Point(self.getlegxy((i+1)%numnodes))
      distance = distancetoline(p,start,end)
      if distance < mindistance:
        mindistance = distance
        closestleg = i 
    return (closestleg+1)%numnodes

  def numplanets(self):
    route = self.getroute()
    numplanets = 0
    for leg in route:
      if len(leg) == 3:
        numplanets +=1
    return numplanets
      
  def nextplanet(self,curleg):
    route = self.getroute()
    numlegs = len(route)
    if self.circular:
      for i in xrange(0,numlegs):
        nextleg = route[(i+curleg+1)%numlegs]
        if len(nextleg) == 3:
          return Planet.objects.get(id = int(nextleg[0]))
    else:
      for i in xrange(curleg+1,numlegs):
        nextleg = route[i]
        if len(nextleg) == 3:
          return Planet.objects.get(id = int(nextleg[0]))
     





#        class: Message
#  description: player-player messages
#         note:

class Message(models.Model):
  def __unicode__(self):
    return self.subject
  subject = models.CharField(max_length=80)
  message = models.TextField()
  replyto = models.ForeignKey('Message', related_name="reply_to", null=True)
  fromplayer = models.ForeignKey(User, related_name='from_player')
  toplayer = models.ForeignKey(User, related_name='to_player')
  def save(self, *args, **kwargs):
    if '>' in self.message:
      self.message = self.message.replace('>','&gt;')
    if '<' in self.message:
      self.message = self.message.replace('<','&lt;')
    super(Message, self).save(*args, **kwargs) # Call the "real" save() method.
  
#        class: Sector
#  description: a sector scheme for organizing planets/fleets.
#               Sectors are keyed with their upper left corner,
#               they are 5 units tall, 5 units wide, and keyed
#               as follows:
#               (x/5)*1000 + y/5
#         note:

class Sector(models.Model):
  def __unicode__(self):
    return str(self.key)
  key = models.IntegerField(primary_key=True)
  controllingplayer = models.ForeignKey(User, null=True)
  x = models.IntegerField()
  y = models.IntegerField()

#        class: Planet
#  description: a planet/star (the names are interchangable)
#         note:


class PlanetConnection(models.Model):
  planeta = models.ForeignKey('Planet', related_name="planeta")
  planetb = models.ForeignKey('Planet', related_name="planetb")
  sector = models.ForeignKey('Sector', null=True)

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
  def unicode(self):
    return self.__unicode__()
  name = models.CharField('Planet Name', max_length=50)
  owner = models.ForeignKey(User, null=True)
  sector = models.ForeignKey('Sector')

  x = models.FloatField()
  y = models.FloatField()
  r = models.FloatField()

  color           = models.PositiveIntegerField()
  society         = models.PositiveIntegerField()
  connections     = models.ManyToManyField("self", 
                                           symmetrical=False,
                                           through="PlanetConnection")
  resources       = models.ForeignKey('Manifest', null=True)
  prices          = models.ForeignKey('Manifest', null=True, 
                                      related_name='prices')
  foreignprices   = models.ForeignKey('Manifest', null=True, 
                                      related_name='foreignprices')
  sensorrange     = models.FloatField(default=0, null=True)
  tariffrate      = models.FloatField('External Tariff Rate', default=0)
  inctaxrate      = models.FloatField('Income Tax Rate', default=0)
  damaged         = models.BooleanField(default=False)
  openshipyard    = models.BooleanField('Allow Others to Build Ships', 
                                        default=False)
  opencommodities = models.BooleanField('Allow Trading of Rare Commodities',
                                        default=False)
  opentrade       = models.BooleanField('Allow Others to Trade Here',
                                        default=False)

  
  def __init__(self, *args, **kwargs):
    super(Planet, self).__init__(*args, **kwargs)
    self.activeupgrades = {}
    self.curattributes = {}  
  def createadvantages(self, report):
    replinestart = "New Planet Survey: " + self.name + " (" + str(self.id) + "): "
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
    if localcache and localcache.has_key('upgrades'):
      if localcache['upgrades'].has_key(self.id) and \
         localcache['upgrades'][self.id].has_key(upgradetype):
        return 1
      else:
        return 0
      
    if len(self.activeupgrades) == 0:
      u = PlanetUpgrade.objects\
                       .filter(planet=self, 
                               state=PlanetUpgrade.ACTIVE)\
                       .values_list('instrumentality__type')
      for i in u:
        self.activeupgrades[i[0]] = 1
      self.activeupgrades[-1] = 1
    if upgradetype in self.activeupgrades:
      return 1
    else:
      return 0
  def startupgrade(self,upgradetype,benosy=False):
    """
    >>> u = User(username="startupgrade")
    >>> u.save()
    >>> r = Manifest()
    >>> r.save()
    >>> s = Sector(key=buildsectorkey(680,625),x=680,y=625)
    >>> s.save()
    >>> p = Planet(resources=r, society=12,owner=u, sector=s,
    ...            x=675, y=625, r=.1, color=0x1234)
    >>> p.save()
    >>> p.startupgrade(Instrumentality.MATTERSYNTH1,True)
    0
    >>> p.startupgrade(Instrumentality.LRSENSORS1,True)
    1
    """  
    if benosy and self.society < Instrumentality.objects.get(type=upgradetype).minsociety:
      return 0
    if PlanetUpgrade.objects.filter(planet=self,instrumentality__type=upgradetype).count() == 0:
      up = PlanetUpgrade()
      up.start(self,upgradetype)
      return 1
    return 0
 
  def scrapupgrade(self,upgradetype):
    up = PlanetUpgrade.objects.get(planet=self,
                                   instrumentality__type=upgradetype)
    up.scrap()
    if upgradetype in self.activeupgrades:
      del self.activeupgrades[upgradetype]

  def setupgradestate(self,upgradetype, state=PlanetUpgrade.ACTIVE):
    up = PlanetUpgrade.objects.get(planet=self,
                                   instrumentality__type=upgradetype)
    if state == PlanetUpgrade.ACTIVE:
      self.activeupgrades[upgradetype] = 1
      uptype = up.instrumentality.type
      for commodity in instrumentalitytypes[uptype]['required']:
        setattr (up.raised,
                 commodity,
                 instrumentalitytypes[uptype]['required'][commodity])
      up.raised.save()
    else:
      del self.activeupgrades[upgradetype]
    up.state = state
    up.save()


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
      
  #              _____O~==+
  #             |    \/ |<-)
  #             |  IRC  | /
  #    _________|_______|_\_____



  def fleetupkeepcosts(self):
    # tests are in Planet.doturn()...
    sums = tuple([Sum(k) for k in shiptypes.keys()])
    amounts = apply(self.home_port.aggregate,sums)
    costs = {}
    for shiptype in amounts:
      numships = amounts[shiptype]
      if numships == 0 or numships == None:
        continue
      else:
        shiptype2 = shiptype.split('_')[0]
        for cost in shiptypes[shiptype2]['upkeep']:
          if not costs.has_key(cost):
            costs[cost] = 0
          costs[cost] += numships*shiptypes[shiptype2]['upkeep'][cost]
    return costs      

  def buildconnection(self, p2):
    if PlanetConnection.objects.filter(Q(planeta=self.id, planetb=p2.id)|
                                       Q(planeta=p2.id, planetb=self.id)).count()==0:

      cx = self.x - ((self.x-p2.x)/2.0)
      cy = self.y - ((self.y-p2.y)/2.0)
      sectorkey = buildsectorkey(cx,cy)
      try:
        sector = Sector.objects.get(key=sectorkey)
      except Sector.DoesNotExist:
        sector = Sector(key=sectorkey, x = int(cx)/5, y= int(cy)/5)
        sector.save()



      # only set a sector key for one side of the connection)
      pc = PlanetConnection(planeta=self, planetb=p2,sector=sector)
      pc.save()
      pc2 = PlanetConnection(planeta=p2, planetb=self)
      pc2.save()
      return 1
    else:
      return 0

  def makeconnections(self, minconnections=0):   
    """

    >>> random.seed(1)
    >>> u = User(username="makeconnections")
    >>> u.save()
    >>> r = Manifest()
    >>> r.save()
    >>> s = Sector(key=buildsectorkey(675,625),x=675,y=625)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=675, y=625, r=.1, color=0x1234)
    >>> p.save()
    >>> p2 = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=675, y=628.2, r=.1, color=0x1234)
    >>> p2.save()
    >>> print p.makeconnections(2)
    1
    >>> pprint (p.connections.all())
    [<Planet: -25>]
    >>> pprint (p2.connections.all())
    [<Planet: -24>]
    >>> print p.makeconnections(2)
    0
    """
    def intersects(testline, lines):
      for line in lines:
        if checkintersection(testline[0],testline[1],
                             line[0],line[1]):
          return True
      return False

    def tooclose(planets, line):
      for planet in planets:
        if line[0].x == planet.x and line[0].y == planet.y:
          # if we get the planet as an endpoint, that's ok...
          continue
        if line[1].x == planet.x and line[1].y == planet.y:
          # same thing for the other endpoint 
          continue
        if distancetoline(planet, line[0], line[1]) < 1.0:
          return True
      return False

    nearbyplanets = nearbysortedthings(Planet,self)
    
    # if there are too many planets in the area, skip
    if len(nearbyplanets) > 65:
      dprint("too many ")
      return 0

    # or too few...
    if len(nearbyplanets) < 2:
      dprint("no neighbors")
      return 0

    # skip planets with neighbors nearby
    if getdistanceobj(nearbyplanets[0],nearbyplanets[1]) < .8:
      dprint("too close")
      return 0
    
    for connection in self.connections.all():
      if connection.owner != None and connection.owner != self.owner:
        self.connections.clear()
        dprint("clearing connections")
        break

    # build a list of lines between all connections
    connections = []
    potentials = []
    for planet in nearbyplanets:
      ploc = Point(planet.x,planet.y)
      connections += [(ploc,Point(p.x,p.y)) for p in planet.connections.all()]
      potentials.append((ploc,Point(self.x,self.y)))

    # remove connections that are to close to other planets
    freeplanets = [x for x in nearbyplanets[1:] if not tooclose(nearbyplanets,(Point(self.x,self.y),Point(x.x,x.y)))]
    dprint("nearbyplanets --> %d" % len(nearbyplanets))
    dprint("after too close --> %d" % len(freeplanets))
    
    # remove connections that intersect other
    # connections
    if len(connections):
      freeplanets = [x for x in freeplanets[1:] if not intersects((x,self),connections)]
      dprint("after intersection --> %d" % len(freeplanets))


    # remove planets owned by other players
    freeplanets = [x for x in freeplanets if x.owner == None or x.owner == self.owner]
    dprint("after ownership --> %d" % len(freeplanets))

    # remove planets that are already connected to other players planets
    freeplanets = [x for x in freeplanets if not x.connections.count() or x.owner == self.owner]
    
    numconnections = max(minconnections,int(math.floor(random.normalvariate(2.0,1.5))))

    choices = cubicrandomchoice(len(freeplanets),numconnections)
    for choice in choices:
      self.buildconnection(freeplanets[choice])
    self.save()
    return len(choices)
 


  def colonize(self, fleet,report):
    if self.owner != None and self.owner != fleet.owner:
      # colonization doesn't happen if the planet is already colonized
      # (someone beat you to it, sorry...)
      report.append("Cancelled Colony: Fleet #" + str(fleet.id) + 
                    " returning home from" + self.name + 
                    " ("+str(self.id)+") -- Planet already owned.")
      fleet.gotoplanet(fleet.homeport)
    else:
      if self.owner == None:
        report.append(  "New Colony: Fleet #" + str(fleet.id) + 
                      " started colony at " + str(self.name) + 
                      " ("+str(self.id)+")")
        self.owner = fleet.owner
        numconnections = self.makeconnections()
        if numconnections > 0:
          report.append("            %d connections found" % numconnections)
      else:
        report.append("Bolstered Colony: Fleet #" + str(fleet.id) + 
                      " bolstered colony at " + self.name + 
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
      self.calculatesenserange()
      self.resources.save()
      self.save()
  
  
  
  def canbuildships(self):
    types = self.buildableships()
    if len(types['types']) > 0:
      return True
    else:
      return False
 

  
  def buildableships(self):
    """
    returns a list of ships that can be built at this planet
    >>> u = User()
    >>> s = Sector(key="100100")
    >>> p = Planet(sector=s, owner=u,x=500,y=500,r=.1,color=0xff0000)
    >>> p.populate()
    >>> pprint(p.buildableships()['types']['scouts'])
    {'antimatter': 25,
     'food': 5,
     'krellmetal': 0,
     'people': 5,
     'quatloos': 250,
     'steel': 250,
     'unobtanium': 0}

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
    {'antimatter': 250,
     'food': 50,
     'krellmetal': 16,
     'people': 50,
     'quatloos': 12500,
     'steel': 625,
     'unobtanium': 0}

    """
    buildable = {}
    buildable['types'] = {}
    buildable['commodities'] = {}
    buildable['available'] = []
    buildable['hasconnections'] = False
    
    available = self.availablecommodities()
    hasmilitarybase = self.hasupgrade(Instrumentality.MILITARYBASE)
    # this is a big imperative mess, but it's somewhat readable
    # (woohoo!)

    # see if we have extra commodities through connections...
    for type in available:
      if available[type] != getattr(self.resources,type):
        buildable['hasconnections'] = True
        break

    for type in shiptypes:
      isbuildable = True
      # turn off fighters and carriers for now, too confusing...
      if type == 'fighters':
        isbuildable = False
      if type == 'carriers':
        isbuildable = False
      for needed in shiptypes[type]['required']:
        if shiptypes[type]['required'][needed] > available[needed]:
          isbuildable = False
          break 
      if hasmilitarybase == False and shiptypes[type]['requiresbase'] == True:
        isbuildable = False
      if isbuildable:
        for needed in shiptypes[type]['required']:
          if shiptypes[type]['required'][needed] != 0 and needed not in  buildable['commodities']:
            buildable['commodities'][needed] = available[needed]
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
    >>> p.senserange()
    1.0
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
    self.calculatesenserange()
    self.save()

    self.makeconnections(2)

    if not self.hasupgrade(Instrumentality.MATTERSYNTH1):
      self.startupgrade(Instrumentality.MATTERSYNTH1)
      self.setupgradestate(Instrumentality.MATTERSYNTH1)

    if not self.hasupgrade(Instrumentality.MATTERSYNTH2):
      self.startupgrade(Instrumentality.MATTERSYNTH2)
      self.setupgradestate(Instrumentality.MATTERSYNTH2)
    
    if not self.hasupgrade(Instrumentality.MILITARYBASE):
      self.startupgrade(Instrumentality.MILITARYBASE)
      self.setupgradestate(Instrumentality.MILITARYBASE)



  def calculatesenserange(self):
    """
    >>> u = User(username="planetcalculatesenserange")
    >>> u.save()
    >>> r = Manifest()
    >>> r.save()
    >>> s = Sector(key=123126,x=101,y=101)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=615, y=625, r=.1, color=0x1234)
    >>> p.save()
    >>> p.calculatesenserange()
    0.51
    >>> p.senserange()
    0.51
    >>> p.startupgrade(Instrumentality.LRSENSORS1)
    1
    >>> p.setupgradestate(Instrumentality.LRSENSORS1)
    >>> p.calculatesenserange()
    1.01
    >>> p.startupgrade(Instrumentality.LRSENSORS2)
    1
    >>> p.setupgradestate(Instrumentality.LRSENSORS2)
    >>> p.calculatesenserange()
    1.51
    >>> p.society = 22
    >>> p.calculatesenserange()
    1.72
    """
    if not self.owner:
      return 0 
    range = .5 
    if self.hasupgrade(Instrumentality.LRSENSORS1):
      range += .5
    if self.hasupgrade(Instrumentality.LRSENSORS2):
      range += .5
    range += min(self.society*.01, 1.0)
    self.sensorrange = range
    return range

  def senserange(self):
    return self.sensorrange

  def availablefortrade(self, resource):
    avail = getattr(self.resources, resource)
    return avail

  def computeprices(self):
    domestic = ""
    foreign = ""
    changed = 0
    if self.prices == None:
      domestic = Manifest()
    else:
      domestic = self.prices
    if self.foreignprices == None:
      foreign = Manifest()
    else:
      foreign = self.foreignprices
    
    if self.resources != None:
      resourcelist = self.resources.manifestlist(['id','quatloos'])
      for resource in resourcelist:
        oldval = getattr(foreign,resource)
        newval = self.computeprice(resource,True)
        if oldval != newval:
          setattr(foreign, resource, newval)
          changed=1

        oldval = getattr(domestic,resource)
        newval = self.computeprice(resource,False)
        if oldval != newval:
          setattr(domestic, resource, newval)
          changed=1
    
    if changed==1:
      foreign.save()
      domestic.save()
      
    if not self.foreignprices or self.prices:
      self.foreignprices = foreign
      self.prices = domestic
      self.save()
    return changed

  def getprices(self, foreign):
    if not self.resources:
      return {}
    resourcelist = self.resources.manifestlist(['id','quatloos'])
    pricelist = {}
    if not self.prices or not self.foreignprices:
      self.computeprices()

    for resource in resourcelist:
      if foreign:
        pricelist[resource] = getattr(self.foreignprices,resource)
      else:
        pricelist[resource] = getattr(self.prices,resource)
    return pricelist

    

  def getprice(self, commodity, foreign):
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
    >>> p.computeprices()
    1
    >>> p.getprice('food',True)
    5
    >>> p.resources.food = 1000
    >>> p.resources.people = 5000
    >>> p.computeprices()
    1
    >>> p.getprice('food',True)
    3 
    >>> p.getprice('food',False)
    7 
    >>> p.resources.food = 0
    >>> p.computeprices()
    1
    >>> p.getprice('food',False)
    10
    >>> p.resources.food = 100000
    >>> p.computeprices()
    1
    >>> p.getprice('food',False)
    3
    >>> p.society=30
    >>> p.startupgrade(Instrumentality.TRADEINCENTIVES)
    1
    >>> p.setupgradestate(Instrumentality.TRADEINCENTIVES)
    >>> p.society=1
    >>> p.computeprices()
    1
    >>> p.getprice('food',False)
    2 
    >>> p.getprice('food',True)
    1
    >>> p.resources.food = 0
    >>> p.computeprices()
    1
    >>> p.getprice('food',True)
    6
    >>> p.getprice('food',False)
    12

    >>> p.society=200
    >>> p.nextproduction('food', p.resources.people)
    -629
    >>> p.computeprices()
    1    
    >>> p.getprice('food',False)
    19
    >>> p.resources.food = 10000
    >>> p.computeprices()
    1 
    >>> p.getprice('food',False)
    5 
    >>> p.resources.food = 1000000
    >>> p.computeprices()
    1 
    >>> p.getprice('food',False)
    2 
    
    #try to find Petriborg's problem...
    >>> p.resources.people = 16766100
    >>> p.resources.food = 844711392
    >>> p.resources.steel = 2006130
    >>> p.resources.quatloos = 56040629
    >>> p.resources.unobtanium = 0
    >>> p.resources.antimatter = 100000
    >>> p.resources.consumergoods = 56798
    >>> p.resources.hydrocarbon = 0
    >>> p.resources.krellmetal = 21
    >>> p.inctaxrate = 0.0
    >>> p.tariffrate = 0.0
    >>> p.society = 114
    >>> p.startupgrade(Instrumentality.FARMSUBSIDIES)
    1
    >>> p.setupgradestate(Instrumentality.FARMSUBSIDIES)
    >>> p.startupgrade(Instrumentality.DRILLINGSUBSIDIES)
    1
    >>> p.setupgradestate(Instrumentality.DRILLINGSUBSIDIES)
    >>> p.setupgradestate(Instrumentality.TRADEINCENTIVES,PlanetUpgrade.INACTIVE)
    >>> p.save()
    >>> p.nextproduction('food',p.resources.people)
    0 
    >>> p.computeprices()
    1 
    >>> p.getprice('food',False)
    3
    """
    if self.prices == None or self.foreignprices == None:
      self.computeprices()
    
    if foreign:
      return getattr(self.foreignprices,commodity)
    else:
      return getattr(self.prices,commodity)

    

  def computeprice(self, commodity, includetariff):
    people = self.resources.people
    nextprod = self.nextproduction(commodity, people)
    onhand = getattr(self.resources,commodity)
    baseprice = productionrates[commodity]['baseprice']
    maxdrop = baseprice/1.5
    productionrate = self.productionrate(commodity)
    pricemod = productionrates[commodity]['pricemod']
    price = baseprice - ((nextprod * pricemod)/baseprice)
    if price <= 0:
      price = 1 




    # if there's a surplus sitting around, that affects the price.  the
    # more surplus the lower the price
    if onhand > 0:
      surplusfactor=0
      if people != 0:
        surplusfactor = float(onhand)/float(people)*5.0
        #print surplusfactor
        if surplusfactor < 4.0:
          price -= maxdrop * (math.log(1+surplusfactor,5))
        else:
          price -= maxdrop
    if price <= 0:
      price = 1 


    # this section models the effect of production on price -- if
    # there is more being produced than consumed, the price goes down
    # and vise versa...
    prodfactor = 0
    onhand2 = onhand
    if onhand2 <= 0:
      onhand2 = 1
    sign = 1
    if nextprod > 0:
      sign = -1

    if nextprod > 0:
      prodfactor = abs((float(nextprod)/(float(onhand2)))*1000.0)
      if prodfactor > 2:
        #print "+" + str(prodfactor)
        prodfactor = 2.0
      price += sign * ((maxdrop/2)-(maxdrop/2) * (math.log(1+prodfactor,3)))
    else:
      prodfactor = abs((float(nextprod)/(float(onhand2)))*10.0)
      if prodfactor > 2:
        #print "-" + str(prodfactor)
        prodfactor = 2.0
      price += sign * ((maxdrop) * (math.log(1+prodfactor,3)))







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
    numtobuy = max(0,min(amount, int(self.resources.quatloos/curprice)))
    commodityonhand = getattr(self.resources,commodity)
    if commodityonhand < 0:
      commodityonhand = 0
    setattr(self.resources,
            commodity,
            commodityonhand+numtobuy)
    self.resources.quatloos -= curprice*numtobuy

    if self.resources.quatloos < 0:
      self.resources.quatloos = 0
    if self.resources.food < 0:
      self.resources.food = 0

    #self.resources.save()
    return numtobuy



  def availablecommodities(self):
    """
    >>> u = User(username="availablecommodities")
    >>> u.save()
    >>> r = Manifest(quatloos=100, food=15)
    >>> r.save()
    >>> s = Sector(key=123126,x=101.5,y=101.5)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s,
    ...            x=615, y=625, r=.1, color=0x1234)
    >>> p.save()
    >>> pprint(p.availablecommodities())
    {'antimatter': 0,
     'consumergoods': 0,
     'food': 15,
     'hydrocarbon': 0,
     'krellmetal': 0,
     'people': 0,
     'quatloos': 100,
     'steel': 0,
     'unobtanium': 0}
    >>> r2 = Manifest(quatloos=100, food=20)
    >>> r2.save()
    >>> p2 = Planet(resources=r2, society=1,owner=u, 
    ...             sector=s, name="availablecommodities2",
    ...             x=615, y=625, r=.1, color=0x1234)
    >>> p2.save()
    >>> #p2.connections.add(p)
    >>> p.buildconnection(p2)
    1
    >>> p.buildconnection(p2)
    0
    >>> p2.buildconnection(p)
    0
    >>> pprint(p.availablecommodities())
    {'antimatter': 0,
     'consumergoods': 0,
     'food': 35,
     'hydrocarbon': 0,
     'krellmetal': 0,
     'people': 0,
     'quatloos': 200,
     'steel': 0,
     'unobtanium': 0}
    >>> pprint(p2.availablecommodities())
    {'antimatter': 0,
     'consumergoods': 0,
     'food': 35,
     'hydrocarbon': 0,
     'krellmetal': 0,
     'people': 0,
     'quatloos': 200,
     'steel': 0,
     'unobtanium': 0}
    >>> p.gathercommodities({'food':1})
    (True, '')
    >>> pprint(p2.availablecommodities())
    {'antimatter': 0,
     'consumergoods': 0,
     'food': 34,
     'hydrocarbon': 0,
     'krellmetal': 0,
     'people': 0,
     'quatloos': 200,
     'steel': 0,
     'unobtanium': 0}
    >>> p.gathercommodities({'food':1000})
    (False, 'food')
    >>> p.gathercommodities({'food':30})
    (True, '')
    >>> pprint(p.availablecommodities())
    {'antimatter': 0,
     'consumergoods': 0,
     'food': 4,
     'hydrocarbon': 0,
     'krellmetal': 0,
     'people': 0,
     'quatloos': 200,
     'steel': 0,
     'unobtanium': 0}
    >>> p2 = Planet.objects.get(name="availablecommodities2")
    >>> p2.gathercommodities({'food':1})
    (True, '')
    >>> pprint(p2.availablecommodities())
    {'antimatter': 0,
     'consumergoods': 0,
     'food': 3,
     'hydrocarbon': 0,
     'krellmetal': 0,
     'people': 0,
     'quatloos': 200,
     'steel': 0,
     'unobtanium': 0}
    >>> r3 = Manifest(quatloos=100, food=50, steel=20)
    >>> r3.save()
    >>> p3 = Planet(resources=r3, society=1,owner=u, 
    ...             sector=s, name="availablecommodities3",
    ...             x=615, y=625, r=.1, color=0x1234)
    >>> p3.save()
    >>> p3.buildconnection(p)
    1
    >>> p4 = Planet(society=1, 
    ...             sector=s, name="availablecommodities4",
    ...             x=615, y=625, r=.1, color=0x1234)
    >>> p4.save()
    >>> p4.buildconnection(p)
    1
    >>> p2.resources.food  = 30
    >>> p2.resources.steel = 30
    >>> p2.resources.save()
    >>> p.resources.food = 1
    >>> p.gathercommodities({'food':10,'steel':10})
    (True, '')
    >>> p2 = Planet.objects.get(name="availablecommodities2")
    >>> pprint(p2.availablecommodities())
    {'antimatter': 0,
     'consumergoods': 0,
     'food': 27,
     'hydrocarbon': 0,
     'krellmetal': 0,
     'people': 0,
     'quatloos': 200,
     'steel': 24,
     'unobtanium': 0}
    >>> p3 = Planet.objects.get(name="availablecommodities3")
    >>> pprint(p3.availablecommodities())
    {'antimatter': 0,
     'consumergoods': 0,
     'food': 44,
     'hydrocarbon': 0,
     'krellmetal': 0,
     'people': 0,
     'quatloos': 200,
     'steel': 16,
     'unobtanium': 0}
    >>> p.gathercommodities({'food':3})
    (True, '')
    """
    available = {}
    connections = self.connections.all()
    for resource in productionrates.keys():
      available[resource] = getattr(self.resources,resource)
      if resource != 'people':
        for connection in connections:
          if(connection.resources):
            available[resource] += getattr(connection.resources,resource) 
    return available



  def gathercommodities(self,commodities):
    local = {}
    tryremote = {}
    transferred = {}
    for commodity in commodities:
      transferred[commodity] = 0
      needed = commodities[commodity]
      onhand = getattr(self.resources,commodity)
      if onhand < needed:
        tryremote[commodity] = needed-onhand
        local[commodity] = onhand
      else:
        local[commodity] = needed
    
    if len(tryremote) > 0:
      available = {}
      connections = self.connections.all()
      for commodity in tryremote:
        available[commodity] = 0
        for connection in connections:
          if connection.resources:
            available[commodity] += getattr(connection.resources,commodity) 

      # check to make sure it's possible to do what we want...
      for key in available:
        if available[key] < tryremote[key]:
          return False, key
      for connection in connections:
        if connection.resources:
          for commodity in tryremote:
            totalneeded = tryremote[commodity]
            onhand = getattr(connection.resources,commodity)
            totalavailable = available[commodity]
            percentresponsible = float(onhand)/float(totalavailable)
            amount = max(0, int(round(totalneeded*percentresponsible)))
            transferred[commodity] += amount
            setattr(connection.resources, commodity, onhand - amount)
          connection.resources.save()
        
    for commodity in local:
      onhand = getattr(self.resources,commodity)
      amount = max(0,onhand-local[commodity])
      transferred[commodity] += local[commodity] 
      setattr(self.resources, commodity, amount)

    for commodity in commodities:
      counter = 0
      while counter < 20 and transferred[commodity] < commodities[commodity]:
        # shitballs...
        # this means we had a rounding error...
        for connection in connections:
          if transferred[commodity] >= commodities[commodity]:
            break
          onhand = getattr(connection.resources,commodity)
          if onhand > 0:
            setattr(connection.resources, commodity, onhand-1)
            transferred[commodity]+=1
            connection.resources.save()
        counter += 1
    for commodity in commodities:
      if transferred[commodity] != commodities[commodity]:
        print "? %s -- transferred = %d wanted = %d" % (commodity,
                                                        transferred[commodity], 
                                                        commodities[commodity])
    self.resources.save()
    return True, ''
      



  def tradescore(self, fleet, dontbuy, curplanet):
    """
    computes a score for a fleet coming *from* curplanet *to* this (self)
    planet.
    >>> u = User(username="tradescore1")
    >>> u.save()
    >>> r = Manifest(people=8000000, food=100000, 
    ...              steel=50000, consumergoods=1000)
    >>> r.save()
    >>> s = Sector(key=130170,x=650.0,y=850.0)
    >>> s.save()
    >>> p = Planet(resources=r, society=50,owner=u, sector=s, name="1",
    ...            x=652.5, y=852.5, r=.1, color=0x1234)
    >>> p.save()
    >>> pl = Player(user=u, capital=p, color=112233)
    >>> pl.lastactivity = datetime.datetime.now()
    >>> pl.save()
    >>> report=[]
    >>> r = Manifest(people=5000, food=1000, quatloos=1000, steel=5)
    >>> r.save()
    >>> p2 = Planet(resources=r, sector=s, x=651, y=851, r=.1, name="2",
    ...             inctaxrate=5.0, owner=u, color=0x1234, society=10)
    >>> p2.save()
    >>> p.society=30
    >>> r2 = Manifest(quatloos=10000)
    >>> r2.save()
    >>> f1 = Fleet(trade_manifest=r2, homeport=p, owner=u, sector=s, 
    ...            x=652.4, y=852.4, merchantmen=1)
    >>> f1.save()
    >>> p2.tradescore(f1, ['people','food'], p)
    (262.4373346723855, [('consumergoods', 344)])
    >>> f2 = Fleet(destination=p2, trade_manifest=r2, homeport=p, 
    ...            owner=u, sector=s, merchantmen=1, disposition=8)
    >>> f2.save()
    >>> p2.tradescore(f1, ['people','food'], p)
    (183.43582495389052, [('consumergoods', 344)])
    >>> p2.x = 700
    >>> p2.tradescore(f1, ['people','food'], p)
    (37.651368936382966, [('consumergoods', 344)])
    """
    distance = getdistanceobj(self,fleet)
    competition = 0
    nextforeign = True
    if self.owner == fleet.owner:
      nextforeign = False
    
    commodity, differential = findbestdeal(curplanet,
                                           self,
                                           fleet, 
                                           dontbuy)
    connections = self.getconnections()
    competition = self.numcompetition()

    # prefer closer planets to ones farther away, except foreign planets
    if not nextforeign:
      differential = differential * (1.0 - math.log(1.0+distance, 100))
    else:
      differential = differential * (1.0 - math.log(1.0+distance, 20))
   
    #attempt to get ships to go between more than the 2 most
    #convenient planets...
    if competition:
      if competition > 8:
        competition = 8
      differential = differential - (differential*math.log(1+competition,10))

    if curplanet.id in connections:
      if differential > 0:
        differential = differential/4.0

    # bump up if famine occuring
    if self.resources.food <= 0 and \
       'food' not in dontbuy and \
       curplanet.resources.food > 0 and \
       competition < 6:
      differential *= 1.3
    return(differential,commodity)
        

  def json(self,playersplanet=0): 
    #flags 
    #food subsidy:          1
    #famine:                2
    #RGLGOVT:               4 
    #MATTERSYNTH1:          8 
    #MILITARYBASE:          16
    #MATTERSYNTH2:          32
    #open trade:            64
    #player owned           128
    #PLANETARYDEFENSE:      256
    #FARMSUBSIDIES:         512
    #DRILLINGSUBSIDIES:     1024
    #damaged:               2048
    json = {}
    if self.owner_id:
      json['o'] = self.owner_id
      json['s'] = self.senserange()
    else:
      json['h'] = 0
    if self.resources:
      json['p'] = self.resources.people
    else:
      json['p'] = 0
    json['f'] = 0
    json['x'] = self.x
    json['y'] = self.y
    json['c'] = "#" + hex(self.color)[2:]
    json['r'] = self.r
    json['i'] = self.id
    json['n'] = escape(self.name)
    if self.opentrade:
      json['f'] += 64
    if playersplanet == 1:
      json['f'] += 128
    if self.damaged:
      json['f'] += 2048
    return json



  def productionrate(self,resource):
    advantageattrib = None
    advantageattrib = self.getattribute(resource+'-advantage')
    advantage = 1.0
    if advantageattrib:
      advantage = float(advantageattrib)
    return ((productionrates[resource]['baserate']+
            (productionrates[resource]['socmodifier']*self.society))*advantage)



  def nextproduction(self, resource, population):
    """
    >>> u = User(username="nextproduction")
    >>> u.save()
    >>> r = Manifest(people=5000, food=1000)
    >>> r.save()
    >>> s = Sector(key=123124,x=101,y=101)
    >>> s.save()
    >>> p = Planet(resources=r, society=50,owner=u, sector=s,
    ...            x=100, y=100, r=.1, color=0x1234)
    >>> p.save()
    >>> pl = Player(user=u,color=0,capital=p)
    >>> pl.lastactivity = datetime.datetime.now()
    >>> pl.save()
    >>> p.nextproduction('food',5000)
    180
    >>> p.nextproduction('hydrocarbon',5000)
    30 
    >>> p.startupgrade(Instrumentality.FARMSUBSIDIES)
    1
    >>> p.setupgradestate(Instrumentality.FARMSUBSIDIES)
    >>> p.nextproduction('food',5000)
    1269
    >>> p.nextproduction('hydrocarbon',5000)
    6
    >>> p.startupgrade(Instrumentality.DRILLINGSUBSIDIES)
    1
    >>> p.setupgradestate(Instrumentality.DRILLINGSUBSIDIES)
    >>> p.nextproduction('food',5000)
    604
    >>> p.nextproduction('hydrocarbon',5000)
    72

    >>> # try to find Petriborg's problem...
    >>> p.resources.people = 16766100
    >>> p.resources.food = 844711392
    >>> p.resources.steel = 2006130
    >>> p.resources.quatloos = 56040629
    >>> p.resources.unobtanium = 0
    >>> p.resources.antimatter = 100000
    >>> p.resources.consumergoods = 56798
    >>> p.resources.hydrocarbon = 0
    >>> p.resources.krellmetal = 21
    >>> p.inctaxrate = 0.0
    >>> p.society = 114
    >>> p.save()
    >>> p.nextproduction('food',p.resources.people)
    0
    """
    
    if (productionrates[resource]['neededupgrade'] != -1 and 
       not self.hasupgrade(productionrates[resource]['neededupgrade'])):
      return 0
    
    oldval = getattr(self.resources,resource)
    produced = self.productionrate(resource) * population
    maxsurplus = productionrates[resource]['maxsurplus']



    farmsub = False
    drillsub = False
    ms1 = False
    ms2 = False
    
    if self.hasupgrade(Instrumentality.FARMSUBSIDIES):
      farmsub = True

    if self.hasupgrade(Instrumentality.DRILLINGSUBSIDIES):
      drillsub = True
  
   
    fullrate = ['people','quatloos']
    if farmsub:
      fullrate.append('food')
    if drillsub:
      fullrate.append('hydrocarbon')

    subsidyfactor = .8
    if farmsub and drillsub:
      subsidyfactor = .4
    

    if (farmsub or drillsub) and resource not in fullrate:
      if produced > population:
        produced = (produced - population)*.2 + population
    elif (farmsub and resource == 'food') or (drillsub and resource == 'hydrocarbon'):
      # handle farm/drilling subsidies
      subsidy = 0
      for resourcetype in productionrates:
        if resourcetype in fullrate:
          continue
        curprice = productionrates[resourcetype]['baseprice']
        consumed = ((self.productionrate(resourcetype) * population)-population)*subsidyfactor
        subsidy += floor(curprice * consumed)
      produced += subsidy/productionrates[resource]['baseprice']
    
    surplus = produced-population
   
    # exponentially decrease new surplus to zero as amount onhand approaches maxsurplus
    if oldval > maxsurplus/2.0 and oldval < maxsurplus:
      surplus -= surplus * (1.0 - ((1.0 - math.log(oldval-(maxsurplus/2.0),(maxsurplus/2.0)))))
    elif oldval > maxsurplus:
      surplus = 0
    
    # reduce amount produced by inctaxrate/2 
    if resource not in ['people','quatloos'] and surplus >= 0:
      taxrate = self.inctaxrate/100.0
      if taxrate < 0:
        taxrate = 0.0
      surplus = (surplus - math.floor(surplus*((self.inctaxrate/100.0)/2.0)))
     
    return int(surplus)




  def nexttaxation(self):
    rate = self.inctaxrate
    if self.inctaxrate < 0:
      rate = 0.0
    return int((self.resources.people * (rate/100.0))/6.0)



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
        if res['nextproduction'] < 0:
          res['nextproduction'] = 0
        res['negative'] = 0
        report.append(res)
    return report   



  def doproductionforresource(self, curpopulation, resource):
    # DAVE!  this function returns the total amount of this
    # resource on the planet for this turn, not the amount
    # produced this turn!
    oldval = getattr(self.resources, resource)
    surplus = self.nextproduction(resource,curpopulation)
    return oldval+surplus



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
    >>> p.startupgrade(Instrumentality.MATTERSYNTH1)
    1
    >>> p.setupgradestate(Instrumentality.MATTERSYNTH1)
    >>> p.hasupgrade(Instrumentality.MATTERSYNTH1)
    1
    >>> p.resources.food
    1444
    >>> p.doproduction('hi',[])
    >>> r.krellmetal
    7
    >>> p.startupgrade(Instrumentality.MATTERSYNTH2)
    1
    >>> p.setupgradestate(Instrumentality.MATTERSYNTH2)
    >>> p.doproduction('hi',[])
    >>> r.unobtanium
    2
    >>> p.setupgradestate(Instrumentality.MATTERSYNTH2,
    ...                   PlanetUpgrade.INACTIVE)
    >>> p.doproduction('hi',[])
    >>> r.unobtanium
    2

    """
    curpopulation = self.resources.people
   

    for resource in productionrates.keys():
      
      if resource == 'quatloos':
        continue

      newval = self.doproductionforresource(curpopulation,resource)
      
      if resource == 'food' and newval < 0:
        # attempt to buy enough food to cover the
        # discrepency...
        foodprice = self.getprice('food',False)
        quatloos = self.resources.quatloos
        # only have to buy 10% of discrepency to subsidize
        numtobuy = (abs(newval)/10)+min(curpopulation/1000,200)
         
        # artificially set the food value so that it ends up as
        self.resources.food = newval/10

        # make the purchase
        numbought = self.sellfrommarkettogovt('food', numtobuy)
        if numbought > 0: 
          # we are still able to subsidize food production
          report.append(replinestart + "Govt. Subsidizing Food Prices")
          self.setattribute('food-scarcity','subsidized')
        # check to see if there's no food available on the planet
        elif numbought == 0:
          # uhoh, famine...
          report.append(replinestart + "Reports Famine!")
          self.resources.population = int(curpopulation * .95)
          self.setattribute('food-scarcity','famine')
      else:
        setattr(self.resources, resource, max(0,newval))

    self.resources.quatloos += self.nexttaxation()
    



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
    'hi'
    >>> p.setattribute("hello","hi2")
    >>> p.getattribute("hello")
    'hi2'
    >>> p.setattribute("hello", None)
    >>> p.getattribute("hello")
    >>> p.getattribute("ljsasajfsfdsdf")
    """
    attribfilter = PlanetAttribute.objects.filter(planet=self,attribute=curattribute)
    if curvalue == None:
      attribfilter.delete()
      if self.curattributes.has_key(curattribute):
        del self.curattributes[curattribute]
      return None
    if attribfilter.count():
      attribfilter.delete()
    pa = PlanetAttribute(planet=self,attribute=curattribute, value=curvalue)
    pa.save()
    self.curattributes[curattribute]=curvalue
  

  def getattributes(self):
    if localcache and localcache.has_key('attributes'):
      if localcache['attributes'].has_key(self.id):
        return localcache['attributes'][self.id]
      else:
        return []
    else:
      self.loadattributes()
      return self.curattributes 


  def getattribute(self,curattribute):
    if localcache and localcache.has_key('attributes'):
      if localcache['attributes'].has_key(self.id) and \
         localcache['attributes'][self.id].has_key(curattribute):
        return localcache['attributes'][self.id][curattribute]
      else:
        return None
    else:
      self.loadattributes()
      if curattribute in self.curattributes:
        return self.curattributes[curattribute]
      else:
        return None

  def loadattributes(self): 
    if len(self.curattributes) == 0:
      a = PlanetAttribute.objects.filter(planet=self)
      for i in a:
        self.curattributes[i.attribute] = i.value
      self.curattributes[-1] = 1
  
  def getconnections(self):
    connections = []
    if localcache and localcache.has_key('connections'):
      if localcache['connections'].has_key(self.id):
        connections = localcache['connections'][self.id]
    else:
      connections = self.connections.all().values_list('id')
    return connections

  def numcompetition(self):
    competition = 0
    if localcache and localcache.has_key('competition'):
      if localcache['competition'].has_key(self.id):
        competition = localcache['competition'][self.id]
    else:
      competition = Fleet.objects\
                         .filter(Q(destination=self)|
                                 Q(source=self), disposition=8).count()
    return competition

  def bumpcompetition(self):
    if localcache and localcache.has_key('competition'):
      if not localcache['competition'].has_key(self.id):
        localcache['competition'][self.id] = 1
      else:
        localcache['competition'][self.id] += 1
    





  def doturn(self, report):
    """
    >>> u = User(username="planetdoturn")
    >>> u.save()
    >>> r = Manifest(people=5000, food=1000)
    >>> r.save()
    >>> s = Sector(key=101101,x=101,y=101)
    >>> s.save()
    >>> p = Planet(resources=r, society=1,owner=u, sector=s, name="doturn1",
    ...            x=505.5, y=506.5, r=.1, color=0x1234)
    >>> p.save()
    >>> pl = Player(user=u, capital=p, color=112233)
    >>> pl.lastactivity = datetime.datetime.now()
    >>> pl.save()
    >>> report=[]
    >>> p.doturn(report)
    >>> p.resources.food
    1444
    >>> p.society=50
    >>> r = Manifest(people=5000, food=1000, quatloos=1000)
    >>> r.save()
    >>> p2 = Planet(resources=r, sector=s, x=505.2, y=506.0, r=.1, name="doturn2",
    ...             inctaxrate=5.0, owner=u, color=0x1234, society=1)
    >>> p2.save()
    >>> p.society=30
    >>> p.startupgrade(Instrumentality.RGLGOVT)
    1
    >>> p.setupgradestate(Instrumentality.RGLGOVT)
    >>> p.society=1
    >>> report = []
    >>> p.resources.quatloos = 1000
    >>> p.resources.save()
    >>> p.nextregionaltaxation(True,report)
    20
    >>> p.doturn(report)
    >>> p = Planet.objects.get(name="doturn1")
    >>> p2 = Planet.objects.get(name="doturn2")
    >>> print report
    ['Regional Taxation -- Planet: doturn1 (21)  Collected -- 20']
    >>> p.resources.quatloos
    1020
    >>> p2 = Planet.objects.get(name="doturn2")
    >>> p2.resources.quatloos
    980
    >>> f1 = Fleet(homeport=p,owner=u,sector=s,scouts=1)
    >>> f1.save()
    >>> p.doturn(report)
    >>> p.nextregionaltaxation(True,report)
    20
    >>> p.resources.quatloos
    1020 
    """
    replinestart = "Planet: " + self.name + " (" + str(self.id) + ") "
   

    # only owned planets produce
    if self.owner != None and self.resources != None:
      # produce surplus resources
      self.doproduction(replinestart,report)
 

      # handle fleet upkeep costs 
      upkeep = self.fleetupkeepcosts()
      [self.resources.consume(line,upkeep[line]) for line in upkeep]
      
      self.resources.save()



  def nextregionaltaxation(self,debit=True, report=[]):
    totaltax = 0
    if self.hasupgrade(Instrumentality.RGLGOVT):
      planets = closethings(Planet.objects\
                                  .filter(owner=self.owner),
                            self.x, self.y, 5.0)
      for i in planets.select_related('resources').iterator():
        if i.owner_id != self.owner_id:
          print "not same owner!"
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
        replinestart = "Regional Taxation -- Planet: " + self.name + " (" + str(self.id) + ") "
        report.append(replinestart + 
                      " Collected -- %d" % (totaltax))
        self.resources.quatloos += totaltax
        self.resources.save()

    return totaltax


#        class: Announcement
#  description: game announcements (not currently used 10/29/2010)
#         note:

class Announcement(models.Model):
  def __unicode__(self):
      return self.subject
  time = models.DateTimeField(auto_now_add=True)
  subject = models.CharField(max_length=50)
  message = models.TextField()

#        class: Event
#  description: game events (things like Player A is at War with
#               Player B, etc...)  (not currently sued 10/29/2010)
#         note:

class Event(models.Model):
  def __unicode__(self):
      return self.event[:20]
  time = models.DateTimeField(auto_now_add=True)
  event = models.TextField()


def atwarsimple(id1, id2):
  # determine if 2 things are at war with each other
  if localcache:
    if localcache.has_key('atwar'):
      if localcache['atwar'].has_key(id1) and \
         localcache['atwar'][id1].has_key(id2):
        return True
      else:
        return False
  


def atwar(thing1, thing2):
  # determine if 2 things are at war with each other
  if localcache:
    if localcache.has_key('atwar'):
      if localcache['atwar'].has_key(thing1.owner_id) and \
         localcache['atwar'][thing1.owner_id].has_key(thing2.owner_id):
        return True
      else:
        return False 
  elif thing1.owner\
              .get_profile()\
              .getpoliticalrelation(thing2.owner.get_profile()) == "enemy":
    return True 
  return False 

def allconnections():
  def addcon(pcons,planeta,planetb):
    if not pcons.has_key(planeta):
      pcons[planeta] = {}
    pcons[planeta][planetb] = 1

  connections = PlanetConnection.objects\
                                .values_list('planeta','planetb')
  planetconnections = {}
  for c in connections:
    addcon(planetconnections, c[0], c[1])
    addcon(planetconnections, c[1], c[0])
  
  return planetconnections

def allplayers():
  players = Player.objects\
                  .all()\
                  .values_list('user_id','lastactivity')
  pdict = {}
  for p in players:
    pdict[p[0]] = {'lastactivity':p[1]}
  return pdict

def allupgrades():
  upgrades = PlanetUpgrade.objects\
                          .filter(state=PlanetUpgrade.ACTIVE)\
                           .values_list('planet_id','instrumentality__type')
  planetupgrades = {}
  for u in upgrades:
    if not planetupgrades.has_key(u[0]):
      planetupgrades[u[0]] = {}
    planetupgrades[u[0]][u[1]] = 1
  return planetupgrades



def allattributes():
  attributes = PlanetAttribute.objects\
                              .all()\
                              .values_list('planet_id','attribute','value')
  planetattributes = {}
  for a in attributes:
    if not planetattributes.has_key(a[0]):
      planetattributes[a[0]] = {}
    planetattributes[a[0]][a[1]] = a[2]
  return planetattributes

def allcompetition():
  competition = {}
  counts = Planet.objects\
                 .filter(owner__isnull=False)\
                 .annotate(Count('source_port'),
                           Count('destination_port'))\
                 .values_list('id',
                              'source_port__count',
                              'destination_port__count')
  for c in counts:
    competition[c[0]] = sum(c[1:])

  return competition
    

def allplanetsbysector():
  planets = Planet.objects\
                  .exclude(owner=None)\
                  .values_list('sector_id','id','owner_id','x','y')
  bysector = {}

  for p in planets:
    if not bysector.has_key(p[0]):
      bysector[p[0]] = []
    bysector[p[0]].append(p[1:])
  
  return bysector


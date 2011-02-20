from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import models, connection, transaction
from django.core.mail import send_mail
from django.db.models import Q, Avg, Sum, Min, Max
from pprint import pprint
import datetime
import math
import operator
import random
import aliens
import time
from newdominion.dominion.util import *
from newdominion.dominion.constants import *
from util import dprint
from operator import itemgetter


#        class: PlanetUpgrade
#  description: represents an instance of a Planet Upgrade (sensor array, 
#               mind control, etc...)
#         note:

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
      

#        class: Player
#  description: DG specific player/user profile.
#         note:

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
  neighbors = models.ManyToManyField("self", symmetrical=True)

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



  def footprint(self):
    return list(Sector.objects.filter(Q(fleet__owner=self.user)|
                                      Q(planet__owner=self.user)).distinct().values_list('key',flat=True))
  
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
    ''
    >>> f = Fleet(scouts=1,blackbirds=1,arcs=1)
    >>> f.shiplistreport()
    '1 scout, 1 blackbird, 1 arc'
    """
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
      json['dst'] = 1
    elif self.damaged == True:
      json['dmg'] = 1
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



  def dotrade(self,report,prices):
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
    >>> f.dotrade(report,{})
    >>> pprint(report)
    ['  Trading at Planet X (1) out of money, restocking.',
     '  Trading at Planet X (1)  bought 25 steel with 2500 quatloos',
     '  Trading at Planet X (1)  new destination = Planet Y-2']
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
    
    dontbuy += self.selltoplanet(curplanet,report,replinestart)
    if prices.has_key(curplanet.id):
      del prices[curplanet.id]
    
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
      report.append(replinestart+" out of money, restocking.")

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
                                            nextforeign,prices)

    # too poor to be effective, go home for resupply... (piracy?)
    elif m.quatloos < 500 and self.destination != self.homeport:
      bestplanet = self.homeport
      bestcommodity = 'food'
      bestdif = 1
    else: 
      # first build a list of nearby planets, sorted by distance
      plist = nearbysortedthings(Planet.objects.filter(owner__isnull=False,
                                                       resources__isnull=False),
                                 self)[1:]
      for destplanet in plist:
        distance = getdistanceobj(self,destplanet)
        nextforeign = True
        if destplanet.owner == self.owner:
          nextforeign = False
        if destplanet == self.destination:
          print "shouldn't happen"
          continue
        if not destplanet.opentrade and  not destplanet.owner == self.owner:
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
                                                 nextforeign,prices)
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
      numbought,price = self.buyfromplanet(bestcommodity,curplanet)
      if prices.has_key(curplanet.id):
        del prices[curplanet.id]

      if bestcommodity == 'people':
        report.append(replinestart + "took on " + str(getattr(m,bestcommodity)) + " passengers.")
      else:
        report.append("%s bought %d %s with %d quatloos" % 
                      (replinestart, numbought, bestcommodity, price))
      report.append("%s new destination = %s (%d)" % (replinestart,bestplanet.name,bestplanet.id))
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
    (125, 1000)

    >>> p.owner=None
    >>> p.tariffrate=50.0
    >>> p.resources.food=1000
    >>> f.trade_manifest.quatloos=1000
    >>> f.trade_manifest.food=0
    >>> p.resources.people=5000
    >>> f.buyfromplanet('food',p)
    (125, 1000)

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
    (83, 996)
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
    return numtobuy, numtobuy*unitcost



  def selltoplanet(self,planet,report=None,replinestart=None):
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
        if report and replinestart:
          report.append(replinestart + 
                        " selling " + str(numtosell) + " " + str(item) +
                        " for " + str(profit) +' quatloos.')
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
    spent = {}
    for shiptype in ships:
      if not buildableships['types'].has_key(shiptype):
        print "cannot build type " + shiptype
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



  def doassault(self,destination,report,otherreport):
    replinestart = "  Assaulting Planet " + self.destination.name + " ("+str(self.destination.id)+")"
    oreplinestart = "  Planet Assaulted " + self.destination.name + " ("+str(self.destination.id)+")"
    nf = nearbythings(Fleet,self.x,self.y).filter(owner = destination.owner)
    for f in nf:
      if f == self:
        continue
      if f.owner == self.owner:
        continue
      if f.destroyed == True or f.damaged == True:
        continue
      if f.numcombatants() == 0:
        continue
      distance = getdistanceobj(f,self)
      if distance < self.senserange() or distance < f.senserange():
        report.append(replinestart + "unsuccessful assault -- planet currently defended")
        otherreport.append(oreplinestart + "unsuccessful assault -- planet is defended")
        # can't assault when there's a defender nearby...
        return
    # ok, we've made it through any defenders...
    if destination.resources:
      report.append(replinestart + "assault in progress -- raining death from space")
      otherreport.append(oreplinestart + "assault in progress -- they are raining death from space")
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
      otherreport.append(replinestart + "planetary assault -- capitulation!")
      #capitulation -- planet gets new owner...
      destination.owner = self.owner
      destination.makeconnections()
      destination.save()
       


  def doturn(self,report,otherreport,prices):
    """
    >>> u = User(username="fleetdoturn")
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
    >>> f = Fleet(trade_manifest=r, merchantmen=1, owner=u, sector=s)
    >>> f.homeport = p
    >>> f.source = p
    >>> f.x = p.x+.1
    >>> f.y = p.y+.1
    >>> f.save()
    >>> f.gotoplanet(p)
    >>> p.getattribute('lastvisitor')
    >>> report = []
    >>> f.move()
    >>> other = []
    >>> random.seed(1)
    >>> f.doturn(report,other,{})
    creating advantages
    >>> print str(report)
    ['Fleet: Fleet #3, 1 merchantman (3) Arrived at  (3)']
    >>> f.move()
    >>> f.doturn(report,other,{})
    >>> p.getattribute('lastvisitor')
    u'fleetdoturn'
    """
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
           not self.destination.getattribute('lastvisitor'):
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
        self.dotrade(report,prices)
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
          self.doassault(self.destination, report, otherreport)
        else:
          self.gotoplanet(self.homeport)
          

    else:
      self.move()
      
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
  connections = models.ManyToManyField("self")
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
        if distancetoline(planet, line[0], line[1]) < .5:
          return True
      return False

    nearbyplanets = nearbysortedthings(Planet,self)
    
    # if there are too many planets in the area, skip
    if len(nearbyplanets) > 80:
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
    #print "choices = " + str(choices)
    for choice in choices:
      self.connections.add(freeplanets[choice])
    self.save()
    return len(choices)
 


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
        report.append(  "New Colony: Fleet #" + str(fleet.id) + 
                      " started colony at " + str(self.name) + 
                      " ("+str(self.id)+")")
        numconnections = self.makeconnections()
        if numconnections > 0:
          report.append("            %d connections found" % numconnections)
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
     'quatloos': 1000,
     'steel': 50}
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
      # turn off fighters for now, too confusing...
      if type == 'fighters':
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

    self.makeconnections(2)

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



  def getprices(self, foreign):
    pricelist = {}
    if self.resources != None:
      resourcelist = self.resources.manifestlist(['id','quatloos'])
      for resource in resourcelist:
        pricelist[resource] = self.getprice(resource, foreign) 
    return pricelist 



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

    self.resources.save()
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
    >>> p2.connections.add(p)
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
    >>> p3.connections.add(p)
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
          available[commodity] += getattr(connection.resources,commodity) 

      # check to make sure it's possible to do what we want...
      for key in available:
        if available[key] < tryremote[key]:
          return False, key
      for connection in connections:
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
        print "shitballs"
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
      


  def getavailableprices(self, foreign):
    pricelist = {}
    if self.resources != None:
      resourcelist = self.resources.manifestlist(['id','quatloos'])
      for resource in resourcelist:
        pricelist[resource] = self.getprice(resource,foreign) 
    return pricelist



  def json(self,planetconnections,playersplanet=0):
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
      if self.hasupgrade(Instrumentality.RGLGOVT):
        json['rg'] = 1
      if self.hasupgrade(Instrumentality.MATTERSYNTH1):
        json['mil'] = 1
        if self.hasupgrade(Instrumentality.MILITARYBASE):
          json['mil'] += 2 
        if self.hasupgrade(Instrumentality.MATTERSYNTH2):
          json['mil'] += 4 
      if self.owner.get_profile().capital == self:
        json['cap'] = "1"
      json['s'] = self.senserange()
    else:
      json['h'] = 0
    
    for con in self.connections.all():
      if ((con.x,con.y),(self.x,self.y)) not in planetconnections:
        cx = con.x - ((con.x-self.x)/2.0)
        cy = con.y - ((con.y-self.y)/2.0)
        sector = buildsectorkey(cx,cy)
        planetconnections[((self.x,self.y),(con.x,con.y))] = sector 

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
    return int((self.resources.people * (self.inctaxrate/100.0))/6.0)



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
    >>> p.getattribute("ljsasajfsfdsdf")
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
    [u'Planet Upgrade: 1 (13) Building -- Matter Synth 1 8% done. ']
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
    ['Planet: 1 (13) Regional Taxes Collected -- 20']
    >>> p.resources.quatloos
    1020
    >>> p2 = Planet.objects.get(name="2")
    >>> p2.resources.quatloos
    980
    >>> f1 = Fleet(homeport=p,owner=u,sector=s,scouts=1)
    >>> f1.save()
    >>> p.doturn(report)
    >>> p.resources.quatloos
    1020 
    """
    replinestart = "Planet: " + self.name + " (" + str(self.id) + ") "

    # first build on upgrades
    [upgrade.doturn(report) for upgrade in self.upgradeslist()]
    
    # only owned planets produce
    if self.owner != None and self.resources != None:
      # do population cap for all planets
      if self.resources.people > 15000000:
        self.resources.people = 15000000
      
      # produce surplus resources
      self.doproduction(replinestart,report)
    
      # handle regional taxation
      if self.hasupgrade(Instrumentality.RGLGOVT):
        totaltax = self.nextregionaltaxation()
        report.append(replinestart + "Regional Taxes Collected -- %d" % (totaltax))
  
      # handle fleet upkeep costs 
      upkeep = self.fleetupkeepcosts()
      [self.resources.consume(line,upkeep[line]) for line in upkeep]
        
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


from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
import datetime
import math
import operator
import random

SVG_SCHEMA = "http://www.w3.org/Graphics/SVG/1.2/rng/"
DISPOSITIONS = (
    ('0', 'Garrison'),
    ('1', 'Planetary Defense'),
    ('2', 'Scout'),
    ('3', 'Screen'),
    ('4', 'Diplomacy'),
    ('5', 'Attack'),
    ('6', 'Colonize'),
    ('7', 'Move'),
    ('8', 'Trade'),
    ('9', 'Piracy'),
    )

INSTRUMENTALITIES = (
    ('0', 'Sensor Array'),
    ('1', 'Planetary Defense Network'),
    ('2', 'International Port'),
    ('3', 'Regional Government'),
    )


shiptypes = {
  'scouts':           {'accel': .3, 'att': 1, 'def': 10, 
                       'sense': 3.0, 'effrange': .5,
                       'required':
                         {'people': 5, 'food': 5, 'steel': 1, 
                         'antimatter': 1, 'quatloos': 10,
                         'unobtanium':0, 'krellmetal':0}
                      },
  'arcs':             {'accel': .18, 'att': 0, 'def': 2, 
                       'sense': 1.0, 'effrange': .25,
                       'required':
                         {'people': 500, 'food': 1000, 'steel': 200, 
                         'antimatter': 10, 'quatloos': 200,
                         'unobtanium':0, 'krellmetal':0}
                      },

  'merchantmen':      {'accel': .2, 'att': 0, 'def': 2, 
                       'sense': 1.0, 'effrange': .25,
                       'required':
                         {'people': 20, 'food': 20, 'steel': 30, 
                         'antimatter': 2, 'quatloos': 10,
                         'unobtanium':0, 'krellmetal':0}
                      },
  'fighters':         {'accel': 0.0,
                       'att': 5, 'def': 1, 
                       'sense': 1.0, 'effrange': 2.0,
                       'required':
                         {'people': 0, 'food': 0, 'steel': 1, 
                         'antimatter': 1, 'quatloos': 10,
                         'unobtanium':0, 'krellmetal':0}
                      },
  'frigates':         {'accel': .25, 'att': 10, 'def': 8, 
                       'sense': 5.0, 'effrange': 1.0,
                       'required':
                         {'people': 50, 'food': 50, 'steel': 50, 
                         'antimatter': 10, 'quatloos': 100,
                         'unobtanium':0, 'krellmetal':0}
                      },
  'destroyers':       {'accel':.22, 'att': 15, 'def': 7, 
                       'sense': 5.0, 'effrange': 1.2,
                       'required':
                         {
                         'people': 70, 'food': 70, 'steel': 100, 
                         'antimatter': 12, 'quatloos': 150,
                         'unobtanium':0, 'krellmetal':0}
                      },
  'cruisers':         {'accel': .22, 'att': 30, 'def': 6, 
                       'sense': 6.0, 'effrange': 1.8,
                       'required':
                         {
                         'people': 100, 'food': 100, 'steel': 200, 
                         'antimatter': 20, 'quatloos': 500,
                         'unobtanium':0, 'krellmetal':1}
                      },
  'battleships':      {'accel': .15, 'att': 50, 'def': 10, 
                       'sense': 6.0, 'effrange': 2.0,
                       'required':
                         {
                         'people': 200, 'food': 200, 'steel': 1000, 
                         'antimatter': 50, 'quatloos': 2000,
                         'unobtanium':0, 'krellmetal':3}
                      },
  'superbattleships': {'accel': .14, 'att': 100, 'def': 20, 
                       'sense': 7.0, 'effrange': 2.0,
                       'required':
                         {
                         'people': 300, 'food': 300, 'steel': 5000, 
                         'antimatter': 150, 'quatloos': 5000,
                         'unobtanium':1, 'krellmetal':5}
                      },
  'carriers':         {'accel': .13, 'att': 0, 'def': 10, 
                       'sense': 5.0, 'effrange': .5,
                       'required':
                         {
                         'people': 500, 'food': 500, 'steel': 7500, 
                         'antimatter': 180, 'quatloos': 6000,
                         'unobtanium':5, 'krellmetal':10} 
                       }
  }
  
productionrates = {'people': {'baserate': 1.3, 'socmodifier': -0.0035, 'initial': 50000},
                   'quatloos': {'baserate': 1.0, 'socmodifier': 0.0, 'initial': 1000},
                   'food': {'baserate': 1.1, 'socmodifier': -.0013, 'initial': 5000},
                   'consumergoods': {'baserate': .9999, 'socmodifier': .0000045, 'initial': 2000},
                   'steel': {'baserate': 1.001, 'socmodifier': 0.0, 'initial': 500},
                   'krellmetal': {'baserate': .99999, 'socmodifier': .00000029, 'initial': 0},
                   'unobtanium': {'baserate': .999995, 'socmodifier': .00000009, 'initial': 0},
                   'antimatter': {'baserate': .9999, 'socmodifier': .000008, 'initial': 50},
                   'hydrocarbon': {'baserate': 1.01, 'socmodifier': -.00018, 'initial': 1000}
                  }


class Instrumentality(models.Model):
  planet = models.ForeignKey('Planet')
  type = models.PositiveIntegerField(default=0, choices = INSTRUMENTALITIES)
  state = models.PositiveIntegerField(default=0)

class Player(models.Model):
  def __unicode__(self):
      return self.user.username
  user = models.ForeignKey(User, unique=True)
  lastactivity = models.DateTimeField(auto_now=True)
  capital = models.ForeignKey('Planet', unique=True)
  color = models.CharField(max_length=15)

  appearance = models.XMLField(blank=True, schema_path=SVG_SCHEMA)
  friends = models.ManyToManyField("self")
  enemies = models.ManyToManyField("self")
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
    self.lastactivity = datetime.datetime.now()
    userlist = User.objects.exclude(id=self.user.id)
    print "number of players = " + str(len(userlist))
    random.seed()
    userorder = range(len(userlist))
    random.shuffle(userorder)
    for uid in userorder:
      curuser= userlist[uid]
      planetlist = curuser.planet_set.all()
      if not len(planetlist):
        print "player has no planets"
      else:
        print "player has planets (" + str(len(planetlist)) + ")"
        planetorder = range(len(planetlist))
        random.shuffle(planetorder)
        for pid in planetorder:
          curplanet = planetlist[pid]
          distantplanets = nearbysortedthings(Planet,curplanet)
          distantplanets.reverse()
          print "  number of distant planets = " + str(len(distantplanets))
          if len(distantplanets) < 6:
            continue
          for distantplanet in distantplanets:
            suitable = True
            #look at the 'distant planet' and its 5 closest 
            # neighbors and see if they are available
            if distantplanet.owner is not None:
              continue 
            nearcandidates = nearbysortedthings(Planet,distantplanet)
            # make sure the 5 closest planets are free
            for nearcandidate in nearcandidates[:5]:
              if nearcandidate.owner is not None:
                suitable = False
                break
            #if there is a nearby inhabited planet closer than 7
            #units away, continue...
            for nearcandidate in nearcandidates:
              distance = getdistanceobj(nearcandidate,distantplanet)
              if nearcandidate.owner is not None:
                if  distance < 9.0:
                  suitable = False
                  break
              elif distance > 9.0:
                print "success!"
                #success!
                break
                
            if suitable:
              print "suitable planet " + str(distantplanet.id)
              distantplanet.owner = self.user
              self.capital = distantplanet
              #self.color = "#ff0000"
              self.color = "#" + hex(((random.randint(64,255) << 16) + 
                            (random.randint(64,255) << 8) + 
                            (random.randint(64,255))))[2:]
              self.save()
              distantplanet.populate()
              distantplanet.save()
              return
      print "--"
class Manifest(models.Model):
  people = models.PositiveIntegerField(default=0)
  food = models.PositiveIntegerField(default=0)
  consumergoods = models.PositiveIntegerField(default=0)
  steel = models.PositiveIntegerField(default=0)
  krellmetal = models.PositiveIntegerField(default=0)
  unobtanium = models.PositiveIntegerField(default=0)
  antimatter = models.PositiveIntegerField(default=0)
  hydrocarbon = models.PositiveIntegerField(default=0)
  quatloos = models.PositiveIntegerField(default=0)
  def manifestlist(self, skip):
    mlist = {}
    for field in self._meta.fields:
      if field.name not in skip: 
        mlist[field.name] = getattr(self,field.name)
    return mlist

class Fleet(models.Model):
  def __unicode__(self):
    numships = self.numships()
    return '(' + str(self.id) + ') '+ str(numships) + ' ship' + ('' if numships == 1 else 's')
  owner = models.ForeignKey(User)
  disposition = models.PositiveIntegerField(default=0, choices = DISPOSITIONS)
  homeport = models.ForeignKey("Planet", null=True, related_name="home_port", editable=False)
  trade_manifest = models.ForeignKey("Manifest", null=True, editable=False)
  sector = models.ForeignKey("Sector", editable=False)
  speed = models.FloatField(default=0)
  direction = models.FloatField(default=0, editable=False)
  x = models.FloatField(default=0, editable=False)
  y = models.FloatField(default=0, editable=False)

  destination = models.ForeignKey("Planet", null=True, editable=False)
  dx = models.FloatField(default=0, editable=False)
  dy = models.FloatField(default=0, editable=False)
  
  scouts = models.PositiveIntegerField(default=0)
  arcs = models.PositiveIntegerField(default=0)
  merchantmen = models.PositiveIntegerField(default=0)
  fighters = models.PositiveIntegerField(default=0)
  frigates = models.PositiveIntegerField(default=0)
  destroyers = models.PositiveIntegerField(default=0)
  cruisers = models.PositiveIntegerField(default=0)
  battleships = models.PositiveIntegerField(default=0)
  superbattleships = models.PositiveIntegerField(default=0)
  carriers = models.PositiveIntegerField(default=0)

  def description(self):
    desc = []
    desc.append(self.__unicode__() + ":")
    for type in self.shiptypeslist():
      desc.append(str(getattr(self,type.name)) + " --> " + type.name)
    desc.append("acceleration = " + str(self.acceleration()))
    desc.append("attack = " + str(self.numattacks()) + " defense = " + str(self.numdefenses()))
    return "\n".join(desc)
  def json(self, playersship=0):
    json = {}
    json['x'] = self.x
    json['y'] = self.y
    json['i'] = self.id
    json['c'] = self.owner.get_profile().color
    if playersship == 1:
      json['ps'] = 1
    if self.dx:
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
    else:
      json['x2'] = 0
      json['y2'] = 0

    return json

  def svg(self):
    svg = []
    if self.dx:
      distanceleft = getdistance(self.x,self.y,self.dx,self.dy)
      angle = math.atan2(self.x-self.dx,self.y-self.dy)
      if distanceleft > .2:
        x2 = self.x - math.sin(angle) * (distanceleft-.2)
        y2 = self.y - math.cos(angle) * (distanceleft-.2)
      else:
        x2 = self.dx
        y2 = self.dy
      svg.append('<line stroke-width=".02" stroke="#330000"')
      svg.append(' marker-end="url(#endArrow)" x1="')
      svg.append(str(self.x))
      svg.append('" y1="')
      svg.append(str(self.y))
      
      svg.append('" x2="')
      svg.append(str(x2))
      svg.append('" y2="')
      svg.append(str(y2))
      svg.append('"/>\n')

    svg.append('<circle cx="')
    svg.append(str(self.x))
    svg.append('" cy="')
    svg.append(str(self.y))
    svg.append('" r=".02" fill="red"')

    svg.append(' onmouseover="fleethoveron(evt,')
    svg.append(str(self.id))
    svg.append(')" onmouseout="fleethoveroff(evt,')
    svg.append(str(self.id))
    svg.append(')" onclick="dofleetmousedown(evt,')
    svg.append(str(self.id))
    svg.append(')" />')
    return ''.join(svg)
  def gotoplanet(self,destination):
    self.direction = math.atan2(self.x-destination.x,self.y-destination.y)
    self.dx = destination.x
    self.dy = destination.y
    self.destination = destination
    self.sector = Sector.objects.get(pk=int(self.x/5.0) * 1000 + int(self.y/5.0))
    self.save()
  def gotoloc(self,dx,dy):
    self.dx = float(dx)
    self.dy = float(dy)
    self.direction = math.atan2(self.x-self.dx,self.y-self.dy)
    self.destination = None
    self.sector = Sector.objects.get(pk=int(self.x/5.0) * 1000 + int(self.y/5.0))
    self.save()
  def arrive(self):
    self.speed=0
    self.x = self.dx
    self.y = self.dy

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
    if self.numships() > 0:
      range =  max([shiptypes[x.name]['sense'] for x in self.shiptypeslist()])
      range += min([self.homeport.society*.002, .5])
      range += min([self.numships()*.05, 1.0])
    return range
  def numships(self):
    return sum([getattr(self,x.name) for x in self.shiptypeslist()]) 
   
  def dotrade(self):
    print "fleet " + str(self.id) + " trading at planet "\
          + str(self.destination.id)
    if self.trade_manifest is None:
      return
    # sell whatever is in the hold
    m = self.trade_manifest
    curplanet = self.destination
    curprices = curplanet.getprices()
    shipsmanifest = m.manifestlist(['id','quatloos'])
    planetmanifest = curplanet
    for line in shipsmanifest:
      shipsmanifest.quatloos += curplanet.getprice(line) * getattr(m,line)
      setattr(m,line,0)
      print line + " --> " + str(quatloos)
      
    # look for next destination (most profitable...)

    # first build a list of neary planets, sorted by distance
    plist = []
    for planet in nearbythings(Planet,self.x,self.y):
      planet.distance = getdistance(self.x,self.y,planet.x,planet.y)
      plist.append(planet)
    plist.sort(reverse=True, key=operator.attrgetter('distance'))
    
    maxdif = -100
    bestplanet = 0
    bestcommodity = 0 
    for destplanet in plist:
      print str(destplanet.id) + " " + destplanet.name + " -- " + str(destplanet.resources) + " " + str(destplanet.x)+","+str(destplanet.y)
      if destplanet.resources:# and (destplanet.opentrade or destplanet.owner == self.owner):
        print "2"
        destprices = destplanet.getprices()
        print destprices
        for item in destprices:
          #    10                  8
          if destprices[item] - curprices[item] - (destplanet.distance*.1)> maxdif:
            print "."
            maxdif = destprices[item] - curprices[item] - (destplanet.distance*.1)
            bestplanet = destplanet
            bestcommodity = item
    if bestplanet:
      self.gotoplanet(bestplanet)
      setattr(m, bestcommodity, getattr(m, bestcommodity) + quatloos/bestplanet.getprice(bestcommodity))
      shipsmanifest.quatloos = quatloos%bestplanet.getprice(bestcommodity)
      print "bought " + str(getattr(m,bestcommodity)) + " " + bestcommodity
      print "leftover quatloos = " + str(quatloos)
      print "new destination = " + str(bestplanet.id)
    # disembark passengers (if they want to disembark here, otherwise
    # they wait until the next destination)
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
    self.x = planet.x
    self.y = planet.y
    self.dx = planet.x
    self.dy = planet.y
    self.sector = planet.sector
    self.owner = planet.owner
    
    if self.arcs > 0:
      self.disposition = 6
    elif self.merchantmen > 0:
      self.disposition = 8
      self.trade_manifest = Manifest()
      self.trade_manifest.save() 
    self.save()
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
      sectorkey = int(self.x/5.0)*1000 + int(self.y/5.0)
      self.sector = Sector.objects.get(pk=sectorkey)

  def doturn(self):
    print "fleet " + str(self.id)
    # see if we need to move the fleet...
    distancetodest = getdistance(self.x,self.y,self.dx,self.dy)
    # figure out how fast the fleet can go
    
    print "ddd = " + str(distancetodest)
    if distancetodest < self.speed: 
      # we have arrived at our destination
      print "arrived at destination"
      self.arrive()

      if self.disposition == 6 and self.arcs > 0:
        self.destination.colonize(self)
        if self.numships() == 0:
          self.delete()
      # handle trade disposition
      if self.disposition == 8 and self.destination and self.trade_manifest:   
        self.dotrade()
      else:
        self.destination=None

    else:
      self.move()
    self.save()
      
class Message(models.Model):
  def __unicode__(self):
      return self.subject
  subject = models.CharField(max_length=80)
  message = models.TextField()
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
  def __unicode__(self):
      return self.name + "-" + str(self.id)
  name = models.CharField(max_length=50)
  owner = models.ForeignKey(User, null=True)
  sector = models.ForeignKey('Sector')
  x = models.FloatField()
  y = models.FloatField()
  r = models.FloatField()
  color = models.PositiveIntegerField()
  society = models.PositiveIntegerField()

  resources = models.ForeignKey('Manifest', null=True)
  tariffrate = models.FloatField(default=0)
  inctaxrate = models.FloatField(default=0)
  openshipyard = models.BooleanField(default=False)
  opencommodities = models.BooleanField(default=False)
  opentrade = models.BooleanField(default=False)
  def colonize(self, fleet):
    if self.owner != None:
      # colonization doesn't happen if the planet is already colonized
      # (someone beat you to it, sorry...)
      fleet.gotoplanet(fleet.homeport)
      msg = Message(toplayer=fleet.owner, fromplayer=fleet.owner,
                    subject="Colonization Fleet " + str(fleet.id) + " Report",
                    message="We must sadly report that planet " + str(self.id) +
                    "(" + self.name + ") is already populated.\n\n We " +
                    "are currently " +
                    "returning to our home port, but could easily be diverted to a " +
                    "new destination on your orders.")
      msg.save()

    if self.resources == None:
      self.resources = Manifest()
    numarcs = fleet.arcs
    for commodity in shiptypes['arcs']['required']:
      setattr(self.resources,commodity,shiptypes['arcs']['required'][commodity]*numarcs)
    self.owner = fleet.owner
    self.resources.save()
    fleet.arcs = 0
    fleet.save()
    self.save()
  def buildableships(self):
    buildable = {}
    buildable['types'] = {}
    buildable['commodities'] = {}
    buildable['available'] = []
    # this is a big imperative mess, but it's somewhat readable
    # (woohoo!)
    for type in shiptypes:
      isbuildable = True
      for needed in shiptypes[type]['required']:
        if shiptypes[type]['required'][needed] > getattr(self.resources,needed):
          isbuildable = False
          break 
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
    self.inctaxrate = .07
    self.tariffrate = 0.0
    self.openshipyard = False
    self.opencommodities = False
    self.opentrade = False
    self.resources = resources
    self.save()
  def getprice(self,commodity):
    basevalue = 1/(1-productionrates[commodity]['baserate'])
    if self.society*productionrates[commodity]['socmodifier'] != 0.0:
      cursocmodifier = 1/(self.society*productionrates[commodity]['socmodifier'])
    else:
      cursocmodifier = 0.0
    unitprice = (15000 + basevalue + cursocmodifier)/1000.0
    return int(round(10.0 * unitprice))

  def getprices(self):
    pricelist = {}
    if self.resources != None:
      resourcelist = self.resources.manifestlist(['id','quatloos'])
      for resource in resourcelist:
        pricelist[resource] = self.getprice(resource) 
    return pricelist 

  def json(self,playersplanet=0):
    json = {}

    if self.owner:
      json['h'] = self.owner.get_profile().color
      if self.owner.get_profile().capital == self:
        json['cap'] = "1"
    else:
      json['h'] = 0

    json['x'] = self.x
    json['y'] = self.y
    json['c'] = "#" + hex(self.color)[2:]
    json['r'] = self.r
    json['i'] = self.id
    if playersplanet == 1:
      json['pp'] = 1
    return json

  def svg(self):
    svg = []
    # first draw the highlight circle
    if self.society > 49:
      svg.append('<circle cx="')
      svg.append(str(self.x))
      svg.append('" cy="')
      svg.append(str(self.y))
      svg.append('" r="')
      svg.append(str(.15))
      svg.append('" stroke="darkred"')
      svg.append(' stroke-width=".01"/>')
      
    if self.highlight:
      svg.append('<circle cx="')
      svg.append(str(self.x))
      svg.append('" cy="')
      svg.append(str(self.y))
      svg.append('" r="')
      svg.append(str(.1))
      svg.append('" stroke="')
      svg.append(self.highlight)
      svg.append('" stroke-width=".03"/>')
    # then draw the star itself
    svg.append('<circle cx="')
    svg.append(str(self.x))
    svg.append('" cy="')
    svg.append(str(self.y))
    svg.append('" r="')
    svg.append(str(self.r))
    svg.append('" fill="#')
    svg.append(hex(self.color)[2:])
    svg.append('" onmouseover="planethoveron(evt,')
    svg.append(str(self.id))
    svg.append(')" onmouseout="planethoveroff(evt,')
    svg.append(str(self.id))
    svg.append(')" onclick="doplanetmousedown(evt,')
    svg.append(str(self.id))
    svg.append(')" />')
    return ''.join(svg)
    #<circle cx="{{ planet.x }}" cy="{{ planet.y }}" r=".02" fill="black" />
  def doturn(self):
    # only owned planets produce
    if self.owner != None and self.resources != None:
      curpopulation = self.resources.people
      popgrowth = productionrates['food']['socmodifier']*self.society
      if self.resources.food > 0 or popgrowth > 1.0:
        for resource in productionrates.keys():
          # 'baserate': 1.2, 'socmodifier'
          stats = productionrates[resource]
          oldval = getattr(self.resources, resource)
          produced = (stats['baserate']+(stats['socmodifier']*self.society))*curpopulation
          if resource in ['food']:
            aftertax = produced * (1-(self.inctaxrate/15.0))
          else:
            aftertax = produced
          newval = max([0,oldval+aftertax-curpopulation])
          setattr(self.resources, resource, newval)
      elif productionrates['food']['socmodifier']*self.society < 1.0:
        # uhoh, famine...
        self.population = int(curpopulation * .95)
      
      # increase the planet's treasury through taxation
      self.resources.quatloos += (self.resources.people * self.inctaxrate)/6.0
      
      # increase the society count if the player has played
      # in the last 2 days.
      if self.owner is None:
        print "fuck!"
      else:
        print self.owner
      if self.owner.get_profile().lastactivity >  datetime.datetime.today() - datetime.timedelta(hours=36):
        self.society += 1
      self.save()
      self.resources.save()
def nearbythings(thing,x,y):
  sx = int(x)/5
  sy = int(y)/5
  return thing.objects.filter(
    Q(sector=((sx-1)*1000)+sy-1)|
    Q(sector=((sx-1)*1000)+sy)|
    Q(sector=((sx-1)*1000)+sy+1)|
    Q(sector=(sx*1000)+sy-1)|
    Q(sector=(sx*1000)+sy)|
    Q(sector=(sx*1000)+sy+1)|
    Q(sector=((sx+1)*1000)+sy-1)|
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
  nearby.sort(lambda x,y:int(getdistanceobj(curthing,x)-
                                     getdistanceobj(curthing,y)))
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





def buildneighborhood(player):
  sectors = Sector.objects.filter(planet__owner=player)
  neighborhood = {}
  neighborhood['sectors'] = []
  neighborhood['fleets'] = []
  neighborhood['planets'] = []
  neighborhood['neighbors'] = []
  neighborhood['viewable'] = []

  extents = [2001,2001,-1,-1]
  allsectors = []
  for sector in sectors:
    if sector.key not in allsectors:
      allsectors.append(sector.key)

    testsector = (sector.x-1)*1000 + sector.y
    if testsector not in allsectors:
      allsectors.append(testsector)

    testsector = (sector.x-1)*1000 + sector.y-1
    if testsector not in allsectors:
      allsectors.append(testsector)

    testsector = (sector.x-1)*1000 + sector.y+1
    if testsector not in allsectors:
      allsectors.append(testsector)

    testsector = (sector.x)*1000 + sector.y-1
    if testsector not in allsectors:
      allsectors.append(testsector)

    testsector = (sector.x)*1000 + sector.y+1
    if testsector not in allsectors:
      allsectors.append(testsector)

    testsector = (sector.x+1)*1000 + sector.y-1
    if testsector not in allsectors:
      allsectors.append(testsector)

    testsector = (sector.x+1)*1000 + sector.y
    if testsector not in allsectors:
      allsectors.append(testsector)
    
    testsector = (sector.x+1)*1000 + sector.y+1
    if testsector not in allsectors:
      allsectors.append(testsector)
  neighborhood['sectors'] = Sector.objects.filter(key__in=allsectors)

  for sector in neighborhood['sectors']:
    for fleet in sector.fleet_set.all():
      neighborhood['fleets'].append(fleet)  
    for planet in sector.planet_set.all():
      if planet.owner == player:
        planet.highlight = "red"
      elif planet.owner is not None:
        if planet.owner not in neighborhood['neighbors']:
          planet.owner.relation = player.get_profile().getpoliticalrelation(planet.owner.get_profile())
          neighborhood['neighbors'].append(planet.owner)
        planet.highlight = "orange"
      else:
        planet.highlight = 0 
      neighborhood['planets'].append(planet)
    extents=setextents(sector.x,sector.y,extents)
  extent = 0
  if extents[2]-extents[0] > extents[3]-extents[1]:
    extent = extents[2]-extents[0]+5
  else:
    extent = extents[3]-extents[1]+5

  neighborhood['viewable'] = (extents[0],extents[1],extent,extent)

  return neighborhood 

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
TRADEGOODS = (
    ('0', 'Food'),
    ('1', 'Metals'),
    ('2', 'Consumer Goods'),
    ('3', 'Antimatter'),
    ('4', 'Hydrocarbon'),
    ('5', 'Quatloos')
    )

class Player(models.Model):
  def __unicode__(self):
      return self.user.username
  user = models.ForeignKey(User, unique=True)
  lastactivity = models.DateTimeField(auto_now=True)
  appearance = models.XMLField(blank=True, schema_path=SVG_SCHEMA)
  def create(self):
    if len(self.user.planet_set.all()) > 0:
      print "cheeky fellow"
      return
    userlist = User.objects.exclude(id=self.user.id)
    print len(userlist)
    random.seed()
    userorder = range(len(userlist))
    random.shuffle(userorder)
    for uid in userorder:
      curuser= userlist[uid]
      planetlist = curuser.planet_set.all()
      if len(planetlist):
        print "user with planets --> " + curuser.username
        planetorder = range(len(planetlist))
        random.shuffle(planetorder)
        print "po --> " + str(planetorder)
        for pid in planetorder:
          curplanet = planetlist[pid]
          distantplanets = nearbythings(Planet,curplanet.x,curplanet.y).reverse()
          if len(distantplanets) < 6:
            continue
          suitable = True
          for distantplanet in distantplanets[:5]:
            nearcandidates = nearby(Planet,distantplanet.x,distantplanet.y)[:5]
            for nearcandidate in nearcandidates[:5]:
              if nearcandidate.owner is not None:
                suitable = False
                break
            if suitable:
              print "yay! " + str(distantplanet.id)
              distantplanet.owner = self.user
              distantplanet.populate()
              distantplanet.save()
              return
            else:
              print "not suitable"

            
      else:
        print "user with no planets :("

class Manifest(models.Model):
  people = models.PositiveIntegerField(default=0)
  food = models.PositiveIntegerField(default=0)
  consumergoods = models.PositiveIntegerField(default=0)
  metals = models.PositiveIntegerField(default=0)
  antimatter = models.PositiveIntegerField(default=0)
  hydrocarbon = models.PositiveIntegerField(default=0)
  quatloos = models.PositiveIntegerField(default=0)
  productionrates = {'food': {'baserate': 1.2, 'socmodifier': -.0026},
                     'consumergoods': {'baserate': .7, 'socmodifier': .007},
                     'metals': {'baserate': .8, 'socmodifier': .006},
                     'antimatter': {'baserate': .5, 'socmodifier': .012},
                     'hydrocarbon': {'baserate': 1.1, 'socmodifier': -.01}
                    }
  def manifestlist(self):
    mlist = {}
    for field in self._meta.fields:
      if field.name not in ['id','quatloos']:
        mlist[field.name] = getattr(self,field.name)
    return mlist

class Fleet(models.Model):
  def __unicode__(self):
    numships = self.shipcount()
    return '(' + str(self.id) + ') '+ str(numships) + ' ship' + '' if numships == 1 else 's'
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
  def acceleration(self):
    accel = 0.0
    if self.scouts != 0:
      accel = .3
    if self.frigates != 0:
      accel = .25
    if self.destroyers != 0:
      accel = .22
    if self.merchantmen != 0:
      accel = .2
    if self.cruisers != 0:
      accel = .18
    if self.battleships != 0:
      accel = .15
    if self.superbattleships != 0:
      accel = .14
    if self.carriers != 0:
      accel = .13
    return accel
  def shipcount(self):  
    numships = self.scouts + self.merchantmen + self.fighters + self.frigates\
               + self.destroyers + self.cruisers + self.battleships\
               + self.superbattleships
    return numships
  def arrive(self):
    self.speed=0
    self.x = self.dx
    self.y = self.dy


  def dotrade(self):
    print "fleet " + str(self.id) + " trading at planet "\
          + str(self.destination.id)
    # sell whatever is in the hold
    m = self.trade_manifest
    curplanet = self.destination
    curprices = curplanet.getprices()
    shipsmanifest = m.manifestlist()
    planetmanifest = curplanet
    for line in shipsmanifest:
      shiptsmanifest.quatloos += curplanet.getprice(line) * getattr(m,line)
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
  def newfleetsetup(self,planet):
    if self.merchantmen > 0:
      self.disposition = 8
    self.homeport = planet
    self.x = planet.x
    self.y = planet.y
    self.sector = planet.sector
    self.owner = planet.owner
    self.save()
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
    print "ship " + str(self.id)
    # see if we need to move the fleet...
    if self.disposition in [2,4,5,6,7,8]:
      distancetodest = getdistance(self.x,self.y,self.dx,self.dy)
      # figure out how fast the fleet can go
      
      print "ddd = " + str(distancetodest)
      if distancetodest < self.speed: 
        # we have arrived at our destination
        print "arrived at destination"
        self.arrive()

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
  fleet = models.ForeignKey('Fleet')
  
class Sector(models.Model):
  def __unicode__(self):
      return str(self.key)
  key = models.IntegerField(primary_key=True)
  controllingplayer = models.ForeignKey(User, null=True)
  x = models.IntegerField()
  y = models.IntegerField()

class Planet(models.Model):
  def __unicode__(self):
      return self.name
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
    if self.resources == None:
      self.resources = Manifest()
    self.resources.people = fleet.manifest.people
    self.owner = fleet.owner
    fleet.manifest.people = 0
    fleet.manifest.save()  
    self.resources.save()

  def populate(self):
    # populate builds a new capital (i.e. a player's first
    # planet, the one he comes from...)
    if self.resources == None:
      self.resources = Manifest(food=1000, consumergoods=500, \
                                metals=500, antimatter=10, \
                                hydrocarbon=200, quatloos=2000, \
                                people = 50000)
    self.inctaxrate = .07
    self.tariffrate = 0.0
    self.openshipyard = False
    self.opencommodities = False
    self.opentrade = False

  def getprice(self,commodity):
    unitprice = self.resources.productionrates[commodity]['baserate'] + \
                self.society*self.resources.productionrates[commodity]['socmodifier']
    return int(round(10.0 * unitprice))

  def getprices(self):
    pricelist = {}
    if self.resources != None:
      resourcelist = self.resources.manifestlist()
      for resource in resourcelist:
        pricelist[resource] = self.getprice(resource) 
    return pricelist 
  def svg(self):
    svg = []
    # first draw the highlight circle
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
      self.resources.food -= int(self.population*.2)
      if self.resources.food > 0:
        self.population = self.population + int(self.population * .15)
        self.resources.food = self.resources.food + int(self.resources.food * .15)
        self.resources.metals = self.resources.metals + int(self.resources.metals * .15)
      else:
        # uhoh, famine...
        self.population = self.population - int(self.population * .5)
      # increase the society count if the player has played
      # in the last 2 days.
      #if self.owner.player.lastactivity >  datetime.datetime.today() - datetime.timedelta(days=2):
      #  self.society += 1
      self.save()

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


def getdistance(x1,y1,x2,y2):
  return math.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))

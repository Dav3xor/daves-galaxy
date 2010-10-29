from newdominion.settings import DEBUG_PRINT
from random import *
from math import *

from django.db.models import Q
import django

import datetime
import operator
import random
import time

def getdistanceobj(o1,o2):
  return getdistance(o1.x,o1.y,o2.x,o2.y)

def getdistance(x1,y1,x2,y2):
  return sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))

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
  sectors = [(((sx-1)*1000)+sy-1),
             (((sx-1)*1000)+sy-1),
             (((sx-2)*1000)+sy),
             (((sx-1)*1000)+sy),
             (((sx-1)*1000)+sy+1),
             ((sx*1000)+sy-2),
             ((sx*1000)+sy-1),
             ((sx*1000)+sy),
             ((sx*1000)+sy+1),
             ((sx*1000)+sy+2),
             (((sx+1)*1000)+sy-1),
             (((sx+2)*1000)+sy),
             (((sx+1)*1000)+sy),
             (((sx+1)*1000)+sy+1)]
  if type(thing) == django.db.models.query.QuerySet:
    return thing.filter(sector__in=sectors)
  else:
    return thing.objects.filter(sector__in=sectors)


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
      d = sqrt((s['x']-f.x)**2 + (s['y']-f.y)**2)
      if d < s['r']:
        f.keep=1
  
  for f in neighborhood['fleets']:
    if f.keep == 1:
      if f.sector.key not in neighborhood['fbys']:
        neighborhood['fbys'][f.sector.key] = []
      neighborhood['fbys'][f.sector.key].append(f)
  return neighborhood



def findbestdeal(curplanet, destplanet, quatloos, capacity, dontbuy, nextforeign, prices):
  bestprofit = -10000.0
  bestitem = "none"

  if not prices.has_key(curplanet.id):
    prices[curplanet.id] = curplanet.getprices(False)
  curprices = prices[curplanet.id]
  
  if not prices.has_key(destplanet.id):
    prices[destplanet.id] = destplanet.getprices(False)
  destprices = prices[destplanet.id]

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

class Point():
  def __init__(self,newx,newy):
      self.x = newx
      self.y = newy


def distancetoline(p, l1, l2):
  """
  >>> p  = Point(5.0,0.0)
  >>> l1 = Point(0.0,-5.0)
  >>> l2 = Point(0.0,5.0)
  >>> distancetoline(p,l1,l2) 
  5.0
  >>> p  = Point(5.0,0.0)
  >>> l1 = Point(0.0,1.0)
  >>> l2 = Point(0.0,10.0)
  >>> distancetoline(p,l1,l2) == getdistanceobj(p,l1) 
  True
  >>> p  = Point(1.0,2.0)
  >>> l1 = Point(0.0,0.0)
  >>> l2 = Point(5.0,5.0)
  >>> distancetoline(p,l1,l2) 
  0.70710678118654757
  >>> p  = Point(0.0,0.0)
  >>> l1 = Point(0.0,-5.0)
  >>> l2 = Point(0.0,5.0)
  >>> distancetoline(p,l1,l2) 
  0.0
  """
  vx = l1.x-p.x 
  vy = l1.y-p.y
  ux = l2.x-l1.x
  uy = l2.y-l1.y

  length = ux*ux+uy*uy;

  det = (-vx*ux)+(-vy*uy); 
  # if this is < 0 or > length then its outside the line segment
  if det<0 or det>length:
    ux=l2.x-p.x
    uy=l2.y-p.y
    return sqrt(min(vx*vx+vy*vy, ux*ux+uy*uy))

  det = ux*vy-uy*vx
  if length == 0.0:
    return 0.0
  else:
    return sqrt((det*det)/length)


def checkintersection(p1,p2,p3,p4):
  """
  >>> p1 = Point(0.0,0.0)
  >>> p2 = Point(1.0,0.0)
  >>> p3 = Point(1.0,1.0)
  >>> p4 = Point(0.0,1.0)
  >>> checkintersection(p1,p3,p2,p4)
  True
  >>> checkintersection(p4,p2,p3,p1)
  True
  >>> checkintersection(p1,p4,p2,p3)
  False
  >>> checkintersection(p1,p2,p4,p3)
  False
  >>> p1 = Point(1.0,1.0)
  >>> p2 = Point(1.0,4.0)
  >>> p3 = Point(4.0,1.0)
  >>> p4 = Point(1.1,4.0)
  >>> checkintersection(p1,p2,p3,p2)
  False
  >>> checkintersection(p1,p2,p3,p4)
  False
  """
  def isonsegment(i,j,k):
    return ((i.x <= k.x or j.x <= k.x) and (k.x <= i.x or k.x <= j.x) and
           (i.y <= k.y or j.y <= k.y) and (k.y <= i.y or k.x <= j.y))

  def computedirection(i,j,k):
    a = (k.x - i.x) * (j.y - i.y);
    b = (j.x - i.x) * (k.y - i.y);
    if a < b:
      return -1
    elif a > b:
      return 1
    else:
      return 0

  # return no intersection if they
  if p1.x == p3.x and p1.y == p3.y:
    return False 
  if p1.x == p4.x and p1.y == p4.y:
    return False
  if p2.x == p3.x and p2.y == p3.y:
    return False
  if p2.x == p4.x and p2.y == p4.y:
    return False


  d1 = computedirection(p3,p4,p1)
  d2 = computedirection(p3,p4,p2)
  d3 = computedirection(p1,p2,p3)
  d4 = computedirection(p1,p2,p4)
  return ((((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and
          ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0))) or
         (d1 == 0 and isonsegment(p3,p4,p1)) or
         (d2 == 0 and isonsegment(p3,p4,p2)) or
         (d3 == 0 and isonsegment(p1,p2,p3)) or
         (d4 == 0 and isonsegment(p1,p2,p4)))
         


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
def dprint(stuff):
  if DEBUG_PRINT:
    print stuff

def cubicrandomchoice(maxnum,numchoices):
  if numchoices >= maxnum:
    return range(maxnum)
  else:
    chosen = {} 
    for i in xrange(numchoices):
      while len(chosen) < numchoices:
        x = random()
        choice = int(floor(((x*x*x)*maxnum)))
        if choice not in chosen:
          chosen[choice] = 1
          break
    return chosen.keys()


def normalizecolor(color):
  splitcolor = [0,0,0]

  if color[0] == '#':
    color = color[1:]
  
  color = int(color,16)
  splitcolor[0] = color >> 16
  splitcolor[1] = (color >> 8)%256
  splitcolor[2] = color % 256
  maxcomp = max(splitcolor)
  if maxcomp < 127:
    brighten = 255-maxcomp
    splitcolor[0] += brighten
    splitcolor[1] += brighten
    splitcolor[2] += brighten

  color = 0
  color += splitcolor[0] << 16
  color += splitcolor[1] << 8
  color += splitcolor[2]

  #color = '#'+hex(color)[2:]
  color = "#%06X" % color
  return color 

if __name__ == '__main__':
  print str(cubicrandomchoice(10,3))
  print str(cubicrandomchoice(5,5))
  print str(cubicrandomchoice(10000,5))


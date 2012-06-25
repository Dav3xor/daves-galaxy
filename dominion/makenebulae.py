from newdominion.dominion.models import *
import Image, ImageDraw
import simplejson
from shapely.geometry import Point, Polygon, MultiPolygon, box
from shapely.ops import cascaded_union
from PIL import *
from random import randint
from random import random

MAXSIZE = 3

class PrettyFloat(float):
  def __repr__(self):
    return '%4.2f' % self

def pretty_floats(obj):
  if isinstance(obj, float):
    return PrettyFloat(obj)
  elif isinstance(obj, dict):
    return dict((k, pretty_floats(v)) for k, v in obj.items())
  elif isinstance(obj, (list, tuple)):
    return map(pretty_floats, obj)             
  return obj

testimage = Image.new('RGB',(3000,3000))
draw = ImageDraw.Draw(testimage)

pf = open('stars.pov','r')
output = open('nebulae.txt','w')

radius = 4 
minarea = radius*radius*3.14159 * 1.5
points = []
sectors = {}
inhabited = {}
def buildsquares(layer1, layer2):
  for x in xrange(0,3000,5):
    print "x=" +str(x)
    layer1strip = box(x,0,x+5,3000).intersection(layer1)
    layer2strip = box(x,0,x+5,3000).intersection(layer2)
    for y in xrange(0,3000,5):
      skey = buildsectorkey(x+2.5,y+2.5)
      ix = int((x+2.5)/5)
      iy = int((y+2.5)/5)
      if (ix,iy) not in inhabited:
        continue
      square = box(x,y,x+5,y+5)
      jsquare = {}
      neb1 = square.intersection(layer1strip)
      neb2 = square.intersection(layer2strip)
      if neb1.area:
        jsquare[1] = jsonsquare(neb1) 
      if neb2.area:
        jsquare[2] = jsonsquare(neb2)
      
      if len(jsquare):
        sector = Sector.objects.filter(key=skey)
        if sector.count() == 0:
          sector = Sector(key=skey, x=x, y=y)
        else:
          sector = sector[0]
        sector.nebulae = simplejson.dumps(pretty_floats(jsquare))
        sector.save()

def jpoly(poly):
  output = []
  curpoly = []
  for p in poly.exterior.coords[:-1]:
    curpoly.append(p[0])
    curpoly.append(p[1])
  output.append(curpoly)
  for i in poly.interiors:
    curpoly = [] 
    for p in i.coords[:-1]:
      curpoly.append(p[0])
      curpoly.append(p[1])
    output.append(curpoly)
  return output 

def jsonsquare(layer):      
  output = []

  if layer.geom_type == 'MultiPolygon':
    for g in layer.geoms:
      if g.geom_type == 'Polygon':
        output.append(jpoly(g))
      else:
        print "uhoh"
  elif layer.geom_type == 'Polygon':
    output.append(jpoly(layer)) 
  return output




def buildsector(sector,extent):
  def checkwithinsector(poly,extent):
    pbounds = poly.bounds
    #print "("+str(pbounds[0])+","+str(pbounds[1])+","+\
    #      str(pbounds[2])+","+str(pbounds[3])+")-("+\
    #      str(extent[0])+","+str(extent[1])+\
    #      ","+str(extent[2])+","+str(extent[3])+")"
    if pbounds[0] > extent[0] and pbounds[1] > extent[1] and \
       pbounds[2] < extent[2] and pbounds[3] < extent[3]:
      print "-"
      points = None
    else:
      print "+"
  points = []
  for p in sector:
    points.append(Point(p[0],p[1]).buffer(1.0+((MAXSIZE-1)*random())))
  # make a union of all the points
  if len(points):
    points = cascaded_union(points)
  else:
    points = MultiPolygon()
  print 'before ' + str(points.area)

  # now simplify the resulting union...
  if points.geom_type == 'Polygon' and points.area < minarea:
    if checkwithinsector(points,extent):
      points = None
  elif points.geom_type == 'MultiPolygon':
    # remove the smallest blobs...
    points = [i for i in points.geoms if i.area > minarea or checkwithinsector(i,extent)]
    if len(points):
      points = cascaded_union(points)
      points = points.simplify(.5, preserve_topology=True)
    else:
      points = None
    
  # print the area if there's anything left
  if points:
    print 'after ' + str(points.area)
  else:
    print 0
  return points

def writegeometry(whole, color):
  for g in whole.geoms:
    if g.geom_type == 'Polygon':
      output.write('poly\n') 
      draw.polygon(g.exterior.coords,color)
      for p in g.exterior.coords:
        output.write(str(p[0]) + ' ' + str(p[1]) + '\n')
      for i in g.interiors:
        #print "interior " + i.geom_type
        if i.geom_type == 'Polygon':
          output.write('hole\n')
          draw.polygon(i.exterior.coords,(0,255,0))
          for p in i.exterior.coords: 
            output.write(str(p[0]) + ' ' + str(p[1]) + '\n')
        elif i.geom_type == 'LinearRing':
          #print str(i)
          output.write('hole\n')
          draw.polygon(i.coords,(0,0,255))
          for p in i.coords:
            output.write(str(p[0]) + ' ' + str(p[1]) + '\n')

# read all the points in from the file...
for i in pf:
  line = i.split(' ')
  x = float(line[0])
  y = float(line[1])
  x100 = int(x/100)
  y100 = int(y/100)
  ix = int(x/5)
  iy = int(y/5)
  ntype = line[2].strip()
  if (x100,y100) not in sectors:
    sectors[(x100,y100)] = {'1':[],'2':[]} 
  if (ix,iy) not in inhabited:
    inhabited[(ix,iy)] = 1
  
  if x % 5 < MAXSIZE:
    inhabited[(ix-1,iy)] = 1
    if y % 5 < MAXSIZE:
      inhabited[(ix-1,iy-1)] = 1
    if y % 5 > MAXSIZE:
      inhabited[(ix-1,iy+1)] = 1
  if x % 5 > MAXSIZE:
    inhabited[(ix+1,iy)] = 1
    if y % 5 < MAXSIZE:
      inhabited[(ix+1,iy-1)] = 1
    if y % 5 > MAXSIZE:
      inhabited[(ix+1,iy+1)] = 1
 
  if y % 5 < MAXSIZE:
    inhabited[(ix-1,iy)] = 1
  if y % 5 > MAXSIZE:
    inhabited[(ix+1,iy)] = 1

  sectors[(x100,y100)][ntype].append((x,y))

for s in sectors:
  print "sector --- " + str(s)
  # wide band = 1 narrow band = 2
  extent = (s[0]*100.0, s[1]*100.0, s[0]*100 + 100, s[1]*100+100)
  sectors[s]['1'] = buildsector(sectors[s]['1'],extent)
  sectors[s]['2'] = buildsector(sectors[s]['2'],extent)
  if sectors[s]['2']:
    s2expanded = sectors[s]['2'].buffer(3.0).simplify(2.0)
    if sectors[s]['1'] == None:
      sectors[s]['1'] = s2expanded
    else:
      sectors[s]['1'] = sectors[s]['1'].union(s2expanded)

deadsectors = [i for i in sectors if sectors[i]['1'] == None and sectors[i]['2'] == None]
for i in deadsectors:
  del sectors[i]
sectorkeys = sorted(sectors.iterkeys())

whole1 = sectors[sectorkeys[0]]['1']
whole2 = sectors[sectorkeys[0]]['2'] 
if whole1 == None:
  whole1 = MultiPolygon()
if whole2 == None:
  whole2 = MultiPolygon()

counter = 0
curx=0
curstrip1 = Polygon()
curstrip2 = Polygon()
for s in sectorkeys[1:]:
  if s[0] > curx:
    whole1 = whole1.union(curstrip1)
    whole2 = whole2.union(curstrip2)
    curx = s[0]
    curstrip1 = Polygon()
    curstrip2 = Polygon()

  print "-->" + str(s)
  if sectors[s]['1']:
    curstrip1 = curstrip1.union(sectors[s]['1'])
  if sectors[s]['2']:
    curstrip2 = curstrip2.union(sectors[s]['2'])
  #counter+=1
  #if counter > 100:
  #  break

whole1.buffer(1.0)
whole1.buffer(-.7)
whole1.simplify(.5)

whole2.buffer(1.0)
whole2.buffer(-.7)
whole2.simplify(.5)

# alright, we have the whole thing, write it to a file...
#writegeometry(whole1,(128,64,0))
#writegeometry(whole2,(255,128,0))

buildsquares(whole1,whole2)


testimage.save("testimage2.png","PNG")

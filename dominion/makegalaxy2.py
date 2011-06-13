import Image, ImageDraw
from PIL import *
from math import *
from random import *
from newdominion.dominion.models import *
from newdominion.dominion.starnames import starname
from quadtree import Quadtree

import subprocess
import os
from django.db import connection, transaction


gminx = 0
gminy = 0
gmaxx = 3000
gmaxy = 3000

testimage = Image.new('RGB',(gmaxx,gmaxy))
draw = ImageDraw.Draw(testimage)
povfile = open("stars.pov","w")
squares={}
numstars = 0
totalstars = 0
sectors = {}
planets = []

tree = Quadtree((gminx,gminy,gmaxx,gmaxy),maxdepth = 16)



def is_nan2(num):
  return str(num) == "nan"
  
def setsize(color):
  basesize = .05
  sizemods = {'blue': 2.0, 'red': .7, 'yellow': 1.0}

  size = basesize * sizemods[color]
  if color == 'red' and random.random() < .011:
    # red giant star
    size *= random.randint(4,5)
  elif color == 'blue' and random.random() < .011:
    # blue giant star
    size *= 2.0
  else: 
    # randomize the size a bit...
    size = size * (1+random.random()*.5-.25)

  if color == 'blue':
    adjust = random.randint(-20,10)
    blueadjust = abs(adjust/2)
    color = [190+adjust,220+adjust,255-blueadjust]
  elif color == 'yellow':
    adjust = random.randint(-20,10)
    color = [255,255,120+adjust]
  elif color == 'red':
    adjust = random.randint(-20,10)
    color = [255,150+adjust,150+adjust]
    if size > .06:
      color[1] += random.randint(20,25)
      color[2] += random.randint(20,25)
    
    
  return size, color
  

def genarmslice(rx,ry,rangle,width, height,location):
  if location > .98:
    #height = height * cos((location-.97)*pi*17)
    #height = height * cos((location-.96)*pi*12)
    height = height * cos((location-.95)*pi*10)
  area = width*height
  numstars = int(area/75)
  numclusters = int(area/1000)
  numredstars = int(area/25)
  rangle2 = rangle-(3.14159/2.0)
  
  if 1:
    for star in range(numredstars):
      for j in xrange(5):
        x = random.betavariate(1.2,1.2)*(height)
        y = random.uniform(0,width)
        # then transform/rotate to it's actual position
        x2 = (gmaxx/2) + rx + x*cos(rangle) - y*sin(rangle)
        y2 = (gmaxy/2) + ry + x*sin(rangle) + y*cos(rangle)
        if genpoint(x2,y2,'red',squares):
          break
     
  if 1:
    for cluster in range(numclusters):
      # find the center of the cluster in the slice
      centerx = random.betavariate(.8,5)*height
      centery = random.uniform(0,width)
      
      # then place it in the final coordinate system
      cx2 = (gmaxx/2) + rx + centerx*cos(rangle) - centery*sin(rangle)
      cy2 = (gmaxy/2) + ry + centerx*sin(rangle) + centery*cos(rangle)
      
      # randomly generate a size for the star cluster
      clusterwidth = random.betavariate(1,1.5)*(width*3)
      for i in range(int(clusterwidth)*2):
        for j in xrange(5):
          angle = random.random()*(2*pi)
          distance = random.betavariate(1,4)*clusterwidth
          x = cx2+(sin(angle) * distance)
          y = cy2+(cos(angle) * distance)
          if genpoint(x,y,'blue',squares):
            break
  if 1:
    for star in range(numstars):
      # first locate the star in the current slice
      # the first argument to betavariate dictates
      # how quickly the outside of the arm ramps up,
      # the second argument dictates how quickly the
      # inside ramps down.
      for j in xrange(5):
        x = random.betavariate(1.6,4)*height
        y = random.uniform(0,width)
        # then transform/rotate to it's actual position
        x2 = (gmaxx/2) + rx + x*cos(rangle) - y*sin(rangle)
        y2 = (gmaxy/2) + ry + x*sin(rangle) + y*cos(rangle)
        if genpoint(x2,y2,'blue',squares):
          break
  
def genarm(start, end, angle, squares):
  angle +=pi/4.0
  step = 1/35.0
  scale = 1.18
  prevrx = 0.0
  prevry = 0.0
  for i in range(start,end):
    j = i*step 
    #armwidth = pow(scale*((i-start)*step*2.5),1.6)
    ratio = .306349

    # find our current (unrotated) xy
    x = pow((scale*e), ratio*j) * cos(j) 
    y = pow((scale*e), ratio*j) * sin(j) 

    # rotate arm by angle from argument 
    # (for doing multiple arms...)
    rx = x*cos(angle) - y*sin(angle)
    ry = x*sin(angle) + y*cos(angle)
    
    genpoint(rx+(gmaxx/2),ry+(gmaxy/2),'blue',squares)
    
    if prevrx != 0.0:
      # rangle = right angle (normal) from the arc at the current point
      rangle = atan2(ry,rx)+pi
      # width is the distance between the current point and previous
      # points on the arm
      width = sqrt(pow(rx-prevrx,2)+pow(ry-prevry,2))
      # height is how wide the arm is at this point
      height = pow((i-start),1.03)
      # location is how far along this arm we are
      location = (float(i-start))/(float(end-start))
      genarmslice(rx,ry,rangle,width,height,location)
      #draw.line([rx+1000,ry+1000,
      #          rx+1000+cos(rangle)*height,
      #          ry+1000+sin(rangle)*height],
      #          tuple([255,0,0]))

    prevrx = rx
    prevry = ry


def genpoint(x,y,color,squares):
  global numstars
  global totalstars
  global sectors
  global povfile
  global tree
  curx = x
  cury = y

  sectorkey = buildsectorkey(x,y)
  cur5x = int(curx/5.0)
  cur5y = int(cury/5.0)

  radius, color = setsize(color)

  bounds = (curx-radius-.18,cury-radius-.18,
            curx+radius+.18,cury+radius+.18)

  intersects = tree.likely_intersection(bounds)
  for i in intersects:
    p = planets[i]
    if getdistance(curx,cury,p[0],p[1]) < radius+p[2]+.36:
      return 0



  if 1: 
    if sectorkey not in sectors:
      sectors[sectorkey] = [str(sectorkey), str(int(curx)), str(int(cury))]

    cursector = sectors[sectorkey]
    if color[0] > 255:
      color[0] = 255
    if color[1] > 255:
      color[1] = 255
    if color[2] > 255:
      color[2] = 255
    intcolor = (color[0]<<16) + (color[1]<<8) + (color[2])
    planet = [curx, cury, radius, 
              sectorkey, intcolor, 
              starname(), 
              1, 0.0,0.0,
              'false','false','false']
    tree.add(len(planets),bounds)
    planets.append(planet)

  """
  numstars += 1
  if numstars % 100 == 0:
    print str(numstars)
  """
  totalstars += 1
  #povstar = "sphere{<%f,%f,0>, %f texture {pigment { color rgb <%f, %f, %f>}}}\n"
  #povfile.write(povstar % (curx,cury,radius,color[0],color[1],color[2]))

  r50 = radius*5
  draw.ellipse([curx-r50,cury-r50,curx+r50,cury+r50],tuple(color))
  return 1





while 1:
  random.seed()

  if 1:
    yellow = 255
    for i in xrange(1,200000):
      for j in xrange(5):
        angle = random.random()*(2*pi)
        distance = random.betavariate(1,30)*4800
        x = (gmaxx/2) + (sin(angle) * distance)
        y = (gmaxy/2) + (cos(angle) * distance)
        color = [yellow, yellow, 128]
        if genpoint(x,y,'yellow',squares):
          break

  if 1:
    genarm(300,690,0,squares)
    genarm(300,680,3.14159,squares)

    genarm(460,710,(3.14159/2.0)+3.14159+.3,squares)
    genarm(460,720,(3.14159/2.0)+.1,squares)
    
    for i in range(8):
      start = random.randint(250,400)
      end = start + random.randint(80,250)
      genarm(start,end,random.random()*(2.0*3.14159),squares)
    
    for i in range(24):
      start = random.randint(580,620)
      end = start + random.randint(30,90)
      genarm(start,end,random.random()*(2.0*3.14159),squares)

  testimage.save("testimage.png","PNG")
  os.system('eog testimage.png')

  print "total = " + str(totalstars)
  print "like this one? --> "
  #  pid = subprocess.Popen(["eog", "testimagesmall.png"]).pid

  input = raw_input("-->")



  #os.system('kill ' + str(pid))
  cursor = connection.cursor()
  cursor.execute('delete from dominion_sector;')
  cursor.execute('delete from dominion_player;')
  cursor.execute('delete from dominion_planet;')
  cursor.execute('delete from dominion_fleet;')
  cursor.execute('delete from dominion_fleet_inviewof;')
  cursor.execute('delete from dominion_fleet_inviewoffleet;')
  cursor.execute('delete from dominion_instrumentality;')
  cursor.execute('delete from dominion_manifest;')
  cursor.execute('delete from dominion_planet_connections;')
  cursor.execute('delete from dominion_planetattribute;')
  cursor.execute('delete from dominion_planetupgrade;')
  cursor.execute('delete from dominion_playerattribute;')
  cursor.execute('delete from dominion_upgradeattribute;')

  if input in ['y','Y','yes','YES']:
    sectors = [sectors[x] for x in sectors]

    insertrows('dominion_sector',
               ('key','x','y'),
               sectors)
    print "------"
    planets2 = []
    for i in xrange(len(planets)):
      p = planets.pop()
      arr = [str(i) for i in p]
      planets2.append(arr)
    planets = []
    insertrows('dominion_planet',
               ('x','y','r','sector_id','color','name','society',
                'tariffrate','inctaxrate','openshipyard',
                'opencommodities','opentrade'),
               planets2)
    break
  break















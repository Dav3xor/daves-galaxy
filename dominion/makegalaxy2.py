import Image, ImageDraw
from PIL import *
from math import *
from random import *
from newdominion.dominion.models import *
from newdominion.dominion.starnames import starname
import subprocess
import os

testimage = Image.new('RGB',(2000,2000))
draw = ImageDraw.Draw(testimage)
povfile = open("stars.pov","w")
squares={}
numstars = 0
sectors = {}

largest = -100000000
smallest = 100000000


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
  
def genarmold(start, end, angle, squares):
  step = 1/65.0
  for i in range(start,end):
    j = i*step
    distance = pow(j,1.02) * 95.0 
    angle2 = angle+j
    
    x = (distance)*cos(angle2)
    y = (distance)*sin(angle2)
    genpoint(x,y,[255,255,255],squares)
    #draw.line([x+1000,y+1000,
    #          x+1000+cos(angle2)*(distance/4),
    #          y+1000+sin(angle2)*(distance/4)],
    #          tuple([255,0,0]))

def genarmslice(rx,ry,rangle,width, height,location):
  if location > .98:
    #height = height * cos((location-.97)*pi*17)
    #height = height * cos((location-.96)*pi*12)
    height = height * cos((location-.95)*pi*10)
  area = width*height
  numstars = int(area/30)
  numclusters = int(area/400)
  numredstars = int(area/20)
  rangle2 = rangle-(3.14159/2.0)
  if 1:
    for cluster in range(numclusters):
      # find the center of the cluster in the slice
      centerx = random.betavariate(1,5)*height
      centery = random.uniform(0,width)
      
      # then place it in the final coordinate system
      cx2 = 1000 + rx + centerx*cos(rangle) - centery*sin(rangle)
      cy2 = 1000 + ry + centerx*sin(rangle) + centery*cos(rangle)
      
      # randomly generate a size for the star cluster
      clusterwidth = random.betavariate(2,5)*(width*3)
      for i in range(int(clusterwidth)*3):
        angle = random.random()*(2*pi)
        distance = random.betavariate(1,4)*clusterwidth
        x = cx2+(sin(angle) * distance)
        y = cy2+(cos(angle) * distance)
        genpoint(x,y,'blue',squares)
        #draw.ellipse([x-.5,y-.5,x+.5,y+.5],tuple([240,240,255]))
  if 1:
    for star in range(numstars):
      # first locate the star in the current slice
      # the first argument to betavariate dictates
      # how quickly the outside of the arm ramps up,
      # the second argument dictates how quickly the
      # inside ramps down.
      x = random.betavariate(2,4)*height
      y = random.uniform(0,width)
      # then transform/rotate to it's actual position
      x2 = 1000 + rx + x*cos(rangle) - y*sin(rangle)
      y2 = 1000 + ry + x*sin(rangle) + y*cos(rangle)
      genpoint(x2,y2,'blue',squares)
      #draw.ellipse([x2-.5,y2-.5,x2+.5,y2+.5],tuple([240,240,255]))
  if 1:
    for star in range(numredstars):
      x = random.betavariate(1.5,1)*(height)
      y = random.uniform(0,width)
      # then transform/rotate to it's actual position
      x2 = 1000 + rx + x*cos(rangle) - y*sin(rangle)
      y2 = 1000 + ry + x*sin(rangle) + y*cos(rangle)
      #draw.ellipse([x2-.2,y2-.2,x2+.2,y2+.2],tuple([240,192,128]))
      genpoint(x2,y2,'red',squares)
      #draw.ellipse([x2-.2,y2-.2,x2+.2,y2+.2],tuple([255,128,128]))
     
  #draw.line([rx+1000,ry+1000,
  #          rx+1000+cos(rangle)*height,
  #          ry+1000+sin(rangle)*height],
  #          tuple([255,0,0]))
  
def genarm(start, end, angle, squares):
  angle +=pi/4.0
  step = 1/35.0
  scale = 1.13
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
    
    #genpoint(rx,ry,[255,255,255],squares)
    
    if prevrx != 0.0:
      # rangle = right angle (normal) from the arc at the current point
      #rangle = atan2(ry-prevry,rx-prevrx) + 3.14159/2.0
      rangle = atan2(ry,rx)+pi
      # width is the distance between the current point and previous
      # points on the arm
      width = sqrt(pow(rx-prevrx,2)+pow(ry-prevry,2))
      # height is how wide the arm is at this point
      height = pow((i-start),1.04)
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
  global sectors
  global povfile
  curx = x
  cury = y

  sectorkey = buildsectorkey(x,y)
  cur5x = int(curx/5.0)
  cur5y = int(cury/5.0)

  radius, color = setsize(color)

  if 0: 
    if sectorkey not in sectors:
      newsector = Sector(key=sectorkey, x=int(curx), y=int(cury))
      newsector.save()
      sectors[sectorkey] = newsector

    cursector = sectors[sectorkey]
    if color[0] > 255:
      color[0] = 255
    if color[1] > 255:
      color[1] = 255
    if color[2] > 255:
      color[2] = 255
    intcolor = (color[0]<<16) + (color[1]<<8) + (color[2])
    planet = Planet(x=curx,y=cury, r=radius, sector=cursector)
    planet.color = intcolor
    planet.name = starname()
    planet.society = 1
    planet.save()

  numstars += 1
  if numstars % 100 == 0:
    print str(numstars)

  povstar = "sphere{<%f,%f,0>, %f texture {pigment { color rgb <%f, %f, %f>}}}"
  povfile.write(povstar % (curx,cury,radius,color[0],color[1],color[2]))

  r50 = radius*10
  draw.ellipse([curx-r50,cury-r50,curx+r50,cury+r50],tuple(color))

while 1:
  random.seed()

  if 1:
    yellow = 255
    for i in range(1,200000):
      angle = random.random()*(2*pi)
      #distance = (1-random.lognormvariate(0.0,.1))*1000
      distance = random.betavariate(1,30)*4000
      #distance = pow(random.random()*70,1.4+random.random()*.2)
      x = 1000 + (sin(angle) * distance)
      y = 1000 + (cos(angle) * distance)
      color = [yellow, yellow, 128]
      genpoint(x,y,'yellow',squares)
      #draw.ellipse([x-.5,y-.5,x+.5,y+.5],tuple([255,255,180]))

  # draw the blue star ring around the center...
  if 0:
    for i in range(1,50000):
      angle = random.random()*(2*pi)
      distance = random.betavariate(85,95)*800
      x = 1000+(sin(angle) * distance)
      y = 1000+(cos(angle) * distance)
      color = [230, 230, 255]
      genpoint(x,y,'blue',squares)
      #draw.ellipse([x-.5,y-.5,x+.5,y+.5],tuple([240,240,255]))
  if 0:
    for cluster in range(700):
      angle = random.random()*(2*pi)
      #distance = random.betavariate(2,2)*200
      distance = random.betavariate(8,3)*220
      # then place it in the final coordinate system
      cx = 1000 + (sin(angle) * distance)
      cy = 1000 + (cos(angle) * distance)
      
      clusterwidth = random.betavariate(2,5)*(80)
      for i in range(int(clusterwidth)*10):
        angle = random.random()*(2*pi)
        distance = random.betavariate(1,5)*clusterwidth
        x = cx+(sin(angle) * distance)
        y = cy+(cos(angle) * distance)
        genpoint(x,y,'blue',squares)
        #draw.ellipse([x-.5,y-.5,x+.5,y+.5],tuple([240,240,255]))
  if 1:
    genarm(500,700,0,squares)
    genarm(500,700,3.14159,squares)

    genarm(460,690,(3.14159/2.0)+3.14159,squares)
    genarm(460,690,(3.14159/2.0),squares)


    for i in range(8):
      genarm(random.randint(520,600),
             random.randint(650,690),
             (3.14159/8.0)+i*(pi/4.0),squares)
           
    

  testimage.save("testimage.png","PNG")
  print "like this one? --> "
  #  pid = subprocess.Popen(["eog", "testimagesmall.png"]).pid

  input = raw_input("-->")
  #os.system('kill ' + str(pid))
  if input in ['y','Y','yes','YES']:
    break
  break

print "200,200 = " + str(len(squares[(200,200)])) + "stars..."
print "numstars = " + str(numstars)
print "smallest = " + str(smallest)
print "largest = " + str(largest)

if 0:
  for key in squares.keys():
    intkey = key[0]*1000+key[1]
    #print str(key) + " " + str(intkey) + ", "+ str(len(squares[key])) + " stars"
    print str(key)
    cursector = Sector(x=key[0], y=key[1], key=intkey)
    cursector.save()
    for star in squares[key]:
      if star['color'][0] > 255:
        star['color'][0] = 255
      if star['color'][1] > 255:
        star['color'][1] = 255
      if star['color'][2] > 255:
        star['color'][2] = 255
      intcolor = (star['color'][0]<<16) + (star['color'][1]<<8) + (star['color'][2])
      planet = Planet(x=star['x'],y=star['y'], r=star['radius'], sector=cursector)
      planet.color = intcolor
      planet.name = "X"
      planet.agriculture = 1
      planet.metals = 1
      planet.industry = 1
      planet.society = 1
      planet.population = 1
      planet.save()













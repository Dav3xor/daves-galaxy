import Image, ImageDraw
from PIL import *
from math import *
from random import *
from newdominion.dominion.models import *
import subprocess
import os

testimage = Image.new('RGB',(2000,2000))
draw = ImageDraw.Draw(testimage)
squares={}
numstars = 0

largest = -100000000
smallest = 100000000


def is_nan2(num):
  return str(num) == "nan"
  
def setsize(color):
  # ok, determine the size of a star by color:
  # green == baseline size
  # red   == the more red, the smaller the star..
  # blue  == the more blue, the larger the star
  global largest
  global smallest
  # (255,255,255) = 64*2 + 64 + 64*5
  intensity = ((color[0]-192)+(color[1]-192)+(color[2]-192))/3

  # make it bigger if the predominant color is blue 
  if color[2]>color[0] and color[2]>color[1]:
    intensity*=2.0
  # and make it smaller if the predominant color is red
  if color[0]>color[1] and color[0]>color[2]:
    intensity/=1.2


  if random.random() > .9:
    if color[0] > color[2] and color[0] > color[1]:
      # make some red giants...
      intensity *= 3.0
    if color[2] > color[0] and color[2] > color[1]:
      # and some blue giants
      intensity *= 2.0 


  size = .01 + intensity/3200.0 + random.random()*.01
  if size < smallest:
    smallest = size
  if size > largest:
    largest = size
  return size
  
def genarm(angle,squares):
  x=0
  y=0
  prevx=0
  prevy=0



  for i in range(1,500):
    j = i/50.0
    #red stars

    x = (pow(i,1.02))*cos(j+angle+.7)
    y = (pow(i,1.02))*sin(j+angle+.1)
    for k in range(0,int(250 -(250-i/2))):
      dist = pow(random.random()*.8,1.5)
      angle = atan2(x-prevx,y-prevy) + random.random()*1.5
      xdist = sin(angle)*dist
      ydist = cos(angle)*dist
      avdist = (xdist+ydist)/2.0
      color = [int(223+(32-(avdist*50.0))),192,192]
      xdist *= i;
      ydist *= i;
      genpoint(x+xdist,y+ydist,color,squares)

    #yellow stars
    x = (pow(i,1.02))*cos(j+angle+.2)
    y = (pow(i,1.02))*sin(j+angle+.2)
    for k in range(0,int(200-i/2)):
      xdist = pow((random.random()*.9)/1.2,1.8)
      ydist = pow((random.random()*.9)/1.2,1.8)
      avdist = (xdist+ydist)/2
      color = [255,255,int(128+(64-(avdist*308.8)))]
      xdist *= i;
      ydist *= i;
      genpoint(x+xdist,y+ydist,color,squares)


    #blue stars
    x = (pow(i,1.02))*cos(j+angle)
    y = (pow(i,1.02))*sin(j+angle)
    for k in range(0,int(25-i/20)):
      xdist = pow((random.random()*.35)/1.2,1.5)
      ydist = pow((random.random()*.2)/1.2,1.5)
      avdist = (xdist+ydist)/2
      color = [int(150+(64-(avdist*117.5))),int(150+(64-(avdist*117.5))),255]
      xdist *= i;
      ydist *= i;
      genpoint(x+xdist,y+ydist,color,squares)
    prevx = x
    prevy = y

def genpoint(x,y,color,squares):
  global numstars
  curx = x+1000.0
  cury = y+1000.0
  cur5x = int(curx/5.0)
  cur5y = int(cury/5.0)

  radius = setsize(color)

  intkey = cur5x*1000+cur5y
  #Entry.objects.filter(headline__contains='Lennon').count()
  cursector = 0
  if Sector.objects.filter(key=intkey).count() == 0: 
    cursector = Sector(x=cur5x, y=cur5y, key=intkey)
    cursector.save()
  else:
    cursector = Sector.objects.get(key=intkey)
  if color[0] > 255:
    color[0] = 255
  if color[1] > 255:
    color[1] = 255
  if color[2] > 255:
    color[2] = 255
  intcolor = (color[0]<<16) + (color[1]<<8) + (color[2])
  planet = Planet(x=curx,y=cury, r=radius, sector=cursector)
  planet.color = intcolor
  planet.name = "X"
  planet.agriculture = 1
  planet.metals = 1
  planet.industry = 1
  planet.society = 1
  planet.population = 1
  planet.save()

  #if not squares.has_key((cur5x,cur5y)):
  #  squares[(cur5x,cur5y)] = []
  #squares[(cur5x,cur5y)].append({'x':curx,'y':cury,'radius':radius, 'color':(color)})
  numstars += 1
  if numstars % 100 == 0:
    print str(numstars)
  r50 = radius*20.0
  draw.ellipse([curx-r50,cury-r50,curx+r50,cury+r50],tuple(color))

while 1:
  genarm(3.14159/2+1.0,squares)
  genarm(3.14159+3.14159/2+1,squares)

  for i in range(1,70000):
    expval = 1
    angle = random.random()*(2*3.14159)
    #distance = exp(random()*4)*5- 5
    distance = pow(random.random()*50,1.4+random.random()*.2)
    x = (sin(angle) * distance)
    y = (cos(angle) * distance)
    color = [255 - int(distance/5.0), 255-int(distance/5.0),255]
    genpoint(x,y,color,squares)

  #print squares

    

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













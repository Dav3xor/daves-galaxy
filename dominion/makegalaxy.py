import Image, ImageDraw
from PIL import *
from math import *
from random import *
from newdominion.dominion.models import *

testimage = Image.new('RGB',(2000,2000))
draw = ImageDraw.Draw(testimage)
squares={}
numstars = 0
def is_nan2(num):
  return str(num) == "nan"
  
def setsize(color):
  # ok, determine the size of a star by color:
  # green == baseline size
  # red   == the more red, the smaller the star..
  # blue  == the more blue, the larger the star

  # (255,255,255) = 64*2 + 64 + 64*5
  intensity = ((color[0]-192)+(color[1]-192)+(color[2]-192))/3

  # make it bigger if the predominant color is blue 
  if color[2]>color[0] and color[2]>color[1]:
    intensity*=2.5
  # and make it smaller if the predominant color is red
  if color[0]>color[1] and color[0]>color[2]:
    intensity/=1.5

  size = .01 + intensity/3200.0
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
      dist = pow(random()*.8,1.5)
      angle = atan2(x-prevx,y-prevy) + random()*1.5
      xdist = sin(angle)*dist
      ydist = cos(angle)*dist
      avdist = (xdist+ydist)/2.0
      color = [int(223+(32-(avdist*50.0))),192,192]
      xdist *= i;
      ydist *= i;
      genpoint(x,y,xdist,ydist,color,squares)

    #yellow stars
    x = (pow(i,1.02))*cos(j+angle+.2)
    y = (pow(i,1.02))*sin(j+angle+.2)
    for k in range(0,int(200-i/2)):
      xdist = pow((random()*.9)/1.2,1.8)
      ydist = pow((random()*.9)/1.2,1.8)
      avdist = (xdist+ydist)/2
      color = [255,255,int(128+(64-(avdist*308.8)))]
      xdist *= i;
      ydist *= i;
      genpoint(x,y,xdist,ydist,color,squares)


    #blue stars
    x = (pow(i,1.02))*cos(j+angle)
    y = (pow(i,1.02))*sin(j+angle)
    for k in range(0,int(25-i/20)):
      xdist = pow((random()*.35)/1.2,1.5)
      ydist = pow((random()*.2)/1.2,1.5)
      avdist = (xdist+ydist)/2
      color = [int(150+(64-(avdist*117.5))),int(150+(64-(avdist*117.5))),255]
      xdist *= i;
      ydist *= i;
      genpoint(x,y,xdist,ydist,color,squares)
    prevx = x
    prevy = y


def genpoint(x,y,xdist,ydist,color,squares):
  global numstars
  curx = x+1000.0+xdist
  cury = y+1000.0+ydist
  cur5x = int(curx/5.0)
  cur5y = int(cury/5.0)

  radius = setsize(color)
  r50 = radius*50.0

  draw.ellipse((curx-r50,cury-r50,curx+r50,cury+r50),tuple(color))
  if not squares.has_key((cur5x,cur5y)):
    squares[(cur5x,cur5y)] = []
  squares[(cur5x,cur5y)].append({'x':curx,'y':cury,'radius':radius, 'color':(color)})
  numstars += 1



genarm(3.14159/2+1.0,squares)
genarm(3.14159+3.14159/2+1,squares)
#print squares


for i in range(1,70000):
  expval = 1
  angle = random()*(2*3.14159)
  #distance = exp(random()*4)*5- 5
  distance = pow(random()*110,1+random()*.3)
  x = 1000 + (sin(angle) * distance)
  y = 1000 + (cos(angle) * distance)
  cur5x = int(x)/5
  cur5y = int(y)/5
  if not squares.has_key((cur5x,cur5y)):
    squares[(cur5x,cur5y)] = []
  color = 255 - int((distance/901)*400)
  radius = setsize((color,color,255))
  r50 = radius *50.0
  squares[(cur5x,cur5y)].append({'x':x,'y':y,'radius':radius, 'color':[color,color,255]})
  numstars += 1
  draw.ellipse((x-r50,y-r50,x+r50,y+r50),(color,color,255))
  #draw.point((x,y),(color,color,255))
  

testimage.save("testimage.png","PNG")
testimage = testimage.resize((500,500),Image.ANTIALIAS)
testimage.save("testimagesmall.png","PNG")

print "200,200 = " + str(len(squares[(200,200)])) + "stars..."
print "numstars = " + str(numstars)

if 0:
  for key in squares.keys():
    intkey = key[0]*1000+key[1]
    print str(key) + " " + str(intkey) + ", "+ str(len(squares[key])) + " stars"
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













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
  height2 = height
  if location > .95:
    height = height * cos((location-.95)*pi*10)
  if location > .8:
    height2 = height * cos((location-.8)*pi*2.5)
  area = width*height
  numstars = int(area/60)
  numclusters = int(area/500)
  numredstars = int(area/30)
  rangle2 = rangle-(3.14159/2.0)
  if 1:
    for cluster in range(numclusters):
      # find the center of the cluster in the slice
      centerx = random.betavariate(2,12)*height2
      centery = random.uniform(0,width)
      
      # then place it in the final coordinate system
      cx2 = 1000 + rx + centerx*cos(rangle) - centery*sin(rangle)
      cy2 = 1000 + ry + centerx*sin(rangle) + centery*cos(rangle)
      
      clusterwidth = random.betavariate(2,5)*(height/3)
      for i in range(int(clusterwidth)*5):
        angle = random.random()*(2*pi)
        distance = random.betavariate(1,5)*clusterwidth
        x = cx2+(sin(angle) * distance)
        y = cy2+(cos(angle) * distance)
        draw.ellipse([x-.5,y-.5,x+.5,y+.5],tuple([240,240,255]))
  if 1:
    for star in range(numstars):
      # first locate the star in the current slice
      # the first argument to betavariate dictates
      # how quickly the outside of the arm ramps up,
      # the second argument dictates how quickly the
      # inside ramps down.
      x = random.betavariate(2,6)*height2
      y = random.uniform(0,width)
      # then transform/rotate to it's actual position
      x2 = 1000 + rx + x*cos(rangle) - y*sin(rangle)
      y2 = 1000 + ry + x*sin(rangle) + y*cos(rangle)
      draw.ellipse([x2-.5,y2-.5,x2+.5,y2+.5],tuple([240,240,255]))
  if 1:
    for star in range(numredstars):
      x = random.betavariate(1,1)*(height2/1.5)
      y = random.uniform(0,width)
      # then transform/rotate to it's actual position
      x2 = 1000 + rx + x*cos(rangle) - y*sin(rangle)
      y2 = 1000 + ry + x*sin(rangle) + y*cos(rangle)
      #draw.ellipse([x2-.2,y2-.2,x2+.2,y2+.2],tuple([240,192,128]))
      draw.ellipse([x2-.2,y2-.2,x2+.2,y2+.2],tuple([255,128,128]))
     
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
      rangle = atan2(ry-prevry,rx-prevrx) + 3.14159/2.0
      # width is the distance between the current point and previous
      # points on the arm
      width = sqrt(pow(rx-prevrx,2)+pow(ry-prevry,2))
      # height is how wide the arm is at this point
      height = pow((i-start),1.18)
      # location is how far along this arm we are
      location = (float(i-start))/(float(end-start))
      genarmslice(rx,ry,rangle,width,height,location)

    prevrx = rx
    prevry = ry


def genpoint(x,y,color,squares):
  global numstars
  curx = x+1000.0
  cury = y+1000.0
  cur5x = int(curx/5.0)
  cur5y = int(cury/5.0)

  radius = setsize(color)

  intkey = cur5x*1000+cur5y
  
  if 0:
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
  r50 = radius*50.0
  draw.ellipse([curx-r50,cury-r50,curx+r50,cury+r50],tuple(color))

while 1:
  random.seed()

  if 1:
    yellow = 255
    for i in range(1,70000):
      angle = random.random()*(2*pi)
      #distance = (1-random.lognormvariate(0.0,.1))*1000
      distance = pow(random.random()*70,1.4+random.random()*.2)
      x = 1000 + (sin(angle) * distance)
      y = 1000 + (cos(angle) * distance)
      color = [yellow, yellow, 128]
      draw.ellipse([x-.5,y-.5,x+.5,y+.5],tuple([255,255,180]))

  # draw the blue star ring around the center...
  if 0:
    for i in range(1,50000):
      angle = random.random()*(2*pi)
      distance = random.betavariate(85,95)*800
      x = 1000+(sin(angle) * distance)
      y = 1000+(cos(angle) * distance)
      color = [230, 230, 255]
      draw.ellipse([x-.5,y-.5,x+.5,y+.5],tuple([240,240,255]))
  if 1:
    for cluster in range(900):
      angle = random.random()*(2*pi)
      #distance = random.betavariate(2,2)*200
      distance = random.betavariate(11,3)*220
      # then place it in the final coordinate system
      cx = 1000 + (sin(angle) * distance)
      cy = 1000 + (cos(angle) * distance)
      
      clusterwidth = random.betavariate(2,5)*(80)
      for i in range(int(clusterwidth)*10):
        angle = random.random()*(2*pi)
        distance = random.betavariate(1,5)*clusterwidth
        x = cx+(sin(angle) * distance)
        y = cy+(cos(angle) * distance)
        draw.ellipse([x-.5,y-.5,x+.5,y+.5],tuple([240,240,255]))
  if 1:
    genarm(520,700,0,squares)
    genarm(520,700,3.14159,squares)

    genarm(460,690,(3.14159/2.0)+3.14159,squares)
    genarm(460,690,(3.14159/2.0),squares)


    for i in range(8):
      genarm(random.randint(520,540),
             random.randint(650,680),
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













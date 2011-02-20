from random import *
from math import *
from PIL import Image,ImageDraw

img = Image.new("RGB",(100,100),(0,0,0))
draw = ImageDraw.Draw(img)

for i in xrange(50):
  x = random()
  y = ((x*x*x)*10)
  print str(int(y))
  draw.point((x*10,y),(255,255,255))
img.save('blah.png')

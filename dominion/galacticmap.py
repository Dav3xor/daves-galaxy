from PIL import Image, ImageDraw


from newdominion.dominion.models import *
import newdominion.settings


im = Image.open(newdominion.settings.GALAXY_MAP_LOCATION)
im2 = Image.new('RGB',(3000,3000),'black')
draw = ImageDraw.Draw(im2)

sectors = inhabitedsectors()

for s in sectors:
  red = 0
  blue = 0
  green = 0
  planets = Planet.objects.filter(sector=s).exclude(owner=None).values('owner__player__color')
  numplanets = planets.count()
  for p in planets:
    color = p['owner__player__color']
    red   += int(color[1:3],16)
    green += int(color[3:5],16)
    blue  += int(color[5:7],16)
  red = hex(red/numplanets)[2:]
  green = hex(green/numplanets)[2:]
  blue = hex(blue/numplanets)[2:]
  if len(red) == 1:
    red = "0" + red
  if len(green) == 1:
    green = "0" + green
  if len(blue) == 1:
    blue = "0" + blue
  color = "#"+red+green+blue
  #print color + "," + str(red) + "," + str(blue) + "," + str(green)
    
  p = Point((s/1000*5),((s%1000)*5))
  draw.rectangle([p.x,p.y,p.x+5,p.y+5], fill=color)

im3 = Image.blend(im,im2,.5)
im3.save(newdominion.settings.GALAXY_MAP_OUTPUT,'PNG')


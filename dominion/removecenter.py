from newdominion.dominion.models import *

xrange = [196,197,198,199,200,201,202,203,204]
yrange = [196,197,198,199,200,201,202,203,204]

for x in xrange:
  for y in yrange:
    remplanets = []
    skey = str(x*1000+y)
    sector = Sector.objects.get(key=skey)
    for planet in sector.planet_set.all():
      if getdistance(planet.x,planet.y,1000,1000) < 20.0:
        remplanets.append(planet)
    for planet in remplanets:
      planet.delete()
      

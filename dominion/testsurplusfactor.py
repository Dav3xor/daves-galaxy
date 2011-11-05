from newdominion.dominion.models import *

planets = Planet.objects.exclude(owner=None)

avg = 0
max = 0
numavg = 0
for p in planets:
  people = p.resources.people
  for key in productionrates:
    if key in ['quatloos','people']:
      continue
    onhand = getattr(p.resources, key)
    surplusfactor = 0
    if people != 0:
      surplusfactor = float(onhand)/float(people) * 1000.0
    
    print "people=" + str(people) + " onhand=" + str(onhand) + " sf=" + str(surplusfactor)
    avg += surplusfactor
    if surplusfactor > max:
      max = surplusfactor
    numavg += 1
print "avg = " + str(avg/numavg)
print "max = " + str(max)


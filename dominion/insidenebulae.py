from newdominion.dominion.models import *

for s in Sector.objects.exclude(nebulae=''):
  neb = simplejson.loads(s.nebulae)
  for p in s.planet_set.all():
    for i in neb['1']:
      poly = [(i[0][j],i[0][j+1]) for j in xrange(0,len(i[0]),2)]
      if point_in_poly(p.x,p.y,poly):
        p.innebulae = True
        p.save()
        print "x"
      else:
        print "."

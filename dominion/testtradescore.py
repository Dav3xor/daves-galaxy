from newdominion.dominion.models import *

f = Fleet.objects.get(id=40044)
plist = nearbysortedthings(Planet.objects.filter(owner__isnull=False,
                                                 resources__isnull=False,
                                                 resources__people__gt=0),f)[1:]

for i in plist:
  distance = getdistanceobj(f,i)
  score = i.tradescore(f, ['people','quatloos'], f.destination,{})
  society = i.society
  print "s=%d\td=%2.2f\tscore=%2.2f\tc=%s" % (society,distance,score[0],score[1])

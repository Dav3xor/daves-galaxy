from newdominion.dominion.models import *

f = Fleet.objects.filter(disposition=11, route__isnull=False)
for i in f:
  planet = i.route.nextplanet(i.curleg)
  if planet and not i.destination:
    print i.route
    i.destination = planet
    i.save()

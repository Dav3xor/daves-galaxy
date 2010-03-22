from newdominion.dominion.models import *
import datetime

staleplayers = []

if 1:
  u = User(username="StaleTest")
  p = Player(user=u)
  pl = Planet.objects.get(id=1235)
  pl.owner = u
  pl.populate()
  pl.save()
  staleplayers = Player.objects.get(username="StaleTest")

staleplayers = Player.objects.filter(lastactivity__lt = 
                                      (datetime.datetime.today()-datetime.timedelta(days=30))).exclude(
                                       user__username__in = ['harj','Bob','PopeKetrick'])

for player in staleplayers:
  for f in player.user.fleet_set.all():
    f.delete()
  for p in player.user.planet_set.all():
    # we want to keep the planet, so things get tricky...
    r = p.resources
    r.planet_set.clear()
    r.delete()
    p.planetattribute_set.clear()
    p.planetattribute_set.delete()
    p.planetupgrade_set.clear()
    p.planetupgrade_set.delete()
    p.owner = None:
    p.save()
  player.owner.delete()
  player.delete()

deleteusers = User.objects.filter(player__lastactivity__lt = (datetime.datetime.today()-datetime.timedelta(days=15)))

print str(deleteusers)



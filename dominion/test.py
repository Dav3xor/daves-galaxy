#!/usr/bin/python

from newdominion.dominion.models import *
from newdominion.dominion.doturn import *
from newdominion.dominion.menus import *
from newdominion.dominion.doturn import *

if Player.objects.count() == 0:
  u = User.objects.get(id=1)
  p = Player(user=u)
  p.save()
  pl = Planet.objects.get(id=10000)
  pl.owner = u
  pl.save()

try:
  u1 = User.objects.get(username="User1")
  p1 = Player.objects.get(user=u1)
  p1.delete()
  u1.delete()

  u2 = User.objects.get(username="User2")
  p2 = Player.objects.get(user=u2)
  p2.delete()
  u2.delete()
except:
  print "test users don't exist (a good thing)"

# create two test players
u1 = User(username="User1")
u1.save()
u2 = User(username="User2")
u2.save()

p1 = Player(user=u1)
p2 = Player(user=u2)

p1.save()
p2.save()

p1.setpoliticalrelation(p2,"friend")
if p2 in p1.friends.all():
  print "p2 is p1's friend (success)"
if p2 in p1.enemies.all():
  print "p2 is p1's enemy (failure)"


if p1 in p2.friends.all():
  print "p1 is p2's friend (success)"
if p1 in p2.enemies.all():
  print "p1 is p2's enemy (failure)"

p1.create()
p2.create()

f1 = Fleet(owner=u1, cruisers=5, destroyers=2)
f2 = Fleet(owner=u2, cruisers=4, destroyers=6)

f1.newfleetsetup(u1.planet_set.all()[0])
f2.newfleetsetup(u2.planet_set.all()[0])

doencounter(f1,f2)

p1.setpoliticalrelation(p2,"enemy")
p1.save()
p2.save()

f1.x = f2.x + .1
f1.y = f2.y + .1
doencounter(f1,f2)
#f1.save()
#f2.save()


if u1.planet_set.count() > 0:
  print "u1 has a planet (success)"
else:
  print "u1 has no planet (failure)"

if u2.planet_set.count() > 0:
  print "u2 has a planet (success)"
else:
  print "u2 has no planet (failure)"



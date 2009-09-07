#!/usr/bin/python

from newdominion.dominion.models import *
from newdominion.dominion.doturn import *
from newdominion.dominion.menus import *
from newdominion.dominion.doturn import *

def testfleets(u1,u2):
  f1 = Fleet(owner=u1)
  f2 = Fleet(owner=u2)

  # these both should fail because cruisers aren't buildable
  # for new players...
  try:
    f1.newfleetsetup(u1.planet_set.all()[0],{'cruisers':5, 'destroyers':2})
    f2.newfleetsetup(u2.planet_set.all()[0],{'cruisers':4, 'destroyers':6})
    exit();
  except:
    print "can't build cruisers (success)"


  f1.newfleetsetup(u1.planet_set.all()[0],{'scouts':5, 'destroyers':2})
  f2.newfleetsetup(u2.planet_set.all()[0],{'scouts':4, 'destroyers':1})


  doencounter(f1,f2)

  u1.get_profile().setpoliticalrelation(p2,"enemy")
  u1.get_profile().save()
  u1.get_profile().save()

  f1.x = f2.x + .1
  f1.y = f2.y + .1
  doencounter(f1,f2)

  f1.delete()
  f2.delete()



def testpiracy(u1, u2):
  # test basic piracy
  f1 = Fleet(owner=u1)
  f2 = Fleet(owner=u2)

  f1.newfleetsetup(u1.planet_set.all()[0],{'frigates':2})
  f1.disposition = 9
  f2.newfleetsetup(u2.planet_set.all()[0],{'merchantmen':1})


  dopiracy(f1,f2)

  f1.x = f2.x + .1
  f1.y = f2.y + .1

  dopiracy(f1,f2)

  if f1.id != None:
    f1.delete()
  if f2.id != None:
    f2.delete()





if Player.objects.count() == 0:
  u = User.objects.get(id=1)
  p = Player(user=u)
  p.color = "#ff0000"
  pl = Planet.objects.get(id=10000)
  p.capital = pl 
  p.save()
  pl.owner = u
  pl.save()

try:
  u1 = User.objects.get(username="User1")
  u2 = User.objects.get(username="User2")
  print "fail u1"
except:
  print "pass u1"

try:
  p1 = Player.objects.get(user=u1)
  p2 = Player.objects.get(user=u2)
  print "fail p1"
except:
  print "pass p1"

try:
  p1.delete()
  p2.delete()
  print "fail d-p1"
except:
  print "pass d-p1"

try:
  u1.delete()
  u2.delete()
except:
  print "pass d-u1"


# create two test players
u1 = User(username="User1")
u1.save()
u2 = User(username="User2")
u2.save()

p1 = Player(user=u1)
p2 = Player(user=u2)

p1.create()
p2.create()

#p1.save()
#p2.save()

p1.setpoliticalrelation(p2,"friend")
if p2 in p1.friends.all():
  print "p2 is p1's friend (success)"
if p2 in p1.enemies.all():
  print "p2 is p1's enemy (failure)"


if p1 in p2.friends.all():
  print "p1 is p2's friend (success)"
if p1 in p2.enemies.all():
  print "p1 is p2's enemy (failure)"

print "creating player planets..."
p1.create()
p2.create()
print "done"

print
print
print
print"----"
print
print
print
testfleets(u1,u2)
print
print
print
print"----"
print
print
print
for i in range(20):
  testpiracy(u1,u2)
print
print
print
print"----"
print
print
print



if u1.planet_set.count() > 0:
  print "u1 has a planet (success)"
else:
  print "u1 has no planet (failure)"

if u2.planet_set.count() > 0:
  print "u2 has a planet (success)"
else:
  print "u2 has no planet (failure)"



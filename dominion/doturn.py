#!/usr/bin/python
from newdominion.dominion.models import *


def doencounter(f1, f2):
  p1 = f1.owner.get_profile()
  p2 = f2.owner.get_profile()
  relation = p1.getpoliticalrelation(p2)
  if f2 == f1 or relation == "friend":
    print "friendly encounter"
    return
  elif relation == "enemy":
    print "battle..."
    dobattle(f1,f2)
  else:
    print "piracy?"
    # piracy?
    dopiracy(f1,f2)

def dobattle(f1, f2):
  report = []

  # make f1 the fleet that can see the farthest
  if f1.senserange() < f2.senserange():
    # swap...
    f1,f2 = f2,f1





  report.append("Battle Report:")
  report.append("fleet #" + str(f1.id) +" ("+ f1.owner.username +
                ") and fleet #" + str(f2.id) + " (" + 
                f2.owner.username + ")")
  #                               att > 0      and      that ship is present
  
  noncombatants1 = f1.numnoncombatants() 
  noncombatants2 = f2.numnoncombatants() 
  
  combatants1 = f1.numcombatants() 
  combatants2 = f2.numcombatants() 

  # what if we had a war, and nobody could fight?
  if len(combatants1) == 0 and len(combatants2) == 0:
    report.append("Menacing jestures were made, but no damage was done.")

  accel1 = f1.acceleration()
  accel2 = f2.acceleration()
  senserange1 = f1.senserange()
  senserange2 = f2.senserange()
  
  distance = getdistance(f1.x,f1.y,f2.x,f2.y)
  # some rules:  att = number of enemies that can be attacked per turn
  #              def = number of attacks suppressed (only 10% chance of success
  #              effective range = how far a ship type can shoot.
  # battles can be fought over multiple turns, depending on how long the ships stay
  # in range of each other

  attacks1 = f1.numattacks()
  attacks2 = f2.numattacks()

  print "---- before ----"
  print f1.description()
  print "----"
  print f2.description()
  print "---- end before ----"
  while attacks1 > 0 and attacks2 > 0:
    if attacks1:
      #report.append("1 attempts to attack 2")
      if random.random()<.1:
        f2ships = f2.shiptypeslist()
        unlucky = random.randint(0,len(f2ships)-1)
        unluckytype = f2ships[unlucky].name
        numships = getattr(f2, unluckytype)
        setattr(f2, unluckytype, numships-1)
        attacks2 -= f2.shiptypes[unluckytype]['att']
        report.append("success, 1 " + unluckytype + " destroyed")
      attacks1 -= 1
    if attacks2:
      #report.append("2 attempts to attack 1")
      if random.random()<.1:
        f1ships = f1.shiptypeslist()
        print len(f1ships)
        unlucky = random.randint(0,len(f1ships)-1)
        unluckytype = f1ships[unlucky].name
        numships = getattr(f1, unluckytype)
        setattr(f1, unluckytype, numships-1)
        attacks1 -= f1.shiptypes[unluckytype]['att']
        report.append("success, 1 " + unluckytype + " destroyed")
      attacks2 -= 1
  print "\n".join(report)


  print "---- after ----"
  print f1.description()
  print "----"
  print f2.description()
  print "---- end after ----"
# do planets update
planets = Planet.objects.filter(owner__isnull=False)
for planet in planets:
  planet.doturn()

fleets = Fleet.objects.all()
encounters = {}
for fleet in fleets:
  nearbyfleets = nearbythings(Fleet,fleet.x,fleet.y)
  for otherfleet in nearbyfleets:
    encounterid = '-'.join([str(x) for x in sorted([fleet.id,otherfleet.id])]) 
    if encounters.has_key(encounterid):
      continue
    encounters[encounterid] = 1
    if otherfleet == fleet:
      continue
    elif otherfleet.owner == fleet.owner:
      continue
    else:
      doencounter(fleet,otherfleet)
  fleet.doturn()


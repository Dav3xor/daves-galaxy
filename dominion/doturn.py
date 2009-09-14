#!/usr/bin/python
from newdominion.dominion.models import *


def doencounter(f1, f2):
  p1 = f1.owner.get_profile()
  p2 = f2.owner.get_profile()
  relation = p1.getpoliticalrelation(p2)
  if f2 == f1 or relation == "friend":
    print "friendly encounter"
    return
  elif f2.disposition == 9 or f1.disposition == 9:
    print "piracy..."
    dopiracy(f1,f2)
  elif relation == "enemy":
    print "battle..."
    dobattle(f1,f2)
  else:
    print "piracy?"


def dopiracy(f1, f2):
  print "------  Starting Piracy! -----"
  distance = getdistance(f1.x,f1.y,f2.x,f2.y)
  relations = f1.owner.get_profile().getpoliticalrelation(f2.owner.get_profile())
  # see who is pirating who...
  if f2.senserange() > f1.senserange() and f2.disposition == 9:
    print "swapping fleets"
    f1,f2 = f2,f1
  
  # ok, from this point on we assume that f1 is the pirate, and
  # f2 is the prey
  print f1
  print f2
  if f2.numcombatants() > 0: 
    # Ok, f2 has combatants, so attempt to sulk away,
    # unless f2 is wise to f1's piratical nature
    # (f2 attacks f1 if within sense range and
    # a random factor is met...
    print "f2 is not a pushover..."
    if distance < f2.senserange():
      if relations == "enemy":
        print "f2 attacks enemy pirate..."
        dobattle(f2,f1)
      elif random.random() < .25:
        print "f2 attacks neutral pirate..."
        dobattle(f2,f1)
  else:
    # aha, actual piracy happens here --
    outcome = random.random()
    if outcome < .7:          # cargo got dropped
      print "dropped"
      if f2.trade_manifest:
        if f1.trade_manifest is None:
          f1.trade_manifest = Manifest()
        for item in f2.trade_manifest.manifestlist(['id','people','quatloos']):
          setattr(f1,item,getattr(f1.trade_manifest,item)+getattr(f2.trade_manifest,item))
          setattr(f2,item,0)
      else:
        print "nothing to steal?"
        # there's nothing to steal, odd...
    elif outcome < .9:        # duke it out...
      print "dukes"
      dobattle(f1,f2)
    else:                     # surrender...
      print "capitulation!"  
      for shiptype in f2.shiptypeslist():
        setattr(f1,shiptype.name,getattr(f1,shiptype.name)+getattr(f2,shiptype.name))
      if f2.trade_manifest is not None:
        if f1.trade_manifest is None:
          f1.trade_manifest = Manifest()
        for item in f2.trade_manifest.manifestlist(['id']):
          setattr(f1,item,getattr(f1.trade_manifest,item)+getattr(f2.trade_manifest,item))
          setattr(f2,item,0)
      f1.save()
      f1.trade_manifest.save()
      f2.delete()




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
  if combatants1 == 0 and combatants2 == 0:
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
        attacks2 -= shiptypes[unluckytype]['att']
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
        attacks1 -= shiptypes[unluckytype]['att']
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


#!/usr/local/bin/python2.5
from newdominion.dominion.models import *
from django.db import transaction
import sys


def doencounter(f1, f2, f1report, f2report):
  if f1.numships() == 0:
    return
  if f2.numships() == 0:
    return
  distance = getdistanceobj(f1,f2)
  if distance > f1.senserange() and distance > f2.senserange():
    return
  p1 = f1.owner.get_profile()
  p2 = f2.owner.get_profile()
  relation = p1.getpoliticalrelation(p2)
  if f2 == f1 or relation == "friend":
    #print "friendly encounter"
    return
  elif f2.disposition == 9 or f1.disposition == 9:
    #print "piracy..."
    dopiracy(f1,f2, f1report, f2report)
  elif relation == "enemy":
    #print "battle..."
    dobattle(f1,f2, f1report,f2report)
  else:
    return

def dopiracy(f1, f2, f1report, f2report):
  if f1.numships() == 0:
    return
  if f2.numships() == 0:
    return
  #print "------  Starting Piracy! -----"
  distance = getdistance(f1.x,f1.y,f2.x,f2.y)
  relations = f1.owner.get_profile().getpoliticalrelation(f2.owner.get_profile())
  # see who is pirating who...

  if f2.senserange() > f1.senserange() and f2.disposition == 9:
    print "swapping fleets"
    f1,f2 = f2,f1
    f1report, f2report = f2report, f1report
  

  replinestart1 = "Piracy - Fleet # " + str(f1.id) + "(pirate) "
  replinestart2 = "Piracy - Fleet # " + str(f2.id) + "(pirate's target) "
  # ok, from this point on we assume that f1 is the pirate, and
  # f2 is the prey
  if f2.numcombatants() > 0: 
    # Ok, f2 has combatants, so attempt to sulk away,
    # unless f2 is wise to f1's piratical nature
    # (f2 attacks f1 if within sense range and
    # a random factor is met...
    f1report.append(replinestart1 + "The other fleet is not a pushover...")
    if distance < f2.senserange():
      if relations == "enemy":
        f1report.append(replinestart1 + "They see us and are attacking.")
        f2report.append(replinestart2 + "Pirate scum found.")
        dobattle(f2,f1, f2report, f1report)
      elif random.random() < .25:
        f1report.append(replinestart1 + "Found by neutral combatants.  ")
        f2report.append(replinestart2 + "Neutral pirate scum found, attacking.")
        dobattle(f2,f1, f2report, f1report)
  else:
    # aha, actual piracy happens here --
    outcome = random.random()
    if outcome < .7:          # cargo got dropped
      f1report.append(replinestart1 + "Prey dropped cargo, retrieved.")
      f2report.append(replinestart2 + "Pirates attacked, we dropped our cargo to escape.")
      if f2.trade_manifest:
        if f1.trade_manifest is None:
          f1.trade_manifest = Manifest()
        for item in f2.trade_manifest.manifestlist(['id','people','quatloos']):
          setattr(f1,item,getattr(f1.trade_manifest,item)+getattr(f2.trade_manifest,item))
          setattr(f2,item,0)
      else:
        f1report.append(replinestart1 + "Prey escaped.")
        f2report.append(replinestart2 + "Pirates seen.")
        # there's nothing to steal, odd...
    elif outcome < .9:        # duke it out...
      print "dukes"
      dobattle(f1,f2,f1report,f2report)
    else:                     # surrender...
      f1report.append(replinestart1 + "Prey surrendered.")
      f2report.append(replinestart2 + "Surrendered to Pirates.")
      for shiptype in f2.shiptypeslist():
        setattr(f1,shiptype.name,getattr(f1,shiptype.name)+getattr(f2,shiptype.name))
        setattr(f2,shiptype.name,0)
      if f2.trade_manifest is not None:
        if f1.trade_manifest is None:
          f1.trade_manifest = Manifest()
        for item in f2.trade_manifest.manifestlist(['id']):
          setattr(f1,item,getattr(f1.trade_manifest,item)+getattr(f2.trade_manifest,item))
          setattr(f2,item,0)
        f1.trade_manifest.save()
      f1.save()
      # delete later...
      f2.save()




def dobattle(f1, f2, f1report, f2report):
  report = []
  if f1.numships() == 0:
    return
  if f2.numships() == 0:
    return
  # make f1 the fleet that can see the farthest
  if f1.senserange() < f2.senserange():
    # swap...
    f1,f2 = f2,f1
    f1report, f2report = f2report, f1report

  f1before = f1.shiplistreport()
  f2before = f2.shiplistreport()

  f1numbefore = f1.numships()
  f2numbefore = f1.numships()

  
  f1replinestart = "Fleet: " + f1.shortdescription(html=0) + " (" + str(f1.id) + ") Battle! -- "
  f2replinestart = "Fleet: " + f2.shortdescription(html=0) + " (" + str(f2.id) + ") Battle! -- "
  
  noncombatants1 = f1.numnoncombatants() 
  noncombatants2 = f2.numnoncombatants() 
  
  combatants1 = f1.numcombatants() 
  combatants2 = f2.numcombatants() 

  # what if we had a war, and nobody could fight?
  if combatants1 == 0 and combatants2 == 0:
    f1report.append(f1replinestart + "Menacing jestures were made, but no damage was done.")
    f2report.append(f2replinestart + "Menacing jestures were made, but no damage was done.")

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

  while attacks1 > 0 or attacks2 > 0:
    if f1.numships() == 0 or f2.numships() == 0:
      break
    if attacks1:
      #report.append("1 attempts to attack 2")
      if random.random()<.1:
        f2ships = f2.shiptypeslist()
        unlucky = random.randint(0,len(f2ships)-1)
        unluckytype = f2ships[unlucky].name
        numships = getattr(f2, unluckytype)
        setattr(f2, unluckytype, numships-1)
        attacks2 -= shiptypes[unluckytype]['att']
        f1report.append(f1replinestart + "Enemy " + shiptypes[unluckytype]['singular'] + " destroyed")
        f2report.append(f2replinestart + "We Lost a " + shiptypes[unluckytype]['singular'] + " destroyed")
        f2.save()
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
        f2report.append(f2replinestart + "Enemy " + shiptypes[unluckytype]['singular'] + " destroyed")
        f1report.append(f1replinestart + "We Lost a " + shiptypes[unluckytype]['singular'] + " destroyed")
        f1.save()
      attacks2 -= 1

@transaction.commit_on_success
def doturn():
  # do planets update
  reports = {}
  planets = Planet.objects.filter(owner__isnull=False)
  for planet in planets:
    if not reports.has_key(planet.owner.id):
      reports[planet.owner.id]=[]

    planet.doturn(reports[planet.owner.id])

  fleets = Fleet.objects.all()
  encounters = {}
  for fleet in fleets:
    if not reports.has_key(fleet.owner.id):
      reports[fleet.owner.id]=[]
    fleet.doturn(reports[fleet.owner.id])
  
    nearbyfleets = nearbythings(Fleet,fleet.x,fleet.y)
    for otherfleet in nearbyfleets:
      if not reports.has_key(otherfleet.owner.id):
        reports[otherfleet.owner.id]=[]
      encounterid = '-'.join([str(x) for x in sorted([fleet.id,otherfleet.id])]) 
      if encounters.has_key(encounterid):
        continue
      encounters[encounterid] = 1
      if otherfleet == fleet:
        continue
      elif otherfleet.owner == fleet.owner:
        continue
      else:
        doencounter(fleet,
                    otherfleet,
                    reports[fleet.owner.id],
                    reports[otherfleet.owner.id])

  # cull fleets...
  fleets = Fleet.objects.all()
  for fleet in fleets:
    if fleet.numships() == 0:
      print "deleting fleet #" + str(fleet.id)
      fleet.delete()

  for report in reports:
    if len(reports[report]) == 0:
      continue
    user = User.objects.get(id=report)
    fullreport = "\n".join(reports[report])
    print "PLAYER #" + str(report) + " (" + user.username + ") REPORT:"
    print "-----------------------------------------------"
    print fullreport

    print user.email 
    send_mail("Dave's Galaxy Turn Report", fullreport, 'turns@davesgalaxy.com', [user.email])
  print "-- successful end of turn --"


if __name__ == "__main__":
  doturn()

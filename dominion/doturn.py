#!/usr/local/bin/python2.5
from newdominion.dominion.models import *
from django.db import transaction
import sys
import os
import random

def doencounter(f1, f2, f1report, f2report):
  f1 = Fleet.objects.get(id=f1.id)
  f2 = Fleet.objects.get(id=f2.id)
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

  replinestart1 = "Piracy - Fleet # " + str(f1.id) + "(pirate) "
  replinestart2 = "Piracy - Fleet # " + str(f2.id) + "(pirate's target) "
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


def doattack(fleet1, fleet2, f1report, f2report, f1replinestart, f2replinestart):
  done = 1
  for ship in fleet1:
    if len(fleet2) == 0:
      done = 1
      break
    if ship['att'] > 0:
      done = 0 
      ship['att'] -= 1
      if random.random() < .1:
        random.shuffle(fleet2)
        if fleet2[0]['def'] and random.random < .7:
          # successful defense
          f1report.append(f1replinestart + "Enemy " + shiptypes[fleet2[0]['type']]['singular'] + " dodged an attack")
          f2report.append(f2replinestart + "Our " + shiptypes[fleet2[0]['type']]['singular'] + " dodged an attack")
          continue
        # kaboom...
        f1report.append(f1replinestart + "Enemy " + shiptypes[fleet2[0]['type']]['singular'] + " destroyed")
        f2report.append(f2replinestart + "We Lost a " + shiptypes[fleet2[0]['type']]['singular'] + " destroyed")
        fleet2[0]['delete'] = 1
  tmp = range(len(fleet2))
  tmp.reverse()
  for i in tmp:
    if fleet2[i].has_key('delete'):
      fleet2.pop(i)
  return done, fleet1, fleet2

def dobattle(f1, f2, f1report, f2report):
  report = []
  if f1.numships() == 0:
    return
  if f2.numships() == 0:
    return


  
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


  fleet1 = f1.listrepr()
  fleet2 = f2.listrepr()
  
  distance = getdistance(f1.x,f1.y,f2.x,f2.y)

  attackoccurred = 0

  done1 = 0
  done2 = 0

  print "-- before attacks ("+str(len(fleet1))+","+str(len(fleet2))+")"  
 
  while not (done1 and done2):
    done1, fleet1, fleet2 = doattack(fleet1, fleet2, f1report, f2report, f1replinestart, f2replinestart)
    done2, fleet2, fleet1 = doattack(fleet2, fleet1, f2report, f1report, f2replinestart, f1replinestart) 
 
  print "-- after attacks ("+str(len(fleet1))+","+str(len(fleet2))+")"  
  for type in shiptypes:
    setattr(f1, type, 0)
    setattr(f2, type, 0)

  if len(fleet1):
    for ship in fleet1:
      setattr(f1, ship['type'], getattr(f1,ship['type']) + 1)

  if len(fleet2):
    for ship in fleet2:
      setattr(f2, ship['type'], getattr(f2,ship['type']) + 1)
  f1.save()
  f2.save()

@transaction.commit_on_success
def doturn():
  # do planets update
  reports = {}
  random.seed()
  planets = Planet.objects.filter(owner__isnull=False)
  for planet in planets:
    if not reports.has_key(planet.owner.id):
      reports[planet.owner.id]=[]

    planet.doturn(reports[planet.owner.id])

  # cull fleets...
  fleets = Fleet.objects.all()
  for fleet in fleets:
    if fleet.numships() == 0:
      print "deleting fleet #" + str(fleet.id)
      fleet.delete()
  
  fleets = Fleet.objects.all()
  for fleet in fleets:
    if not reports.has_key(fleet.owner.id):
      reports[fleet.owner.id]=[]

    fleet.doturn(reports[fleet.owner.id])
  

  encounters = {}
  fleets = Fleet.objects.all()
  fleetorder = range(len(fleets))
  random.shuffle(fleetorder)
  for fn in fleetorder:
    senserange = fleets[fn].senserange()
    nearbyfleets = nearbysortedthings(Fleet,fleets[fn])
    for otherfleet in nearbyfleets:
      if getdistanceobj(fleets[fn],otherfleet) > senserange:
        break

      if not reports.has_key(otherfleet.owner.id):
        reports[otherfleet.owner.id]=[]
      
      encounterid = '-'.join([str(x) for x in sorted([fleets[fn].id,otherfleet.id])]) 
      if encounters.has_key(encounterid):
        continue
      encounters[encounterid] = 1
      if otherfleet == fleets[fn]:
        continue
      elif otherfleet.owner == fleets[fn].owner:
        continue
      else:
        doencounter(fleets[fn],
                    otherfleet,
                    reports[fleet.owner.id],
                    reports[otherfleet.owner.id])


  for report in reports:
    if len(reports[report]) == 0:
      continue
    user = User.objects.get(id=report)
    fullreport = "\n".join(reports[report])
    print "PLAYER #" + str(report) + " (" + user.username + ") REPORT:"
    print "-----------------------------------------------"
    print fullreport

    print user.email 
    if os.path.exists('/home/dav3xor/webapps/game/newdominion/dominion/'):
      send_mail("Dave's Galaxy Turn Report", 
                fullreport, 
                'turns@davesgalaxy.com', 
                [user.email])
    else:
      print "(test)"
  print "-- successful end of turn --"


if __name__ == "__main__":
  doturn()

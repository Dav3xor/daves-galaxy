#!/usr/bin/python2

from newdominion.dominion.models import *
from newdominion.dominion.util import *
from django.db import connection, transaction
from django.db.models import Avg, Max, Min, Count
import sys
import os
import random
import time
import newdominion.settings

def doencounter(f1, f2, f1report, f2report):
  f1 = Fleet.objects.get(id=f1.id)
  f2 = Fleet.objects.get(id=f2.id)
  if f1.numships() == 0:
    return
  if f2.numships() == 0:
    return
  p1 = f1.owner.get_profile()
  p2 = f2.owner.get_profile()
  relation = p1.getpoliticalrelation(p2)
  if f2 == f1 or relation == "friend":
    #print "friendly encounter"
    return
  if f1.disposition == 9:
    #print "piracy..."
    dopiracy(f1,f2, f1report, f2report)
  elif f2.disposition == 9:
    #print "piracy..."
    dopiracy(f2,f1, f2report, f1report)
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
        f2.damaged = True
        f2.gotoplanet(f2.homeport)
      else:
        f1report.append(replinestart1 + "Prey escaped.")
        f2report.append(replinestart2 + "Pirates seen.")
        # there's nothing to steal, odd...
    elif outcome < .9:        # duke it out...
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



def doattack(fleet1, fleet2, minatt=0, justonce=True):
  dead = []
  done = 1

  # if one fleet is much bigger than the other,
  # assume that  
  startship = 0
  if len(fleet1) > len(fleet2)*1.5:
    startship = len(fleet1)-int(max(0,((len(fleet2)*1.5))))

  for i in xrange(startship,len(fleet1)):
    while fleet1[i]['att'] >= minatt:
      done = 0 
      if random.random() < .1:
        # see if we've hit something...
        hit = random.randint(0,len(fleet2)-1)
        dodged = False
        # you get 3 chances to dodge (if you have defences left...)
        for j in xrange(3):
          if fleet2[hit]['def'] and random.random() < .7:
            fleet2[hit]['def'] -= 1
            # successful defense
            dodged = True
            break
        if not dodged:
          # kaboom...
          dead.append(hit)
      fleet1[i]['att'] -= 1
      if justonce == True:
        break

  return done, dead

def dobattle(f1, f2, f1report, f2report):
  def generatelossreport(casualties1,casualties2,f1report,
                         f1replinestart,f2replinestart):
    if len(casualties1):
      f1report.append(f1replinestart + "Our Ships Lost:")
      for casualties in casualties1:
        f1report.append("   %20s -- %d" % (casualties, casualties1[casualties]))

    if len(casualties2):
      f1report.append(f2replinestart + "Their Ships Lost:")
      for casualties in casualties2:
        f1report.append("   %20s -- %d" % (casualties, casualties2[casualties]))
  
  def removedestroyed(dead,casualtylist,fleet):
    # remove duplicates and sort last to first
    dead = sorted(list(set(dead)),reverse=True)
    for i in dead:
      print str(i) + " - " + str(len(fleet))
      if not casualtylist.has_key(fleet[i]['type']):
        casualtylist[fleet[i]['type']] = 1
      else: 
        casualtylist[fleet[i]['type']] += 1

      fleet.pop(i)

  report = []
  total1 = f1.numships()
  total2 = f2.numships()
  noncombatants1 = f1.numnoncombatants() 
  noncombatants2 = f2.numnoncombatants() 
  combatants1 = f1.numcombatants() 
  combatants2 = f2.numcombatants() 
  casualties1 = {}
  casualties2 = {}
 
  if total1 == 0:
    return
  if total2 == 0:
    return
  
  f1replinestart = "Fleet: " + f1.shortdescription(html=0) + " (" + str(f1.id) + ") Battle! -- "
  f2replinestart = "Fleet: " + f2.shortdescription(html=0) + " (" + str(f2.id) + ") Battle! -- "
  

  # what if we had a war, and nobody could fight?
  if combatants1 == 0 and combatants2 == 0:
    f1report.append(f1replinestart + "Menacing jestures were made, but no damage was done.")
    f2report.append(f2replinestart + "Menacing jestures were made, but no damage was done.")
    return

  fleet1 = f1.listrepr()
  fleet2 = f2.listrepr()
  
  distance = getdistance(f1.x,f1.y,f2.x,f2.y)

  attackoccurred = 0

  done1 = 0
  done2 = 0 
  
  counter = 1 
  
  dead1=[]
  dead2=[]
  
  done1, dead2 = doattack(fleet1, fleet2,0,True)
  done2, dead1 = doattack(fleet2, fleet1,0,True) 
  
  while (not (done1 and done2)) and len(fleet1) and len(fleet2):
    if fleet1[0]['att'] > fleet2[0]['att'] and counter % 4 != 1:
      done1, dead2 = doattack(fleet1, fleet2,fleet2[0]['att'])
    elif fleet2[0]['att'] > fleet1[0]['att'] and counter % 4 != 1:
      done2, dead1 = doattack(fleet2, fleet1,fleet2[0]['att']) 
    else:
      done1, dead2 = doattack(fleet1, fleet2)
      done2, dead1 = doattack(fleet2, fleet1) 

    if len(dead1) > 0:
      removedestroyed(dead1,casualties1,fleet1)
      dead1 = []

    if len(dead2) > 0:
      removedestroyed(dead2,casualties2,fleet2)
      dead2 = []
    
    counter += 1

          #fleet2.pop(hit)
    
  if len(casualties1) or len(casualties2):
    # write a report...
    generatelossreport(casualties1,casualties2,
                       f1report,f1replinestart,f2replinestart)
    generatelossreport(casualties2,casualties1,
                       f2report,f2replinestart,f1replinestart)


  if total1 > len(fleet1):
    f1.damaged = True
  if total2 > len(fleet2):
    f2.damaged = True

  for type in shiptypes:
    setattr(f1, type, 0)
    setattr(f2, type, 0)

  if len(fleet1):
    for ship in fleet1:
      setattr(f1, ship['type'], getattr(f1,ship['type']) + 1)
  else:
    f1.destroyed = True

  if len(fleet2):
    for ship in fleet2:
      setattr(f2, ship['type'], getattr(f2,ship['type']) + 1)
  else:
    f2.destroyed = True

  f1.save()
  f2.save()

@print_timing
def doclearinview():
  cursor = connection.cursor()

  # Data modifying operation
  cursor.execute("DELETE FROM dominion_fleet_inviewof;")
  cursor.execute("DELETE FROM dominion_fleet_inviewoffleet;")
  cursor.execute("DELETE FROM dominion_player_neighbors;")

  # Since we modified data, mark the transaction as dirty
  transaction.set_dirty()

@print_timing
def dobuildinview():

  def checknearby(a,b):
    if abs(a['x'] - b['x']) <= 2.0 and abs(a['y'] - b['y']) <= 2.0:
      return True
    else:
      return False

  def addtopossible(possibles, fleet, other):
    if not possibles.has_key(fleet['id']):
      possibles[fleet['id']] = []
    possibles[fleet['id']].append(other['id'])
  
  def addtodefinite(deflist, stuff):
    for i in stuff:
      if not deflist.has_key(i):
        deflist[i] = 1
    
  players = Player.objects.all()
  
  for player in players:
    player.cursectors = expandsectors(player.footprint())
 
  fleetplayerview = {}
  fleetfleetview = {}
  for i in range(len(players)):
    curplayer = players[i]
    curuser = curplayer.user
    curplanets = curuser.planet_set
    curfleets  = curuser.fleet_set

    addtodefinite(fleetplayerview, [(str(k),str(curplayer.user.id))
                   for k in curplayer.user.fleet_set.all().values_list('id',flat=True)])

    possiblefleets = {}
    possibleplanets = {}

    for j in range(i+1,len(players)):
      otherplayer = players[j]
      
    
      #if allies, show all fleets to each other.
      if curplayer.getpoliticalrelation(otherplayer) == 'friend':
        addtodefinite(fleetplayerview,
                      [(str(k),str(curplayer.user.id))
                       for k in otherplayer.user.fleet_set.all().values_list('id',flat=True)])
        addtodefinite(fleetplayerview,
                      [(str(k),str(otherplayer.user.id))
                       for k in curplayer.user.fleet_set.all().values_list('id',flat=True)])
                       
      # else, we have to do some digging.  
      else:
        intersection = curplayer.cursectors & otherplayer.cursectors
        if len(intersection):
          otherfleets  = Fleet.objects.filter(owner=otherplayer.user,
                                              sector__key__in=intersection).values('id','x','y')

          otherplanets = Planet.objects.filter(owner=otherplayer.user,
                                              sector__key__in=intersection).values('id','x','y')

          myfleets     = Fleet.objects.filter(owner=curplayer.user,
                                              sector__key__in=intersection).values('id','x','y')

          myplanets    = Planet.objects.filter(owner=curplayer.user,
                                              sector__key__in=intersection).values('id','x','y')
          
          for fleet in myfleets:
            for other in otherfleets:
              if checknearby(fleet,other):
                addtopossible(possiblefleets, fleet, other)
            for planet in otherplanets:
              if checknearby(fleet,planet):
                addtopossible(possibleplanets, fleet, planet) 
          
          for fleet in otherfleets:
            for other in myfleets:
              if checknearby(fleet,other):
                addtopossible(possiblefleets, fleet, other)
            for planet in myplanets:
              if checknearby(fleet,planet):
                addtopossible(possibleplanets, fleet, planet) 

          ffleets = Fleet.objects.filter(id__in=possiblefleets.keys())
          for fleet in ffleets:
            otherids = possiblefleets[fleet.id]

            others = Fleet.objects.filter(id__in=otherids)
            for other in others:
              if fleet.doinviewof(other):
                addtodefinite(fleetplayerview,[(str(fleet.id),str(other.owner.id))])
                addtodefinite(fleetfleetview,[(str(fleet.id),str(other.id))])
                break

          pfleets = Fleet.objects.filter(id__in=possibleplanets.keys())     
          for fleet in pfleets:
            otherids = possibleplanets[fleet.id]
            
            others = Planet.objects.filter(id__in=otherids)
            for other in others:
              if fleet.doinviewof(other):
                addtodefinite(fleetplayerview,[(str(fleet.id),str(other.owner.id))])
                break

  insertrows('dominion_fleet_inviewof',
             ('fleet_id', 'user_id'),
             fleetplayerview.keys())
  insertrows('dominion_fleet_inviewoffleet',
             ('from_fleet_id', 'to_fleet_id'),
             fleetfleetview.keys())

@print_timing
def dobuildneighbors():
  """
  >>> buildneighbors()
  """
  print "building neighbors..."
  players = Player.objects.all()
  for player in players:
    # expand sectors twice for neighbors
    player.cursectors = expandsectors(expandsectors(player.footprint()))

  for i in xrange(len(players)):
    neighbors = []
    for j in xrange(i+1,len(players)):
      if len(players[i].cursectors & players[j].cursectors):
        neighbors.append(players[j])
    if len(neighbors):
      print "%s --- %s" %(str(players[i]),str(neighbors))
      apply(players[i].neighbors.add,neighbors)



@transaction.commit_on_success
def doturn():
  random.seed()
  reports = {}
  info = {}
  doclearinview()
  dobuildneighbors()
  doatwar(reports,info)
  doplanets(reports)
  cullfleets(reports)
  dofleets(reports)
  dobuildinview()
  doencounters(reports)
  sendreports(reports)

def doatwar(reports, info):
  """
  >>> s = Sector(key=125123,x=100,y=100)
  >>> s.save()

  >>> u = User(username="doatwar")
  >>> u.save()
  >>> r = Manifest(people=5000, food=1000)
  >>> r.save()
  >>> p = Planet(resources=r, society=1,owner=u, sector=s,
  ...            x=626, y=617, r=.1, color=0x1234, name="Planet X")
  >>> p.save()
  >>> pl = Player(user=u, capital=p, color=112233)
  >>> pl.save()

  >>> u2 = User(username="doatwar2")
  >>> u2.save()
  >>> r = Manifest(people=5000, food=1000)
  >>> r.save()
  >>> p2 = Planet(resources=r, society=1,owner=u2, sector=s,
  ...            x=626, y=617, r=.1, color=0x1234, name="Planet X")
  >>> p2.save()
  >>> pl2 = Player(user=u2, capital=p, color=112233)
  >>> pl2.save()
  """
  atwar = User.objects.filter(player__enemies__isnull=False).distinct()
  for user in atwar:
    if not reports.has_key(user.id):
      reports[user.id]=[]
    reports[user.id].append("WAR! -- you are at war with the following players:")
    for enemy in user.get_profile().enemies.all():
      reports[user.id].append("  " + enemy.user.username)
@print_timing
def doplanets(reports):
  # do planets update
  planets = Planet.objects.filter(owner__isnull=False)
  for planet in planets.iterator():
    if not reports.has_key(planet.owner.id):
      reports[planet.owner.id]=[]

    planet.doturn(reports[planet.owner.id])

@print_timing
def cullfleets(reports):
  # cull fleets...
  print "---"
  print "Culling Fleets"

  print "Num Destroyed = " + str(Fleet.objects.filter(destroyed=True).count())
  Fleet.objects.filter(destroyed=True).delete()

  print "Num Damaged = " + str(Fleet.objects.filter(damaged=True).count())
  Fleet.objects.filter(damaged=True).update(damaged=False)

  # spin through and remove all empty fleets (colony fleets that colonized, etc...)
  # should be able to do this inside the db with another couple flags... (see
  # above destroyed/damaged flags...)
  fleets = Fleet.objects.all()
  for fleet in fleets:
    if fleet.numships() == 0:
      print "deleting fleet #" + str(fleet.id)
      fleet.delete()
  print "---"

@print_timing
def dofleets(reports):
  fleets = Fleet.objects.all()
  prices = {}
  for fleet in fleets.iterator():
    if not reports.has_key(fleet.owner.id):
      reports[fleet.owner.id]=[]
    if fleet.destination and fleet.destination.owner:
      if not reports.has_key(fleet.destination.owner.id):
        reports[fleet.destination.owner.id]=[]
      fleet.doturn(reports[fleet.owner.id],
                   reports[fleet.destination.owner.id],
                   prices)
    else:
      blah = []
      fleet.doturn(reports[fleet.owner.id],blah,prices)
  
@print_timing
def doencounters(reports):
  encounters = {}
  fleets = Fleet.objects.filter(viewable__isnull=False)
  fleetorder = range(len(fleets))
  random.shuffle(fleetorder)
  for fn in fleetorder:
    for otherfleet in fleets[fn].viewable.all():
      if not reports.has_key(otherfleet.owner.id):
        reports[otherfleet.owner.id]=[]
      
      encounterid = '-'.join([str(x) for x in sorted([fleets[fn].id,otherfleet.id])]) 
      if encounters.has_key(encounterid):
        continue
      encounters[encounterid] = 1
      if otherfleet.owner == fleets[fn].owner:
        continue
      else:
        doencounter(fleets[fn],
                    otherfleet,
                    reports[fleets[fn].owner.id],
                    reports[otherfleet.owner.id])

@print_timing
def sendreports(reports):
  for report in reports:
    if len(reports[report]) == 0:
      continue
    user = User.objects.get(id=report)
    fullreport = "\n".join(reports[report])
    fullreport = fullreport.encode('utf8')
    print "PLAYER #" + str(report) + " (" + user.username + ") REPORT:"
    print "-----------------------------------------------"
    print fullreport

    print user.email 
    if newdominion.settings.DEBUG == False:
      send_mail("Dave's Galaxy Turn Report", 
                fullreport, 
                'turns@davesgalaxy.com', 
                [user.email])
    else:
      print "(test)"
  print "-- successful end of turn --"


if __name__ == "__main__":
  starttime = time.time()

  doturn()
  
  endtime = time.time()
  elapsed = endtime-starttime
  print "Elapsed: " + str(elapsed) + "s"

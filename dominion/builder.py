#!/usr/bin/python2

import django
django.setup()

from newdominion.dominion.models import *
import time

r = RedisQueueServer('builder')

def buildupgrade(msg):
  print "starting upgrade"
  planets = Planet.objects.filter(id=msg['planetid'])
  userid = msg['userid'] 
  upgrade = msg['upgrade']
  if len(planets):
    curplanet = planets[0]
    if curplanet.owner_id == userid:
      curplanet.startupgrade(upgrade,True)
      return 1
  return 0

def scrapupgrade(msg):
  django.db.connection.queries=[]
  print "scrapping upgrade"
  planets = Planet.objects.filter(id=msg['planetid'])
  userid = msg['userid']
  upgrade = msg['upgrade']
  if len(planets):
    curplanet = planets[0]
    if curplanet.owner_id == userid:
      scrapupgrade = PlanetUpgrade.objects\
                                  .filter(planet=curplanet, 
                                          instrumentality__type=int(upgrade))\
                                  .select_related('planet','planet__resources',
                                                  'raised',
                                                  'instrumentality', 
                                                  'instrumentality__requires')

      if scrapupgrade:
        # in case we have duplicates (mumble mumble)
        for i in scrapupgrade:
          i.scrap()
        pprint (django.db.connection.queries)
        return 1
  return 0

def buildfleet(msg):
  statusmsg = ""
  userid    = msg['userid']
  newships  = msg['ships']
  planets   = Planet.objects\
                    .filter(id=msg['planetid'])\
                    .select_related('sector','resources','owner')
  print "Build Fleet:",
  if len(planets):
    planet = planets[0]
    if planet.owner_id != userid:
      print "failure, wrong owner" 
      return ("Not Your Planet.",)

    fleet = Fleet()
    statusmsg = fleet.newfleetsetup(planet,newships)  
    if len(statusmsg) == 2:
      print "success"
      return ('Fleet Built, Send To? (Escape to Cancel)', fleet.listjson(planet.owner))
    else:
      return statusmsg
def scrapfleet(msg):
  fleetid = msg['fleet']
  userid  = msg['userid']
  fleets  = Fleet.objects\
                 .filter(id=fleetid)\
                 .select_related('owner','resources','destination',
                                 'destination__resources','homeport',
                                 'homeport__resources', 'source',
                                 'source__resources', 'trade_manifest')
  if len(fleets):
    fleet = fleets[0]
    if fleet.owner_id != userid:
      return ("Not Your Fleet.",)
    elif not fleet.inport():
      return ("Not In Port.",)
    else:
      fleet.scrap()
      return ('Fleet Scrapped.',
              buildjsonsectors([fleet.sector_id],fleet.owner))
    


functions = {'buildupgrade':buildupgrade, 
             'scrapupgrade':scrapupgrade,
             'buildfleet':buildfleet,  
             'scrapfleet':scrapfleet
            }

def builder(msg):
  if msg[0] not in functions:
    print "unknown key? --> " + str(msg[0])
    return None
  else:
    return functions[msg[0]](msg[1])
  
while 1:
  r.doBeerAndABump(builder)

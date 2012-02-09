#!/usr/bin/python2

from django.db import connection, transaction
from django.core.mail import send_mail
from newdominion.dominion.models import *
import newdominion.settings

cursor = connection.cursor()


localcache['upgrades']    = allupgrades()
localcache['attributes']  = allattributes()
localcache['players']     = allplayers()
localcache['costs']       = {}


# calculate sensor range for fleets and planets
print "fleet sensor ranges..."
for fleet in Fleet.objects\
                  .exclude(destroyed=True)\
                  .select_related('homeport')\
                  .iterator():
  fleet.calculatesenserange()
  fleet.save()

print "planet sensor ranges..."
for planet in Planet.objects\
                    .exclude(owner=None)\
                    .select_related('resources')\
                    .iterator():
  planet.calculatesenserange()
  
  #also do some housekeeping...
  lastactive = localcache['players'][planet.owner_id]['lastactivity']
  timedelta = (datetime.datetime.today() - datetime.timedelta(hours=36))
  
  enoughfood = planet.productionrate('food')
  curpopulation = planet.resources.people

  if not planet.hasupgrade(Instrumentality.MINDCONTROL) and \
     lastactive > timedelta:
    planet.society += 1
  
  elif lastactive < \
     (datetime.datetime.today() - datetime.timedelta(days=10)) and \
     planet.resources.people > 70000:
    # limit population growth on absentee landlords... ;)
    planet.resources.people = curpopulation * (enoughfood*.9)
    planet.resources.save()

  if planet.getattribute('food-scarcity'):
    planet.setattribute('food-scarcity',None)
  planet.save()

# build neighbors
players = Player.objects.all()
print "building player sector lists"
for player in players:
  # expand sectors twice for neighbors
  player.cursectors = expandsectors(expandsectors(player.footprint()))
  player.friendset = set(player.friends.all().values_list('id',flat=True))
  player.enemyset = set(player.enemies.all().values_list('id',flat=True))

print "finding new neighbors"
withneighbors = []
for i in xrange(len(players)):
  neighbors = []
  for j in xrange(i+1,len(players)):
    if players[j].id in players[i].friendset or\
       players[j].id in players[i].enemyset or\
       len(players[i].cursectors & players[j].cursectors):
      neighbors.append(players[j])
  if len(neighbors):
    withneighbors.append([players[i],neighbors])



print "deleting old neighbors"
cursor.execute("DELETE FROM dominion_player_neighbors;")

print "adding new neighbors"
for line in withneighbors:
  apply(line[0].neighbors.add,line[1])
  print "%s --- %s" %(str(line[0]),str(line[1]))


if newdominion.settings.DEBUG == False:
  send_mail("DOSENSERANGE",
          "dosenserange.py succeeded",
          'turns@davesgalaxy.com',
          ['Dav3xor@gmail.com'])


#!/usr/bin/python2

from django.db import connection, transaction
from django.core.mail import send_mail
from newdominion.dominion.models import *
import newdominion.settings

cursor = connection.cursor()

"""
# calculate sensor range for fleets and planets
print "fleet sensor ranges..."
for fleet in Fleet.objects.exclude(destroyed=True).iterator():
  fleet.calculatesenserange()
  fleet.save()

print "planet sensor ranges..."
for planet in Planet.objects.exclude(owner=None).iterator():
  planet.calculatesenserange()
  planet.save()

"""

# build neighbors
players = Player.objects.all()
print "building player sector lists"
for player in players:
  # expand sectors twice for neighbors
  player.cursectors = expandsectors(expandsectors(player.footprint()))








print "finding new neighbors"
withneighbors = []
for i in xrange(len(players)):
  neighbors = []
  for j in xrange(i+1,len(players)):
    if len(players[i].cursectors & players[j].cursectors):
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


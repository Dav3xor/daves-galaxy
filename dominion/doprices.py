#!/usr/bin/python2

from newdominion.dominion.models import *
from django.db import connection
from pprint import pprint

django.db.connection.queries=[]

planets = Planet.objects.\
                filter(owner__isnull=False)


print "getting upgrades"

localcache['upgrades']       = allupgrades()
localcache['attributes']     = allattributes()



planets = planets.select_related('owner', 'resources',
                                 'prices', 'foreignprices')
counter = 0   


print "computing prices"
somewhatempty = {'x':1}
for planet in planets.iterator():
  up = {'x':1}
  attr = {'y':1}
  if planet.computeprices():
    planet.save()
  counter += 1
  if not counter % 100:
    print counter

print "number of queries = " + str(len(django.db.connection.queries))

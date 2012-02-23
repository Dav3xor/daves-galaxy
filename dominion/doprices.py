#!/usr/bin/python2

from newdominion.dominion.models import *
from django.db import connection
from pprint import pprint

django.db.connection.queries=[]

planets = Planet.objects\
                .filter(owner__isnull=False)\
                .select_related('owner', 'resources',
                                'prices', 'foreignprices')


print "getting upgrades"

localcache['upgrades']       = allupgrades()
localcache['attributes']     = allattributes()
counter = 0   


print "computing prices"
somewhatempty = {'x':1}
for planet in planets.iterator():
  #django.db.connection.queries = []
  planet.computeprices()
  #pprint (django.db.connection.queries)
  counter += 1
  if not counter % 100:
    print counter

print "number of queries = " + str(len(django.db.connection.queries))

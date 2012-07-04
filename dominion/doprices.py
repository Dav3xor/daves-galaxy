#!/usr/bin/python2

from newdominion.dominion.models import *
from django.db import connection
from pprint import pprint
import datetime

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

  #NOTE: the following code copies the planet surplus/resources
  #      and removes the primary key, so don't change anything
  #      on the planet below...  you've been warned...
  history = PlanetHistory(day          = datetime.datetime.now(),
                          planet       = planet,
                          sensorrange  = planet.sensorrange,
                          tariffrate   = planet.tariffrate,
                          inctaxrate   = planet.inctaxrate,
                          damaged      = planet.damaged)
  
  #TODO: do this all at once?
  history.inport = Fleet.objects\
                        .filter(sector= planet.sector,
                                x     = planet.x,
                                y     = planet.y)\
                        .count()
  prices = planet.prices
  prices.pk = None
  prices.save()
  history.prices = prices
  
  surplus = planet.resources
  surplus.pk = None
  surplus.save()
  history.surplus = surplus
  
  history.save()

  #pprint (django.db.connection.queries)
  counter += 1
  if not counter % 100:
    print counter

print "number of queries = " + str(len(django.db.connection.queries))

#!/usr/bin/python2

from newdominion.dominion.models import *

for fleet in Fleet.objects.exclude(destroyed=True).iterator():
  fleet.calculatesenserange()
  fleet.save()

for planet in Planet.objects.exclude(owner=None).iterator():
  planet.calculatesenserange()
  planet.save()

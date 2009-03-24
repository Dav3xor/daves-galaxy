#!/usr/bin/python
from newdominion.dominion.models import *

# do planets update
planets = Planet.objects.filter(owner__isnull=False)
for planet in planets:
  planet.doturn()

fleets = Fleet.objects.all()
for fleet in fleets:
  fleet.doturn()


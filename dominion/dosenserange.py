#!/usr/bin/python2

from django.core.mail import send_mail
from newdominion.dominion.models import *
import newdominion.settings

for fleet in Fleet.objects.exclude(destroyed=True).iterator():
  fleet.calculatesenserange()
  fleet.save()

for planet in Planet.objects.exclude(owner=None).iterator():
  planet.calculatesenserange()
  planet.save()

if newdominion.settings.DEBUG == False:
  send_mail("DOSENSERANGE",
          "dosenserange.py succeeded",
          'turns@davesgalaxy.com',
          ['Dav3xor@gmail.com'])


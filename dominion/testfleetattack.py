from newdominion.dominion.models import *

fleets = Fleet.objects.all()
strengths = []
for f in fleets:
  strength = 0
  for t in shiptypes:
    strength += shiptypes[t]['att'] * getattr(f,t)
  strengths.append(strength)
strengths.sort()
print strengths


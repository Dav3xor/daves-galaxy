from newdominion.dominion.models import *

p = Planet.objects.get(id=419896)

connections = p.makeconnections()
print str(connections)

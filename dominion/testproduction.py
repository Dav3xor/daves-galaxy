from newdominion.dominion.models import *


u = User.objects.get(id=1)
p = Planet.objects.get(id=10000)
f = Fleet(arcs=1, sector=p.sector)
p.owner = u
p.resources = None
p.planetattributes = None
f.homeport = p
f.owner = p.owner
f.x = p.x
f.y = p.y

output = []
for i in productionrates:
  output.append(i[:6] + "\t")
print ''.join(output)
print "------------------------------------------------------------"

if 1:
  p.colonize(f,output)
  for i in range(50):
    output =  []
    p.society = i 
    for j in productionrates:
      output.append(str(int(getattr(p.resources,j)))[:7]+"\t")
    print ''.join(output)
    p.doturn(output)
  print "------------------------------------------------------------"

  p.populate()
  for i in range(50):
    output =  []
    p.society = i+50
    for j in productionrates:
      output.append(str(int(getattr(p.resources,j)))[:7]+"\t")
    print ''.join(output)
    p.doturn(output)
  print "------------------------------------------------------------"

if 0:
  f.arcs = 1
  p.colonize(f,output)
  for i in range(50):
    output =  []
    p.society = i
    #print p.getprices()
    for j in productionrates:
      output.append(str(int(getattr(p.resources,j)))[:7]+"\t")
    print ''.join(output)
    #print p.buildableships()
    p.doturn(output)
  print "------------------------------------------------------------"


  f.arcs = 1
  p.colonize(f,output)

  a = PlanetAttribute(planet=p,attribute="people-advantage",value="1.015")
  a.save()

  for i in range(50):
    output =  []
    p.society = i
    #print p.getprices()
    for j in productionrates:
      output.append(str(int(getattr(p.resources,j)))[:7]+"\t")
    print ''.join(output)
    #print p.buildableships()
    p.doturn(output)
  print "------------------------------------------------------------"

  if 0:
    p.populate()
    for i in range(50):
      output =  []
      p.society = i+50
      print p.getprices()
      #print p.buildableships()
      p.doturn(output)
    print "------------------------------------------------------------"
  #f.delete()
  a.delete()
  p.owner = None
  p.resources.delete()
  p.save()

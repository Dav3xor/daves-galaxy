# to get pychart to output svg, use the following:
# export PYCHART_OPTIONS="output=blah.svg"

from newdominion.dominion.models import *
from pychart import *

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

plotvals = []
labels = []

output = []
for i in productionrates:
  output.append(i[:6] + "\t")
print ''.join(output)
print "------------------------------------------------------------"

if 1:
  p.colonize(f,output)
  for i in range(200):
    vals = [i]
    output =  []
    p.society = i 
    for j in productionrates:
      output.append(str(int(getattr(p.resources,j)))[:7]+"\t")
      vals.append(float(getattr(p.resources,j)))
    print ''.join(output)
    p.doturn(output)
    plotvals.append(vals)
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

  theme.use_color = 1
  theme.reinitialize()
  xaxis = axis.X(format="/a-60/hL%d", tic_interval = 20, label="Society Level")
  yaxis = axis.Y(tic_interval = 20, label="Surplus On Hand")
  ar = area.T(size=(500,200),
              x_axis=xaxis, 
              y_axis=yaxis, 
              y_coord = log_coord.T(), 
              y_range=(1.000,None),
              x_range=(0.0001,None))
  j = 1 
  for i in productionrates:
    ar.add_plot(line_plot.T(label=i, data=plotvals, ycol=j))
    j+=1
  ar.draw()
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

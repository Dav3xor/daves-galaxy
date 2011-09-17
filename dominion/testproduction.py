# to get pychart to output svg, use the following:
# export PYCHART_OPTIONS="output=blah.svg"

from newdominion.dominion.models import *
from pychart import *


import doctest
from django.test.utils import setup_test_environment
from django.test.utils import teardown_test_environment
from django.db import connection
from django.conf import settings
verbosity = 1
interactive = True
setup_test_environment()


settings.DEBUG = False    
old_name = settings.DATABASE_NAME
connection.creation.create_test_db(verbosity, autoclobber=not interactive)

buildinstrumentalities()
u = User(username="makeconnections")
u.save()
r = Manifest()
r.save()
s = Sector(key=buildsectorkey(675,625),x=675,y=625)
s.save()
p = Planet(resources=r, society=1,owner=u, sector=s,
           x=675, y=625, r=.1, color=0x1234)
p.save()

pl = Player(user=u, capital=p, color=112233)
pl.lastactivity = datetime.datetime.now()
pl.save()

f = Fleet(arcs=1, sector=p.sector)
p.resources = None
p.planetattributes = None
p.save()
f.homeport = p
f.owner = p.owner
f.x = p.x
f.y = p.y

plotvals = []
labels = []

output = ['society']
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
    output.append(str(i)+"\t")
    for j in productionrates:
      output.append(str(int(getattr(p.resources,j)))[:7]+"\t")
      vals.append(float(getattr(p.resources,j)))
    print ''.join(output)
    p.doturn(output)
    plotvals.append(vals)
  print "------------------------------------------------------------"
if 1:
  p.populate()
  for i in range(50):
    output =  []
    p.society = i+50
    output.append(str(p.society)+"\t")
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
  #ar.draw()
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



connection.creation.destroy_test_db(old_name, verbosity)
teardown_test_environment()


from newdominion.dominion.models import *

counter = 0
f = Fleet.objects.all().select_related('owner','destination').iterator()
for i in f:
  if i.disposition == 1 and i.numcombatants() > 0:
    i.disposition = 5
    i.save()
    counter += 1
    if not counter % 100:
      print str(counter)
  """
  if i.sector_id != buildsectorkey(i.x,i.y):
    i.sector_id = buildsectorkey(i.x,i.y)
    i.save()
    print "wrong sector id=" + str(i.id) + " --> " + str(i.sector_id) + "--" + str(buildsectorkey(i.x,i.y))
  if i.destination and i.source and \
     i.x==i.dx and i.y==i.dy and \
     i.disposition==8 and \
     i.speed==0 and \
     i.inport():
    #print "stuck trade fleet? id="+str(i.id) + " - " + str(i.owner.username)
    report = []
    i.dotrade(report,i.inport())
    print report
    counter += 1
  """
print "numstuck = " + str(counter)

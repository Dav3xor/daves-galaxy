from newdominion.dominion.models import *

counter = 0

print "loading tables"
localcache['upgrades']       = allupgrades()
localcache['attributes']     = allattributes()
localcache['connections']    = allconnections()
localcache['competition']    = allcompetition()
localcache['players']        = allplayers()
localcache['planets']        = allplanetsbysector()
localcache['costs']          = {}
localcache['planetarrivals'] = {}
localcache['arrivals']       = []
print "done"
f = Fleet.objects\
         .filter(Q(merchantmen__gt=0)|Q(bulkfreighters__gt=0))\
         .select_related('owner','destination','trade_manifest',
                         'route','homeport','destination','source')
total = f.count()
for i in f.iterator():
  counter += 1
  if i.destination and i.source and \
     i.x==i.dx and i.y==i.dy and \
     i.disposition==8 and \
     i.speed==0 and \
     i.inport():
    #print "stuck trade fleet? id="+str(i.id) + " - " + str(i.owner.username)
    print str(counter) + "(" + str(total) + ")"
    report = []
    if i.owner == None:
      continue
    i.dotrade(report,i.inport())
  #else:
  #  print "-"
print "numstuck = " + str(counter)

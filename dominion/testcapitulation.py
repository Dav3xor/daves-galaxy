from newdominion.dominion.models import *

numcruisers = [1,5,10,50,100,500,1000,5000]
society = [1,5,10,25,50,100,150,200]
population = [2000, 10000, 50000, 100000, 500000, 1000000, 5000000, 16000000]
output = []

f = Fleet(cruisers=1)

line = "\t"
for i in xrange(8):
  line += "%d\t" % society[i]
output.append(line)

line = "\t"
for i in xrange(8):
  line += "%d\t" % population[i]
output.append(line)
output.append("-----------------------------------------------------------------------------")
for i in xrange(8):
  line = "%d\t" % numcruisers[i]
  f.cruisers = numcruisers[i]
  for j in xrange(8):
    line += "%2.4f\t" % f.capitulationchance(society[j], population[j])
  output.append(line)   

print '\n'.join(output)

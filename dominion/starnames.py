import random
from newdominion.dominion.models import *

greek = ['Alpha', 'Nu',
         'Beta', 'Xi',
         'Gamma', 'Omicron',
         'Delta', 'Pi',
         'Epsilon', 'Rho',
         'Zeta', 'Sigma',
         'Eta', 'Tau',
         'Theta', 'Upsilon',
         'Iota', 'Phi',
         'Kappa', 'Chi',
         'Lambda', 'Psi',
         'Mu', 'Omega']

firstsyl = ['Queez','Arse','Andro','Aqua','Auri','Boo',
            'Cae', 'Canis ', 'Cancer ', 'Cari', 'Cassio',
            'Cecilae ', 'Ceti ', 'Cepheus ', 'Ceph','Circ',
            'Delph','Draco', 'Draconis ','Eridani ','Eri',
            'Forn','Indi','Mono','Octans','Ophiuchi', 
            'Phoense','Picto','Pictoris ','Pixis ']

lastsyl = ['tooine', 'fleem','meda','rius','gae','norg',
           'tes','lum','nae','peia','eus','inus','bae','ini',
           'inus','ax','ceros','nus','nis','ris']

secondword = ['Major', 'Minor', 'Majoris', 'Minoris', 
              'Australis', 'Borealis','Cygni','Librae',
              'Leporis','Lyrae','Octantis','Pavonis','Austrinus',
              'Reticulum'] 

def starname():
  g = random.randint(0,len(greek)-1)
  f = random.randint(0,len(firstsyl)-1)
  l = random.randint(0,len(lastsyl)-1)
  s = random.randint(0,len(secondword)-1)

  num = random.randint(0,7)
  numpresent = random.randint(0,100) / 80

  output = ""
  if ' ' in firstsyl[f]:
    # firstcyl is actually a word...
    output = greek[g] + " " + firstsyl[f] + secondword[s]
  else:
    output = greek[g] + " " + firstsyl[f] + lastsyl[l]

  if numpresent:
    output+=" " + str(num)
  return output

counter = 0
while Planet.objects.filter(name="X").count() > 0:
  for planet in Planet.objects.filter(owner=None, name="X")[:1000]:
    planet.name=starname()
    planet.save()
    counter+=1
    if counter%1000 == 0:
      print str(counter)

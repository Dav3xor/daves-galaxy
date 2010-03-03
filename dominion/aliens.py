import glob
import random
import sys

modpath = sys.modules['newdominion.dominion.aliens'].__file__
modpath = '/'.join(modpath.split('/')[:-1]) + "/aliens/"

# Body Definitions
# hx,hy = head x,y
# lx,ly = leftarm x,y
# rx,ry = rightarm x,y
# fx,fy = feet x,y
bodydefs = [ {'hx':60, 'hy':77, 'lx':40, 'ly':85, 'rx':78, 'ry':85, 'fx':67, 'fy':120}, # slug with tail
             {'hx':58, 'hy':75, 'lx':45, 'ly':79, 'rx':71, 'ry':79, 'fx':60, 'fy':120}, # mannequin

             {'hx':60, 'hy':75, 'lx':55, 'ly':80, 'rx':66, 'ry':80, 'fx':60, 'fy':118}, #hourglass

             {'hx':50, 'hy':65, 'lx':40, 'ly':70, 'rx':63, 'ry':70, 'fx':50, 'fy':110},
             {'hx':50, 'hy':65, 'lx':40, 'ly':70, 'rx':63, 'ry':70, 'fx':50, 'fy':110},
             {'hx':50, 'hy':65, 'lx':40, 'ly':70, 'rx':63, 'ry':70, 'fx':50, 'fy':110},
             {'hx':50, 'hy':65, 'lx':40, 'ly':70, 'rx':63, 'ry':70, 'fx':50, 'fy':110},
             {'hx':50, 'hy':65, 'lx':40, 'ly':70, 'rx':63, 'ry':70, 'fx':50, 'fy':110},
             {'hx':50, 'hy':65, 'lx':40, 'ly':70, 'rx':63, 'ry':70, 'fx':50, 'fy':110},
             {'hx':50, 'hy':65, 'lx':40, 'ly':70, 'rx':63, 'ry':70, 'fx':50, 'fy':110},
             {'hx':50, 'hy':65, 'lx':40, 'ly':70, 'rx':63, 'ry':70, 'fx':50, 'fy':110},
             {'hx':50, 'hy':65, 'lx':40, 'ly':70, 'rx':63, 'ry':70, 'fx':50, 'fy':110},
             {'hx':50, 'hy':65, 'lx':40, 'ly':70, 'rx':63, 'ry':70, 'fx':50, 'fy':110},
             {'hx':50, 'hy':65, 'lx':40, 'ly':70, 'rx':63, 'ry':70, 'fx':50, 'fy':110},
             {'hx':50, 'hy':65, 'lx':40, 'ly':70, 'rx':63, 'ry':70, 'fx':50, 'fy':110},
             {'hx':50, 'hy':65, 'lx':40, 'ly':70, 'rx':63, 'ry':70, 'fx':50, 'fy':110},
             {'hx':50, 'hy':65, 'lx':40, 'ly':70, 'rx':63, 'ry':70, 'fx':50, 'fy':110},
             {'hx':50, 'hy':65, 'lx':40, 'ly':70, 'rx':63, 'ry':70, 'fx':50, 'fy':110},
             {'hx':50, 'hy':65, 'lx':40, 'ly':70, 'rx':63, 'ry':70, 'fx':50, 'fy':110},
             {'hx':50, 'hy':65, 'lx':40, 'ly':70, 'rx':63, 'ry':70, 'fx':50, 'fy':110},
             {'hx':50, 'hy':65, 'lx':40, 'ly':70, 'rx':63, 'ry':70, 'fx':50, 'fy':110},
             {'hx':50, 'hy':65, 'lx':40, 'ly':70, 'rx':63, 'ry':70, 'fx':50, 'fy':110} ]




# first, we load all the body parts into their own arrays...


# load heads...
heads = []
bodies = []
arms = []
feet = []

for headfile in glob.glob(modpath+"head*.svg"):
  f = open(headfile,'r')
  heads.append(f.read())


bodyfiles = glob.glob(modpath+"body*.svg")
bodyfiles.sort()
for bodyfile in bodyfiles:
  f = open(bodyfile,'r')
  bodies.append(f.read())

for armfile in glob.glob(modpath+"leftarm*.svg"):
  f = open(armfile,'r')
  leftarm = f.read()
  armfile = armfile.replace("left","right")
  f = open(armfile,'r')
  rightarm = f.read()
  arms.append({'left':leftarm,'right':rightarm})
  


for feetfile in glob.glob(modpath+"feet*.svg"):
  f = open(feetfile,'r')
  feet.append(f.read())


def makealien(seed, color):
  random.seed()
  # figure out which arms we want to use.
  # we have to figure this out beforehand, because
  # they both have to be the same, except once in a 
  # while, when we just pick 2 different arms for the
  # heck of it.
  leftarmindex = random.randint(0,len(arms)-1)
  rightarmindex = leftarmindex
  if random.randint(0,5) ==3:
    rightarmindex = random.randint(0,len(arms)-1)
  bodyindex = random.randint(0,len(bodies)-1)
  bd = bodydefs[bodyindex]
  alien = (
           '<g transform="translate(%d,%d)">%s</g>' % (bd['lx'], bd['ly'], arms[leftarmindex]['left'])  +  
           '<g transform="translate(%d,%d)">%s</g>' % (bd['fx'], bd['fy'], random.choice(feet))     +
           '<g transform="translate(60,75)">%s</g>' % (bodies[bodyindex])                       +
           '<g transform="translate(%d,%d)">%s</g>' % (bd['rx'], bd['ry'], arms[rightarmindex]['right']) +
           '<g transform="translate(%d,%d)">%s</g>' % (bd['hx'], bd['hy'], random.choice(heads))
           )



  R = (color >> 16)
  G = (color >> 8)%256
  B = color%256

  # if the color is really bright, tone it down a bit
  # so we can have a highlight color...
  if R > 203 or G > 203 or B > 203:
    R = int(R/1.25)
    G = int(G/1.25)
    B = int(B/1.25)

  basecolor = (R<<16) + (G<<8) + B

  highlight = (int(R*1.25)<<16) + (int(G*1.25)<<8) + int(B*1.25)
  shadow = (int(R/1.25)<<16) + (int(G/1.25)<<8) + int(B/1.25)
  alien=alien.replace(':#404040;',':#'+hex(basecolor)[2:]+';')
  alien=alien.replace(':#202020;',':#'+hex(shadow)[2:]+';')
  alien=alien.replace(':#808080;',':#'+hex(highlight)[2:]+';')
  return alien


import glob
import random

# Body Definitions
# hx,hy = head x,y
# lx,ly = leftarm x,y
# rx,ry = rightarm x,y
# fx,fy = feet x,y
bodydefs = [ {'hx':50, 'hy':67, 'lx':30, 'ly':75, 'rx':68, 'ry':75, 'fx':57, 'fy':110}, # slug with tail
             {'hx':48, 'hy':65, 'lx':35, 'ly':69, 'rx':61, 'ry':69, 'fx':50, 'fy':110}, # mannequin

             {'hx':50, 'hy':65, 'lx':45, 'ly':70, 'rx':56, 'ry':70, 'fx':50, 'fy':108}, #hourglass

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



header = """
<svg
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   version="1.0"
   width="100"
   height="150"
   id="svg2512">
  <path stroke="black" fill="none" d="m 0 0 l 100 0 l 0 150 l -100 0 z" stroke-width="2" />
"""

footer = "</svg>"

# first, we load all the body parts into their own arrays...


# load heads...
heads = []
bodies = []
arms = []
feet = []

for headfile in glob.glob("aliens/head*.svg"):
  f = open(headfile,'r')
  heads.append(f.read())


bodyfiles = glob.glob("aliens/body*.svg")
bodyfiles.sort()
for bodyfile in bodyfiles:
  f = open(bodyfile,'r')
  bodies.append(f.read())

for armfile in glob.glob("aliens/leftarm*.svg"):
  f = open(armfile,'r')
  leftarm = f.read()
  armfile = armfile.replace("left","right")
  f = open(armfile,'r')
  rightarm = f.read()
  arms.append({'left':leftarm,'right':rightarm})
  


for feetfile in glob.glob("aliens/feet*.svg"):
  f = open(feetfile,'r')
  feet.append(f.read())


def makealien(seed, color):
  random.seed(seed.__hash__())
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
  print str(type(heads))
  alien = (header +
           '<g transform="translate(%d,%d)">%s</g>' % (bd['lx'], bd['ly'], arms[leftarmindex]['left'])  +  
           '<g transform="translate(%d,%d)">%s</g>' % (bd['fx'], bd['fy'], random.choice(feet))     +
           '<g transform="translate(50,65)">%s</g>' % (bodies[bodyindex])                       +
           '<g transform="translate(%d,%d)">%s</g>' % (bd['rx'], bd['ry'], arms[rightarmindex]['right']) +
           #'<g transform="translate(%d,%d)">%s</g>' % (bd['hx'], bd['hy'], random.choice(heads))    +
           '<g transform="translate(%d,%d)">%s</g>' % (bd['hx'], bd['hy'], str(type(heads)))    +
           footer)



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



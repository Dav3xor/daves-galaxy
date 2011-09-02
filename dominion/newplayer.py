#!/usr/bin/python2
import sys
from newdominion.dominion.models import *
from django.conf import settings
import time

email = """
Greetings New Player:

Alright, your account is ready, please go to http://www.davesgalaxy.com
to play.  Have fun!

account name: %s

To learn how to play, take a look at the pages under the help tab
inside of the game, they're quite helpful.  If you have any questions
that are not answered by the in game help, please send me an email at
Dav3xor@gmail.com, I'm more than happy to be of assistance.

-- Dave
"""

email2 = """
New Player: %s (%d)
Creation Time: %10.1fs
"""

email3 = """
New Player: %s (%d)

FAILED

reason:

%s
"""

email4 = """
could not find player id: %d

reason: 

%s
""" 



try:
  userid = int(sys.argv[1])
  account = User.objects.get(id=userid)
except:
  error = sys.exc_info()[0]
  email4 = email4 % (userid, error)
  if settings.DEBUG == False:
    send_mail("New Player Error!",
              email4,
              "dave@davesgalaxy.com",
              ["Dav3xor@gmail.com"])
  else:
    print email4
  exit()

try:
  starttime = time.time()
  player = Player(lastactivity=datetime.datetime.now(), user = account)
  player.create()
  player.save()
  endtime = time.time()
  elapsedtime = endtime-starttime
  email = email % (account.username)
  email2 = email2 % (account.username,userid,elapsedtime) 
  if settings.DEBUG == False:
    send_mail("Dave's Galaxy Registration Complete", 
              email,
              'dave@davesgalaxy.com', 
              [account.email])
    send_mail("New DG User Created", 
              email2,
              'dave@davesgalaxy.com', 
              ['Dav3xor@gmail.com'])
  else:
    print email
    print "---"
    print email2
except:
  error = sys.exc_info()[0]
  email3 = email3 % (account.username, userid, error)
  if settings.DEBUG == False:
    send_mail("New Player Error!",
              email3,
              "dave@davesgalaxy.com",
              ["Dav3xor@gmail.com"])
  else:
    print email3



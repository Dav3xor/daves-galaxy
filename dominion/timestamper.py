#!/usr/bin/python2


from newdominion.dominion.models import *
import time

r = RedisQueueServer('timestamper')
cursor = connection.cursor()
waittime = 300

while 1:
  time.sleep(waittime)
  stamps = r.getTimeStamps()
  if len(stamps):
    print "---"
    players = Player.objects\
                    .filter(user__id__in=stamps.keys())\
                    .values_list('user__id','id')
    for p in players:
      query = ("UPDATE dominion_player SET lastactivity = '" +
               str(stamps[str(p[0])]) + "' WHERE id = '" + str(p[1]) + "';")
      print query
      cursor.execute(query)
      transaction.commit_unless_managed() 

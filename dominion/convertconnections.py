#!

from newdominion.dominion.models import *
from django.db import connection
from pprint import pprint

cursor = connection.cursor()
cursor.execute("""SELECT * FROM dominion_planet_connections;""")
for row in cursor.fetchall():
  p1 = Planet.objects.get(id=row[1])
  p2 = Planet.objects.get(id=row[2])
  p1.buildconnection(p2)

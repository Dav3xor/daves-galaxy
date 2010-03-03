from newdominion.dominion.aliens import makealien 
from newdominion.dominion.models import *




users = User.objects.all()
for u in users:
  p = u.get_profile()

  p.appearance = makealien(u.username, 0xffff00)
  p.save()

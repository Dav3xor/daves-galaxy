from newdominion.dominion.models import *
from newdominion.dominion.util import *
from newdominion.dominion.forms import *
from django.template.loader import render_to_string

class Menu():
  def __init__(self):
    self.menu = []
    self.title = ""
  def additem(self, id, title, url):
    # id = object id, fleet #12345
    # title = "MANAGE PLANET"
    item = {'type': 'item', 'id': id, 'title': title, 'url': url}
    self.menu.append(item)
  def addfleet(self, fleet, user):
    item = {'type': 'fleet', 'fleet': fleet, 'user': user}
    self.menu.append(item)
  def addplanet(self, planet):
    item = {'type': 'planet', 'planet': planet}
    self.menu.append(item)
  def addpostitem(self, id, title, url):
    item = {'type': 'postitem', 'id': id, 'title': title, 'url': url}
    self.menu.append(item)
  def addline(self):
    item = {'type': 'line'}
    self.menu.append(item)
  def addhelp(self):
    item = {'type': 'helpitem'}
    self.menu.append(item)
  def addheader(self, text):
    item = {'type': 'header', 'header': text}
    self.menu.append(item)
  def addtitle(self, text):
    self.title = text
  def addmove(self, fleet):
    item = {'type':'movefleet', 'id': 'movefleet'+str(fleet.id), 
            'fleet':str(fleet.id), 'x':str(fleet.x), 'y':str(fleet.y)}
    self.menu.append(item)
  def addontoroute(self, fleet, route):
    item = {'type':'ontoroute', 'id': 'ontoroute'+str(route.id), 
            'fleet':str(fleet.id), 'route':str(route.id), 'name':route.name}
    
    if route.circular:
      item['type'] = 'ontocircularroute'
      item['x'] = fleet.x
      item['y'] = fleet.y

    self.menu.append(item)
  def addrenameroute(self, route):
    item = {'type':'renameroute', 'id': 'renameroute'+str(route.id),
            'route': route, 'name':route.name}
    self.menu.append(item)
  def addnamedroute(self, planet=None):
    if planet:
      x = planet.x
      y = planet.y
      planetid = planet.id
    else:
      x = 0
      y = 0
      planetid = -1 
    item = {'type':'namedroute', 'id': 'namedroute'+str(planetid), 
            'planet':str(planetid), 'x':str(x), 'y':str(y)}
    self.menu.append(item)
  def addscrap(self, fleet):
    port = fleet.inport()
    if port and fleet.owner and\
       fleet.owner\
            .get_profile()\
            .getpoliticalrelation(port.owner.get_profile()) != 'enemy':
      item = {'type':'scrapfleet', 'id': 'scrapfleet'+str(fleet.id), 
              'fleet': str(fleet.id)}
      self.menu.append(item)
  def render(self):
    context = {'items': self.menu,
               'title': self.title}
    return render_to_string('menu.xhtml',context)


def moveto(x,y):
  x = "<script>movemenu("+str(x)+","+str(y)+");</script>"
  return x

def buildform(form, context): #title, action, formname, tabid):
  context['form'] = form
  #formname, action, title, form, tabid
  #context = {'name':formname, 'action': action, 'title':title, 'form': form, 'tabid': tabid}
  return render_to_string('form.xhtml', context)

def makefleetadminform(fleet):
  faf = FleetAdminForm(instance=fleet)
  faf.fields['disposition'].choices = fleet.validdispositions()
  return faf


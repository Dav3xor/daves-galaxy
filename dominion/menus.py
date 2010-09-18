from newdominion.dominion.models import *
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
  def addline(self):
    item = {'type': 'line'}
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
  def addscrap(self, fleet):
    if fleet.inport():
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


from newdominion.dominion.models import *
from newdominion.dominion.forms import *

def listfromdict(dict):
  list = []
  for key in dict:
    list.append([key+":",str(dict[key])])
  return list

def moveto(x,y):
  x = "<script>movemenu("+str(x)+","+str(y)+");</script>"
  return x

def buildfleetlist(planet,id):
  l = Fleet.objects.filter((Q(homeport=planet)|Q(destination=planet))&(Q(owner=planet.owner)))
  counter = 0
  x="<ul>"
  for s in l:
    if getdistanceobj(s,planet) < .05:
      counter += 1
      x+='<li onmouseover="zoomcircleid(2.0,\'f'+str(s.id)+'\');" '
      x+='onmouseout="zoomcircleid(.5,\'f'+str(s.id)+'\');" '
      x+='onmouseup="zoomcircleid(.5,\'f'+str(s.id)+'\'); '
      x+='handlemenuitemreq(event, \'fleets\',\''+id+'\','+str(s.id)+ ')">'
      x+= s.shortdescription() + '</li>'
  x+="</ul>"
  if counter > 0:
    return '<span style="margin-left: 10px; color: white;">Fleets in Port</span>' + x
  else:
    return ""

def buildmenu(l,id,type):
  x="<ul>\n"
  for s in l:
    x+='<li onmouseup="handlemenuitemreq(event, \''+type+'\',\''+s[0]+'\',\''+str(id)+'\')">'+s[1]+"</li>\n"
  x+="</ul>\n"
  return x

def buildform(form, action, formname):
  x='<form method="POST" name="'+formname+'" \nonsubmit="sendform(this,\''+action+'\');return false;">\n<table>\n'
  x+=form.as_table()
  x+='<tr><td/>'
  x+='<td><button width="100%" value="Submit" type="submit">---Submit---</button>'
  x+='</td></tr></table></form>'
  return x

def buildul(l,id,handler):
  x="<ul>"
  for s in l:
    x+="<li>"+s+"</li>"
  x+="</ul>"
  return x

def build2col(l,id,handler):
  x="<table>"
  for s in l:
    x+="<tr><td style='color: white;'>"+s[0]+"</td><td>"+s[1]+"</td></tr>"
  x+="</table>"
  return x
def movefleetmenuitem(fleet):
  x='<ul><li onmouseup="rubberbandfromfleet('+str(fleet.id)+','+\
     str(fleet.x)+','+str(fleet.y)+')">MOVE</li></ul>'
  return x

def scrapfleetmenuitem(fleet):
  x = " "
  if fleet.inport():
    x='<ul><li onmouseup="newmenu(\'/fleets/'+str(fleet.id)+'/scrap/\',\'GET\');">SCRAP</li></ul>'
  else:
    x=" "
  return x

def makefleetadminform(fleet):
  faf = FleetAdminForm(instance=fleet)
  faf.fields['disposition'].choices = fleet.validdispositions()
  return faf

fleetmenus = {
  'root': {'type': 'menu',
           'eval': """buildmenu([['info','Info']],fleet.id,'fleets')+\
                      movefleetmenuitem(fleet)+scrapfleetmenuitem(fleet)+\
                      '<hr width="100%"/>'+\
                      buildform(makefleetadminform(fleet),\
                                '/fleets/'+str(fleet.id)+"/admin/",\
                                "adminform")"""
          },
  'admin': { 'type': 'form', 'form': FleetAdminForm,\
             'eval': """buildform(makefleetadminform(fleet)),\
                                '/fleets/'+str(fleet.id)+"/admin/",\
                                "adminform")"""}
  }

planetmenus = {
  'root': {'type': 'menu', \
           'eval': "buildmenu([['info','INFO'],['fleets','FLEETS'],['manage','MANAGE PLANET']], \
             planet.id,'planets')"}, \
  'info': { 'type': 'info', \
            'eval': "'<h1>PLANET INFO:</h1><hr width=\"100%\" />' + build2col([\
              ['Name:',str(planet.name)],\
              ['Owner:',str(planet.owner)],\
              ]+\
              ([] if not planet.resources else listfromdict(planet.resources.__dict__)),\
              planet.id,'handleplanetmenuitemreq')"},\
  'fleets': { 'type': 'menu',\
              'eval': "buildmenu([['buildfleet','BUILD FLEET']],planet.id,'planets')+\
                '<hr width=\"100%\" />' +\
                buildfleetlist(planet,'root')"},\
  'manage': { 'type': 'form', 'form': PlanetManageForm,\
               'eval': 'moveto(100,120) + buildform(PlanetManageForm(instance=planet),\
                 "/planets/"+str(planet.id)+"/manage/","manageform")'},\
  'addfleet': { 'type': 'form', 'form': AddFleetForm,\
                'eval': 'buildform(AddFleetForm(),\
                "/planets/"+str(planet.id)+"/addfleet/","addfleetform") +\
                "Quatloos Available: <h1>" + str(5 if planet.resources == None else planet.resources.quatloos) +"</h1>"'}\
  }




menuglobals = {'buildul': buildul, 
                 'build2col': build2col,
                 'listfromdict': listfromdict,
                 'buildmenu': buildmenu,
                 'buildform': buildform,
                 'moveto': moveto,
                 'buildfleetlist': buildfleetlist,
                 'PlanetManageForm': PlanetManageForm,
                 'Fleet': Fleet,
                 'Q': Q,
                 'FleetAdminForm': FleetAdminForm,
                 'movefleetmenuitem': movefleetmenuitem,
                 'scrapfleetmenuitem': scrapfleetmenuitem,
                 'makefleetadminform': makefleetadminform,
                 'AddFleetForm': AddFleetForm}


if 0:
  planet = Planet.objects.get(id="100000") 
  fleet = Fleet.objects.get(id="1")
  menuglobals['planet'] = planet
  menuglobals['fleet'] = fleet
  for key in planetmenus:
    menu = planetmenus[key]
    print "key:      " + key
    print "type:     " + menu['type']
    print "estring:  " + menu['eval']
    print "output:"
    print eval(menu['eval'],menuglobals)
    print "---"
  

  for key in fleetmenus:
    menu = fleetmenus[key]
    print "key:      " + key
    print "type:     " + menu['type']
    print "estring:  " + menu['eval']
    print "output:"
    print eval(menu['eval'],menuglobals)
    print "---"






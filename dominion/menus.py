from newdominion.dominion.models import *
from newdominion.dominion.forms import *

def listfromdict(dict):
  list = []
  for key in dict:
    list.append([key+":",str(dict[key])])
  return list


def buildfleetlist(l,id):
  x="<ul>"
  for s in l:
    print x
    x+='<li onmouseup="handlemenuitemreq(\'fleets\',\''+id+'\','+str(s.id)+ ')">Fleet #'\
       +str(s.id).upper()+", "+ str(s.numships())+" ships</li>"
  x+="</ul>"
  return x

def buildmenu(l,id):
  x="<ul>\n"
  for s in l:
    x+='<li onmouseup="handlemenuitemreq(\'planets\',\''+s+'\',\''+str(id)+'\')">'+s.upper()+"</li>\n"
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

fleetmenus = {
  'root': {'type': 'menu',
           'eval': """buildmenu(['info','disposition','split'],fleet.id)+\
                      movefleetmenuitem(fleet)+\
                      '<hr width="100%"/>'+\
                      buildform(FleetAdminForm(instance=fleet),\
                                '/fleets/'+str(fleet.id)+"/admin/",\
                                "adminform")"""
          },
  'admin': { 'type': 'form', 'form': FleetAdminForm,\
             'eval': """buildform(FleetAdminForm(instance=fleet),\
                                '/fleets/'+str(fleet.id)+"/admin/",\
                                "adminform")"""}
  }

planetmenus = {
  'root': {'type': 'menu', \
           'eval': "buildmenu(['info','fleets','manage'], \
             planet.id)"}, \
  'info': { 'type': 'info', \
            'eval': "'<h1>PLANET INFO:</h1><hr width=\"100%\" />' + build2col([\
              ['Name:',str(planet.name)],\
              ['Owner:',str(planet.owner)],\
              ]+\
              ([] if not planet.resources else listfromdict(planet.resources.__dict__)),\
              planet.id,'handleplanetmenuitemreq')"},\
  'fleets': { 'type': 'menu',\
              'eval': "buildmenu(['buildfleet','scrap'],planet.id)+\
                '<hr width=\"100%\" />' +\
                buildfleetlist(planet.home_port.all(),\
                'root')"},\
  'manage': { 'type': 'form', 'form': PlanetManageForm,\
               'eval': 'buildform(PlanetManageForm(instance=planet),\
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
                 'buildfleetlist': buildfleetlist,
                 'PlanetManageForm': PlanetManageForm,
                 'FleetAdminForm': FleetAdminForm,
                 'movefleetmenuitem': movefleetmenuitem,
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






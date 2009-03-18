# Create your views here.
from django.template import Context, loader
from newdominion.dominion.models import *
from newdominion.dominion.forms import *
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from newdominion.dominion.menus import *

def fleetmenu(request,fleet_id,action):
  fleet = get_object_or_404(Fleet, id=int(fleet_id))
  menuglobals['fleet'] = fleet
  print "--> " + str(request.POST)
  if request.POST:
    if action == 'movetoloc':
      fleet.gotoloc(request.POST['x'],request.POST['y']);
    elif action == 'movetoplanet': 
      planet = get_object_or_404(Planet, id=int(request.POST['planet']))
      fleet.gotoplanet(planet)
    else:
      form = fleetmenus[action]['form'](request.POST, instance=fleet)
      form.save()
    menu = eval(fleetmenus['root']['eval'],menuglobals)
    return render_to_response('planetmenu.xhtml', {'menu': menu}, mimetype='application/xhtml+xml')

  else:
    print "sfsaf"
    menu = eval(fleetmenus[action]['eval'],menuglobals)
    print "--"
    print menu
    print "--"
    return render_to_response('planetmenu.xhtml', {'menu': menu}, mimetype='application/xhtml+xml')

def planetmenu(request,planet_id,action):
  planet = get_object_or_404(Planet, id=int(planet_id))
  menuglobals['planet'] = planet
  print "--> " + str(request.POST)
  if request.POST:
    if action == 'addfleet':
      form = planetmenus[action]['form'](request.POST)
      fleet = form.save(commit=False)
      fleet.homeport = planet
      fleet.x = planet.x
      fleet.y = planet.y
      fleet.sector = planet.sector
      fleet.owner = planet.owner
      fleet.save()
    else:
      form = planetmenus[action]['form'](request.POST, instance=planet)
      form.save()
    menu = eval(planetmenus['root']['eval'],menuglobals)
    return render_to_response('planetmenu.xhtml', {'menu': menu}, mimetype='application/xhtml+xml')
  else:
    menu = eval(planetmenus[action]['eval'],menuglobals)
    return render_to_response('planetmenu.xhtml', {'menu': menu}, mimetype='application/xhtml+xml')

def sector(request, sector_id):
  x = int(sector_id)/1000*5
  y = int(sector_id)%1000*5
  sector = get_object_or_404(Sector, key=sector_id) 
  planets = sector.planet_set.all()
  t = loader.get_template('show.xhtml')
  context = {'sector': sector, 'planets': planets, 'viewable': (x,y,5,5)}
  return render_to_response('show.xhtml', context, 
                             mimetype='application/xhtml+xml')

def setextents(x,y,extents):
  x *= 5
  y *= 5
  if x < extents[0]:
    extents[0] = x
  if x > extents[2]:
    extents[2] = x
  if y < extents[1]:
    extents[1] = y
  if y > extents[3]:
    extents[3] = y
  return extents


def testforms(request):
  fleet = Fleet.objects.get(pk=1)
  form = AddFleetForm(instance=fleet)
  return render_to_response('form.xhtml',{'form':form})

def playermap(request, player_id):
  player = get_object_or_404(Player, name=player_id)
  sectors = Sector.objects.filter(planet__owner__name=player_id)
  planets = []
  fleets = []
  allsectors = []
  afform = AddFleetForm(auto_id=False);
  for sector in sectors:
    if sector.key not in allsectors:
      allsectors.append(sector.key)

    testsector = (sector.x-1)*1000 + sector.y
    if testsector not in allsectors:
      allsectors.append(testsector)

    testsector = (sector.x-1)*1000 + sector.y-1
    if testsector not in allsectors:
      allsectors.append(testsector)

    testsector = (sector.x-1)*1000 + sector.y+1
    if testsector not in allsectors:
      allsectors.append(testsector)

    testsector = (sector.x)*1000 + sector.y-1
    if testsector not in allsectors:
      allsectors.append(testsector)

    testsector = (sector.x)*1000 + sector.y+1
    if testsector not in allsectors:
      allsectors.append(testsector)

    testsector = (sector.x+1)*1000 + sector.y-1
    if testsector not in allsectors:
      allsectors.append(testsector)

    testsector = (sector.x+1)*1000 + sector.y
    if testsector not in allsectors:
      allsectors.append(testsector)
    
    testsector = (sector.x+1)*1000 + sector.y+1
    if testsector not in allsectors:
      allsectors.append(testsector)

  extents = [2001,2001,-1,-1]
  sectors = Sector.objects.filter(key__in=allsectors)
  for sector in sectors:
    for fleet in sector.fleet_set.all():
      fleets.append(fleet)  
    for planet in sector.planet_set.all():
      if planet.owner == player:
        planet.highlight = "red"
      else:
        planet.highlight = 0 
      planets.append(planet)
    extents=setextents(sector.x,sector.y,extents)
  extent = 0
  if extents[2]-extents[0] > extents[3]-extents[1]:
    extent = extents[2]-extents[0]+5
  else:
    extent = extents[3]-extents[1]+5

  viewable = (extents[0],extents[1],extent,extent)
  context = {'fleets': fleets, 'planets': planets, 'viewable': viewable,
             'afform': afform}
  return render_to_response('show.xhtml', context,
                             mimetype='application/xhtml+xml')

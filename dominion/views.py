# Create your views here.
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from newdominion.dominion.models import *
from newdominion.dominion.help import *
from newdominion.dominion.forms import *
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render_to_response
from newdominion.dominion.menus import *
from django.core.paginator import Paginator
from django.db.models import Sum

from registration.forms import RegistrationForm
from registration.models import RegistrationProfile
from registration.views import register
from django.contrib.auth import authenticate, login

import simplejson
import sys
import datetime
import util



@login_required
def upgrades(request,planet_id,action='none',upgrade='-1'):
  curplanet = get_object_or_404(Planet,id=int(planet_id))
  if action=="start":
    newupgrade = PlanetUpgrade()
    newupgrade.start(curplanet,int(upgrade))
  if action=="scrap":
    scrapupgrade = PlanetUpgrade.objects.get(planet=curplanet, instrumentality__type=int(upgrade))
    if scrapupgrade:
      scrapupgrade.scrap()


  return HttpResponseRedirect('/planets/'+planet_id+'/upgradelist/')

@login_required
def fleetmenu(request,fleet_id,action):
  fleet = get_object_or_404(Fleet, id=int(fleet_id))
  clientcommand = ""
  
  request.user.get_profile().lastactivity = datetime.datetime.utcnow()
  request.user.get_profile().save()

  if fleet.owner != request.user and action != 'info':
    return HttpResponse("Nice Try.")
  menuglobals['fleet'] = fleet
  if request.POST:
    if action == 'movetoloc':
      fleet.gotoloc(request.POST['x'],request.POST['y']);
      clientcommand = {}
      clientcommand[str(fleet.sector.key)] = buildjsonsector(fleet.sector,request.user)
      return HttpResponse(simplejson.dumps(clientcommand))
    elif action == 'movetoplanet': 
      planet = get_object_or_404(Planet, id=int(request.POST['planet']))
      fleet.gotoplanet(planet)
      clientcommand = {}
      clientcommand[str(fleet.sector.key)] = buildjsonsector(fleet.sector,request.user)
      return HttpResponse(simplejson.dumps(clientcommand))
    else:
      form = fleetmenus[action]['form'](request.POST, instance=fleet)
      form.save()

      jsonresponse = {'killmenu':1, 'status': 'Disposition Changed'}
      return HttpResponse(simplejson.dumps(jsonresponse))


  else:
    menu = eval(fleetmenus[action]['eval'],menuglobals)
    jsonresponse = {'menu':menu}
    return HttpResponse(simplejson.dumps(jsonresponse))


      
def index(request):
  if request.POST and request.POST.has_key('usernamexor') and request.POST.has_key('passwordxor'):
    username = request.POST['usernamexor']
    password = request.POST['passwordxor']
    user = authenticate(username=username, password=password)
    if user is not None:
      if user.is_active:
        login(request, user)
        return HttpResponseRedirect('/view/')
        # Redirect to a success page.
      else:
        # Return a 'disabled account' error message
        return register(request, 
                        template_name='index.xhtml',
                        skip_validation=True,
                        extra_context={'loginerror': 'Account Disabled'})
    else:
      return register(request, 
                      template_name='index.xhtml',
                      skip_validation=True,
                      extra_context={'loginerror': 'Invalid Login'})
  return register(request, template_name='index.xhtml')

@login_required
def planetmenu(request,planet_id,action):
  planet = get_object_or_404(Planet, id=int(planet_id))
  menuglobals['planet'] = planet
  if planet.owner != request.user and action != 'info':
    return HttpResponse("Cheeky Devil")

  request.user.get_profile().lastactivity = datetime.datetime.utcnow()
  request.user.get_profile().save()

  if request.POST:
    form = planetmenus[action]['form'](request.POST, instance=planet)
    form.save()
    menu = eval(planetmenus['root']['eval'],menuglobals)
    jsonresponse = {'menu':menu}
    return HttpResponse(simplejson.dumps(jsonresponse))
  else:
    menu = eval(planetmenus[action]['eval'],menuglobals)
    jsonresponse = {'menu':menu}
    return HttpResponse(simplejson.dumps(jsonresponse))

@login_required
def sector(request, sector_id):
  x = int(sector_id)/1000*5
  y = int(sector_id)%1000*5
  sector = get_object_or_404(Sector, key=sector_id) 
  planets = sector.planet_set.all()
  t = loader.get_template('show.xhtml')
  context = {'sector': sector, 'planets': planets, 'viewable': (x,y,5,5)}
  return render_to_response('show.xhtml', context, 
                             mimetype='application/xhtml+xml')
@login_required
def preferences(request):
  user = request.user
  player = user.get_profile()
  if request.POST:
    if request.POST.has_key('color'):
      try:
        color = int(request.POST['color'].split('#')[-1], 16)
        player.color = "#" + hex(color)[2:]
        player.color = util.normalizecolor(player.color)
        player.save()
      except ValueError:
        print "bad preferences color"
        # do nothing
      jsonresponse = {'resetmap':1, 'killmenu':1, 'status': 'Preferences Saved'}
      return HttpResponse(simplejson.dumps(jsonresponse))
  context = {'user': user, 'player':player}  
  slider = render_to_string('preferences.xhtml', context)
  jsonresponse = {'slider':slider}
  return HttpResponse(simplejson.dumps(jsonresponse))

def buildjsonsector(s,curuser):
  planets = s.planet_set.all()
  fleets = curuser.inviewof.filter(sector=s)
  jsonsector = {}
  jsonsector['planets'] = {}
  jsonsector['fleets'] = {}
  
  for planet in planets:
    if planet.owner == curuser:
      jsonsector['planets'][planet.id] = planet.json(1)
    else:
      jsonsector['planets'][planet.id] = planet.json()


  for fleet in fleets:
    if fleet.owner == curuser:
      jsonsector['fleets'][fleet.id] = fleet.json(1)
    else:
      jsonsector['fleets'][fleet.id] = fleet.json()
  return jsonsector 


@login_required
def planets(request):
  tabs = [{'id':"allplanetstab",        'name': 'All',         'url':'/planets/list/all/1/'},
          {'id':"coloniesplanetstab",   'name': 'Colonies',    'url':'/planets/list/colonies/1/'},    
          {'id':"territoriesplanetstab",'name': 'Territories', 'url':'/planets/list/territories/1/'},      
          {'id':"provincesplanetstab",  'name': 'Provinces',   'url':'/planets/list/provinces/1/'},     
          {'id':"statesplanetstab",     'name': 'States',      'url':'/planets/list/states/1/'}]
  
  slider = render_to_string('tablist.xhtml',{'tabs':tabs, 'slider': 'planetview'})
  jsonresponse = {'slider':slider, 'killmenu': 1}

  return HttpResponse(simplejson.dumps(jsonresponse))
  
@login_required
def fleets(request):
  tabs = [{'id':"allfleetstab",         'name': 'All',         'url':'/fleets/list/all/1/'},
          {'id':"scoutsfleetstab",      'name': 'Scouts',      'url':'/fleets/list/scouts/1/'},    
          {'id':"merchantmenfleetstab", 'name': 'Merchants',   'url':'/fleets/list/merchantmen/1/'},      
          {'id':"arcsfleetstab",        'name': 'Arcs',        'url':'/fleets/list/arcs/1/'},     
          {'id':"militaryfleetstab",    'name': 'Military',    'url':'/fleets/list/military/1/'}]
  
  slider =  render_to_string('tablist.xhtml',{'tabs':tabs, 'slider': 'fleetview'})
  jsonresponse = {'slider':slider, 'killmenu': 1}

  return HttpResponse(simplejson.dumps(jsonresponse))


@login_required
def planetlist(request,type,page=1):
  user = request.user
  page = int(page)
  planets = []

  if type == 'all':
    planets = user.planet_set.all()
  elif type == 'colonies':
    planets = user.planet_set.filter(society__lte=25)
  elif type == 'territories':
    planets = user.planet_set.filter(society__lte=50,society__gt=25)
  elif type == 'provinces':
    planets = user.planet_set.filter(society__lte=75,society__gt=50)
  elif type == 'states':
    planets = user.planet_set.filter(society__gt=75)



  paginator = Paginator(planets, 10)
  curpage = paginator.page(page)
  context = {'page': page,
             'planets': curpage,
             'listtype': type,
             'paginator': paginator}

  return render_to_response('planetlist.xhtml', context)
  #, mimetype='application/xhtml+xml')


@login_required
def fleetlist(request,type,page=1):
  user = request.user
  page = int(page)
  fleets = []
  if type == 'all':
    fleets = user.fleet_set.all()
  elif type == 'scouts':
    fleets = user.fleet_set.filter(scouts__gt=0)
  elif type == 'merchantmen':
    fleets = user.fleet_set.filter(Q(merchantmen__gt=0)|Q(bulkfreighters__gt=0))
  elif type == 'arcs':
    fleets = user.fleet_set.filter(arcs__gt=0)
  elif type == 'military':
    fleets = user.fleet_set.all()
    milfleets = []
    for fleet in fleets:
      if fleet.numcombatants() > 0:
        milfleets.append(fleet)
    fleets = milfleets

  paginator = Paginator(fleets, 10)
  curpage = paginator.page(page)
  context = {'page': page,
             'fleets': curpage,
             'listtype': type,
             'paginator': paginator}

  return render_to_response('fleetlist.xhtml', context)




@login_required
def sectors(request):
  if request.POST:
    jsonsectors = {}
    sectors = []
    keys = []
    for key in request.POST:
      if key.isdigit():
        keys.append(key)
    sectors = Sector.objects.filter(key__in=keys)
    for sector in sectors:
      jsonsectors[sector.key] = buildjsonsector(sector, request.user)
    output = simplejson.dumps( jsonsectors )
    return HttpResponse(output)
  return HttpResponse("Nope")

def testforms(request):
  fleet = Fleet.objects.get(pk=1)
  form = AddFleetForm(instance=fleet)
  return render_to_response('form.xhtml',{'form':form})


@login_required
def fleetscrap(request, fleet_id):
  fleet = get_object_or_404(Fleet, id=int(fleet_id))
  fleet.scrap() 
  jsonresponse = {'killmenu': 1, 'status': 'Fleet Scrapped'}
  return HttpResponse(simplejson.dumps(jsonresponse))

@login_required
def fleetinfo(request, fleet_id):
  fleet = get_object_or_404(Fleet, id=int(fleet_id))
  fleet.disp_str = DISPOSITIONS[fleet.disposition][1] 
  menu = render_to_string('fleetinfo.xhtml',{'fleet':fleet})
  jsonresponse = {'menu':menu}
  return HttpResponse(simplejson.dumps(jsonresponse))

@login_required
def planetinfo(request, planet_id):
  planet = get_object_or_404(Planet, id=int(planet_id))
  if planet.owner and planet.owner.get_profile().capital and planet.owner.get_profile().capital == planet:
    planet.capital = 1
  else:
    planet.capital = 0
  planet.resourcelist = planet.resourcereport()
  menu = render_to_string('planetinfo.xhtml',{'planet':planet})
  jsonresponse = {'menu':menu}
  return HttpResponse(simplejson.dumps(jsonresponse))

@login_required
def upgradelist(request, planet_id):
  curplanet = get_object_or_404(Planet, id=int(planet_id))
  upgrades = curplanet.upgradeslist()
  potentialupgrades = curplanet.buildableupgrades() 
  menu = render_to_string('upgradelist.xhtml',{'planet':curplanet,
                                                 'potentialupgrades':potentialupgrades,
                                                 'upgrades':upgrades})
  jsonresponse = {'menu':menu}
  return HttpResponse(simplejson.dumps(jsonresponse))

@login_required
def buildfleet(request, planet_id):
  statusmsg = ""
  user = request.user
  player = user.get_profile()
  planet = get_object_or_404(Planet, id=int(planet_id))
  
  if planet.owner != request.user:
    return HttpResponse("Not on my Watch.")

  buildableships = planet.buildableships()
  if request.POST:
    newships = {}
    for index,key in enumerate(request.POST):
      key=str(key)
      if 'num-' in key:
        shiptype = key.split('-')[1]
        numships = int(request.POST[key])
        if numships > 0:
          newships[shiptype]=numships

        if shiptype not in buildableships['types']:
          statusmsg = "Ship Type '"+shiptype+"' not valid for this planet."
          break
    if statusmsg == "":
      fleet = Fleet()
      statusmsg = fleet.newfleetsetup(planet,newships)  
      jsonresponse = {'killmenu':1, 'status': 'Fleet Built, Send To?', 
                      'rubberband': [fleet.id,fleet.x,fleet.y]}
      return HttpResponse(simplejson.dumps(jsonresponse))
  else:
    buildableships = planet.buildableships()
    context = {'shiptypes': buildableships, 
               'planet': planet,
               'tooltips': buildfleettooltips}
    menu = render_to_string('buildfleet.xhtml', context)
    jsonresponse = {'menu': menu}
    return HttpResponse(simplejson.dumps(jsonresponse))

@login_required
def playerinfo(request, user_id):
  user = get_object_or_404(User, id=int(user_id))
  
  user.totalsociety = Planet.objects.filter(owner = user).aggregate(t=Sum('society'))['t']
  user.totalfleets =  Fleet.objects.filter(owner = user).count()
  user.totalplanets =  Planet.objects.filter(owner = user).count()

  user.totalresources=Manifest.objects.filter(Q(planet__owner = user)|
                                              Q(fleet__owner = user)).aggregate(people=Sum('people'),
                                                                                quatloos=Sum('quatloos'),
                                                                                )
  context = {'player': user}
  menu = render_to_string('playerinfo.xhtml', context)
  jsonresponse = {'menu': menu}
  return HttpResponse(simplejson.dumps(jsonresponse))

@login_required
def politics(request, action):
  user = request.user
  player = user.get_profile()
  statusmsg = ""
  
  request.user.get_profile().lastactivity = datetime.datetime.utcnow()
  request.user.get_profile().save()
 
  try:
    for postitem in request.POST:
      if '-' not in postitem:
        continue
      action, key = postitem.split('-')
      
      otheruser = get_object_or_404(User, id=int(key))
      otherplayer = otheruser.get_profile() 
      
      if action == 'begforpeace' and len(request.POST[postitem]):
        msg = Message()
        msg.subject="offer of peace" 
        msg.fromplayer=user
        msg.toplayer=otheruser
        msgtext = []
        msgtext.append("<h1>"+user.username+" is offering the hand of peace</h1>")
        msgtext.append("")
        msgtext.append(request.POST[postitem])
        msgtext.append("")
        msgtext.append("<h1>Declare Peace?</h1> ")
        msg.message = "\n".join(msgtext)
        msg.save()
        statusmsg = "message sent"
      if action == 'changestatus':
        currelation = player.getpoliticalrelation(otherplayer)
        if currelation != "enemy" and currelation != request.POST[postitem]:
          player.setpoliticalrelation(otherplayer,request.POST[postitem])
          player.save()
          otherplayer.save()
          user.save()
          otheruser.save()
          statusmsg = "status changed"
  except:
    raise
  neighborhood = buildneighborhood(user)
  neighbors = {}
  neighbors['normal'] = []
  neighbors['enemies'] = []
  for neighbor in neighborhood['neighbors']:
    neighbor.relation = player.getpoliticalrelation(neighbor.get_profile())
    if neighbor == user:
      continue
    if user.get_profile().getpoliticalrelation(neighbor.get_profile()) == "enemy":
      neighbors['enemies'].append(neighbor)
    else:
      neighbors['normal'].append(neighbor)
  context = {'neighbors': neighbors,
             'player':player}
  if statusmsg:
    context['statusmsg'] = statusmsg

  slider = render_to_string('neighbors.xhtml', context)
  jsonresponse = {'slider': slider}

  if statusmsg:
    jsonresponse['status'] = statusmsg

  return HttpResponse(simplejson.dumps(jsonresponse))

@login_required
def messages(request):
  user = request.user
  player = user.get_profile()

  request.user.get_profile().lastactivity = datetime.datetime.utcnow()
  request.user.get_profile().save()

  if request.POST:
    for postitem in request.POST:
      if postitem == 'newmsgsubmit':
        if not request.POST.has_key('newmsgto'):
          continue
        elif not request.POST.has_key('newmsgsubject'):
          continue
        elif not request.POST.has_key('newmsgtext'):
          continue
        else:
          otheruser = get_object_or_404(User, id=int(request.POST['newmsgto']))
          body = request.POST['newmsgtext']  
          subject = request.POST['newmsgsubject']
          msg = Message()
          msg.subject = subject
          msg.message = body
          msg.fromplayer = user
          msg.toplayer = otheruser
          msg.save()
      if '-' in postitem:
        action, key = postitem.split('-')
        if action == 'msgdelete':
          msg = get_object_or_404(Message, id=int(key))
          if msg.toplayer==user:
            msg.delete()
        if action == 'replymsgtext' and len(request.POST[postitem]) > 0:
          othermsg = get_object_or_404(Message, id=int(key))
          otheruser = othermsg.fromplayer
          otherplayer = otheruser.get_profile() 
          msg = Message()
          msg.subject = "Re: " + othermsg.subject
          msg.message = request.POST[postitem]
          msg.fromplayer = user
          msg.toplayer = otheruser
          msg.save()

  messages = user.to_player.all()
  neighborhood = buildneighborhood(user)
  context = {'messages': messages,
             'neighbors': neighborhood['neighbors'] }
  slider = render_to_string('messages.xhtml', context)
  jsonresponse = {'slider': slider}
  return HttpResponse(simplejson.dumps(jsonresponse))

def printflist(fleets):
  for f in fleets:
    print "u=" + str(f.owner) + " id=" + str(f.id)

@login_required
def playermap(request):
  player = request.user
  afform = AddFleetForm(auto_id=False);
  

  # turn happens at 10am utc, 2am pacific time 
  curtime = datetime.datetime.utcnow()
  endofturn = datetime.datetime(curtime.year, curtime.month, curtime.day, 10, 0, 0)
  timeleft = 0
  if curtime.hour > 10:
    # it's after 2am, and the turn will happen tommorrow at 2am... 
    endofturn = endofturn + datetime.timedelta(days=1)
  timeleft = "+" + str((endofturn-curtime).seconds) + "s"
  
    

  nummessages = len(player.to_player.all())
  context = {
             'cx':    player.get_profile().capital.x,
             'cy':    player.get_profile().capital.y,
             'afform':      afform, 
             'player':      player,
             'nummessages': nummessages,
             'timeleft':    timeleft}
  
  if Planet.objects.filter(owner=request.user).count() == 1:
    context['newplayer'] = 1
  
  return render_to_response('show.xhtml', context,
                             mimetype='application/xhtml+xml')

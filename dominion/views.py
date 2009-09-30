# Create your views here.
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from newdominion.dominion.models import *
from newdominion.dominion.forms import *
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from newdominion.dominion.menus import *

from registration.forms import RegistrationForm
from registration.models import RegistrationProfile
from registration.views import register
from django.contrib.auth import authenticate, login

import simplejson
import sys
import datetime

@login_required
def fleetmenu(request,fleet_id,action):
  fleet = get_object_or_404(Fleet, id=int(fleet_id))
  clientcommand = ""
  
  request.user.get_profile().lastactivity = datetime.datetime.utcnow()
  request.user.get_profile().save()

  if fleet.owner != request.user and action != 'info':
    print("cheeky devil.")
    return HttpResponse("Nice Try.")
  menuglobals['fleet'] = fleet
  if request.POST:
    if action == 'movetoloc':
      fleet.gotoloc(request.POST['x'],request.POST['y']);
      clientcommand = {}
      neighborhood = buildneighborhood(request.user)
      cullneighborhood(neighborhood)
      clientcommand[str(fleet.sector.key)] = buildjsonsector(fleet.sector.key,request.user,neighborhood)
      return HttpResponse(simplejson.dumps(clientcommand))
    elif action == 'movetoplanet': 
      planet = get_object_or_404(Planet, id=int(request.POST['planet']))
      fleet.gotoplanet(planet)
      clientcommand = {}
      neighborhood = buildneighborhood(request.user)
      cullneighborhood(neighborhood)
      clientcommand[str(fleet.sector.key)] = buildjsonsector(fleet.sector.key,request.user,neighborhood)
      return HttpResponse(simplejson.dumps(clientcommand))
    else:
      form = fleetmenus[action]['form'](request.POST, instance=fleet)
      form.save()
      return render_to_response('nomenu.xhtml', {'statusmsg':'Disposition Changed'},
                                mimetype='application/xhtml+xml')


  else:
    menu = eval(fleetmenus[action]['eval'],menuglobals)
    return render_to_response('planetmenu.xhtml', {'menu': menu}, mimetype='application/xhtml+xml')


      
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
    print action
    return HttpResponse("Cheeky Devil")

  request.user.get_profile().lastactivity = datetime.datetime.utcnow()
  request.user.get_profile().save()

  if request.POST:
    form = planetmenus[action]['form'](request.POST, instance=planet)
    form.save()
    menu = eval(planetmenus['root']['eval'],menuglobals)
    return render_to_response('planetmenu.xhtml', {'menu': menu}, mimetype='application/xhtml+xml')
  else:
    menu = eval(planetmenus[action]['eval'],menuglobals)
    return render_to_response('planetmenu.xhtml', {'menu': menu}, mimetype='application/xhtml+xml')

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
        player.save()
      except ValueError:
        print "bad preferences color"
        # do nothing
      return render_to_response('nomenu.xhtml', {'statusmsg':'Preferences Saved'},
                                mimetype='application/xhtml+xml')
  context = {'user': user, 'player':player}  
  return render_to_response('preferences.xhtml', context,
                             mimetype='application/xhtml+xml')

def buildjsonsector(key,curuser,neighborhood):
  sector = get_object_or_404(Sector, key = int(key))
  planets = sector.planet_set.all()
  fleets = sector.fleet_set.all()
  jsonsector = {}
  jsonsector['planets'] = {}
  jsonsector['fleets'] = {}
  
  for planet in planets:
    if planet.owner == curuser:
      jsonsector['planets'][planet.id] = planet.json(1)
    else:
      jsonsector['planets'][planet.id] = planet.json()
  if neighborhood['fbys'].has_key(int(key)):
    for fleet in neighborhood['fbys'][int(key)]:
      if fleet.owner == curuser:
        jsonsector['fleets'][fleet.id] = fleet.json(1)
      else:
        jsonsector['fleets'][fleet.id] = fleet.json()
  return jsonsector 

@login_required
def sectors(request):
  if request.POST:
    neighborhood = buildneighborhood(request.user)
    cullneighborhood(neighborhood)
    sectors = {}
    for key in request.POST:
      if key.isdigit():
        sectors[key] = buildjsonsector(key, request.user,neighborhood)
            
    output = simplejson.dumps( sectors )
    return HttpResponse(output)
  return HttpResponse("Nope")

def testforms(request):
  fleet = Fleet.objects.get(pk=1)
  form = AddFleetForm(instance=fleet)
  return render_to_response('form.xhtml',{'form':form})

@login_required
def fleetinfo(request, fleet_id):
  fleet = get_object_or_404(Fleet, id=int(fleet_id))
  fleet.disp_str = DISPOSITIONS[fleet.disposition][1] 
  return render_to_response('fleetinfo.xhtml',{'fleet':fleet})

@login_required
def planetinfo(request, planet_id):
  planet = get_object_or_404(Planet, id=int(planet_id))
  if planet.owner and planet.owner.get_profile().capital and planet.owner.get_profile().capital == planet:
    planet.capital = 1
  else:
    planet.capital = 0
  planet.resourcelist = planet.resourcereport()
  return render_to_response('planetinfo.xhtml',{'planet':planet})

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
  buildableships = planet.buildableships()
  context = {'shiptypes': buildableships, 
             'planet': planet,
             'tooltips': buildfleettooltips}
  print str(buildfleettooltips)
  return render_to_response('buildfleet.xhtml', context,
                             mimetype='application/xhtml+xml')

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
    if neighbor.relation == "enemy":
      neighbors['enemies'].append(neighbor)
    else:
      neighbors['normal'].append(neighbor)
  context = {'neighbors': neighbors,
             'player':player}
  if statusmsg:
    context['statusmsg'] = statusmsg
  return render_to_response('neighbors.xhtml', context,
                             mimetype='application/xhtml+xml')

@login_required
def messages(request,action):
  user = request.user
  player = user.get_profile()
  messages = user.to_player.all()
  neighborhood = buildneighborhood(user)

  request.user.get_profile().lastactivity = datetime.datetime.utcnow()
  request.user.get_profile().save()

  context = {'messages': messages,
             'neighbors': neighborhood['neighbors'] }
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
  return render_to_response('messages.xhtml', context,
                            mimetype='application/xhtml+xml')
def printflist(fleets):
  for f in fleets:
    print "u=" + str(f.owner) + " id=" + str(f.id)

@login_required
def playermap(request):
  player = request.user
  afform = AddFleetForm(auto_id=False);
  

  neighborhood = buildneighborhood(player)
  printflist(neighborhood['fleets'])
  #neighborhood = cullneighborhood(neighborhood)
  
  curtime = datetime.datetime.utcnow()
  endofturn = datetime.datetime(curtime.year, curtime.month, curtime.day, 10, 0, 0)
  timeleft = 0
  if curtime.hour > 10:
    # it's after 2am, and the turn will happen tommorrow at 2am... 
    endofturn = endofturn + datetime.timedelta(days=1)
  timeleft = "+" + str((endofturn-curtime).seconds) + "s"
  
    

  nummessages = len(player.to_player.all())
  context = {
             'viewable':    neighborhood['viewable'],
             'afform':      afform, 
             'neighbors':   neighborhood['neighbors'], 
             'player':      player,
             'nummessages': nummessages,
             'timeleft':    timeleft}
  
  if Planet.objects.filter(owner=request.user).count() == 1:
    context['newplayer'] = 1
  
  return render_to_response('show.xhtml', context,
                             mimetype='application/xhtml+xml')

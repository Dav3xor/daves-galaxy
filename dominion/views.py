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

import simplejson
import sys

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

def index(request):
  return register(request, template_name='index.xhtml')

def planetmenu(request,planet_id,action):
  planet = get_object_or_404(Planet, id=int(planet_id))
  menuglobals['planet'] = planet
  #print "--> " + str(request.POST)
  if request.POST:
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
@login_required
def preferences(request):
  user = request.user
  player = user.get_profile()
  player.color = "FF0000"
  if request.POST:
    print str(request.POST)
    if request.POST.has_key('color'):
      player.color = request.POST['color']
      player.save()
  context = {'user': user, 'player':player}  
  return render_to_response('preferences.xhtml', context,
                             mimetype='application/xhtml+xml')


@login_required
def sectors(request):
  print "x"
  if request.POST:
    sectors = {}
    #for index in request.POST:
    #  print request.POST[sector]
    print request.POST
    for key in request.POST:
      if key.isdigit():
        sector = get_object_or_404(Sector, key = int(key))
        planets = sector.planet_set.all()
        fleets = sector.fleet_set.all()
        sectors[key] = {}
        sectors[key]['planets'] = {}
        sectors[key]['fleets'] = {}
        for planet in planets:
          sectors[key]['planets'][planet.id] = planet.json()
        for fleet in fleets:
          sectors[key]['fleets'][fleet.id] = fleet.json()
    output = simplejson.dumps( sectors )
    print "y"
    return HttpResponse(output)
  return HttpResponse("Nope")

def testforms(request):
  fleet = Fleet.objects.get(pk=1)
  form = AddFleetForm(instance=fleet)
  return render_to_response('form.xhtml',{'form':form})

@login_required
def buildfleet(request, planet_id):
  statusmsg = ""
  user = request.user
  player = user.get_profile()
  planet = get_object_or_404(Planet, id=int(planet_id))
  buildableships = planet.buildableships()
  #print str(buildableships)
  if request.POST:
    newships = {}
    for index,key in enumerate(request.POST):
      key=str(key)
      #print str(key) + " - " + str(index)
      if 'num-' in key:
        shiptype = key.split('-')[1]
        numships = int(request.POST[key])
        if numships > 0:
          newships[shiptype]=numships

        if shiptype not in buildableships['types']:
          statusmsg = "Ship Type '"+shiptype+"' not valid for this planet."
          print "invalid ship type"
          break
    if statusmsg == "":
      fleet = Fleet()
      statusmsg = fleet.newfleetsetup(planet,newships)  
  context = {'shiptypes': buildableships, 'planet': planet}
  return render_to_response('buildfleet.xhtml', context,
                             mimetype='application/xhtml+xml')

@login_required
def politics(request, action):
  user = request.user
  player = user.get_profile()
  statusmsg = ""
  #print str(request.POST)
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
    print"---------------------------"
    print "Unexpected error:", sys.exc_info()[0]
    print"---------------------------"
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
  context = {'messages': messages,
             'neighbors': neighborhood['neighbors'] }
  if request.POST:
    #for key,value in enumerate(request.POST):
    #  print str(key) + " - " + str(value)
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

@login_required
def playermap(request):
  player = request.user
  afform = AddFleetForm(auto_id=False);
  neighborhood = buildneighborhood(player)

  nummessages = len(player.to_player.all())
  context = {'fleets':      neighborhood['fleets'], 
             'planets':     neighborhood['planets'], 
             'viewable':    neighborhood['viewable'],
             'afform':      afform, 
             'neighbors':   neighborhood['neighbors'], 
             'player':      player,
             'nummessages': nummessages}
  return render_to_response('show.xhtml', context,
                             mimetype='application/xhtml+xml')

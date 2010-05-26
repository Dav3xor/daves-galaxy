# Create your views here.
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from newdominion.dominion.models import *
from newdominion.dominion.help import *
from newdominion.dominion.forms import *
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render_to_response
from newdominion.dominion.menus import *
from django.core.paginator import Paginator
from django.db.models import Sum, Count

from registration.forms import RegistrationForm
from registration.models import RegistrationProfile
from registration.views import register
from django.contrib.auth import authenticate, login

import simplejson
import sys
import datetime
import util
import feedparser
import os

def scoreboard(request, detail=None):
  scores = []
  base = User.objects.values('username')
  scores.append({'name':'Highest Society Level',    'q':base.annotate(value=Sum('planet__society')).order_by('-value')})
  scores.append({'name':'Most Population', 'q':base.annotate(value=Sum('planet__resources__people')).order_by('-value')})
  scores.append({'name':'Most Planets',    'q':base.annotate(value=Count('planet')).order_by('-value')})
  scores.append({'name':'Most Fleets',     'q':base.annotate(value=Count('fleet')).order_by('-value')})
  scores.append({'name':'Most Money',      'q':base.annotate(value=Sum('planet__resources__quatloos')).order_by('-value')})

  if detail==None:
    return render_to_response('scoreboard.xhtml', 
                              {'scores':scores})
  else:
    type = int(detail)-1
    return render_to_response('scoreboarddetail.xhtml',{'board':scores[type]})
  

@login_required
def instrumentality(request,instrumentality_id):
  instrumentality = get_object_or_404(Instrumentality, id=int(instrumentality_id))

  menu = render_to_string('instrumentalityinfo.xhtml', 
                          {'instrumentality':instrumentality})
  jsonresponse = {'menu':menu, 'status': 'Loaded Info.'}
  return HttpResponse(simplejson.dumps(jsonresponse))
  
@login_required
def upgrades(request,planet_id,action='none',upgrade='-1'):
  user = getuser(request)
  curplanet = get_object_or_404(Planet,id=int(planet_id))
  if user.dgingame and curplanet.owner == user:
    if action=="start":
      newupgrade = PlanetUpgrade()
      newupgrade.start(curplanet,int(upgrade))
    if action=="scrap":
      scrapupgrade = PlanetUpgrade.objects.get(planet=curplanet, 
                                               instrumentality__type=int(upgrade))
      if scrapupgrade:
        scrapupgrade.scrap()
  return HttpResponseRedirect('/planets/'+planet_id+'/upgradelist/')

def sorrydemomode():
      jsonresponse = {'killmenu':1, 'status': 'Sorry, Demo Mode...'}
      return HttpResponse(simplejson.dumps(jsonresponse))
  

def fleetmenu(request,fleet_id,action):
  user = getuser(request)
  fleet = get_object_or_404(Fleet, id=int(fleet_id))
  clientcommand = ""

  menuglobals['fleet'] = fleet
  if request.POST:
    if user.dgingame and fleet.owner == user:
      if action == 'movetoloc':
        fleet.gotoloc(request.POST['x'],request.POST['y']);
        clientcommand = {}
        clientcommand[str(fleet.sector.key)] = buildjsonsector(fleet.sector,user)
        return HttpResponse(simplejson.dumps(clientcommand))
      elif action == 'movetoplanet': 
        planet = get_object_or_404(Planet, id=int(request.POST['planet']))
        fleet.gotoplanet(planet)
        clientcommand = {}
        clientcommand[str(fleet.sector.key)] = buildjsonsector(fleet.sector,user)
        return HttpResponse(simplejson.dumps(clientcommand))
      else:
        form = fleetmenus[action]['form'](request.POST, instance=fleet)
        form.save()

        jsonresponse = {'killmenu':1, 'status': 'Disposition Changed'}
        return HttpResponse(simplejson.dumps(jsonresponse))
    else:
      return sorrydemomode()

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

def planetmenu(request,planet_id,action):
  user = getuser(request)
  planet = get_object_or_404(Planet, id=int(planet_id))
  menuglobals['planet'] = planet

  if request.POST:
    if user.dgingame and planet.owner == user:
      form = planetmenus[action]['form'](request.POST, instance=planet)
      form.save()
      menu = eval(planetmenus['root']['eval'],menuglobals)
      jsonresponse = {'killmenu':1}
      return HttpResponse(simplejson.dumps(jsonresponse))
    else:
      return sorrydemomode()
  else:
    menu = eval(planetmenus[action]['eval'],menuglobals)
    if action in ['manage']:
      jsonresponse = {'window':menu}
    else:
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
def dashboard(request):
  logs = os.popen("tail /home/dav3xor/webapps/game/apache2/logs/access_log", "r")
  errors = os.popen("tail -n6 /home/dav3xor/webapps/game/apache2/logs/error_log", "r")

  loglines = logs.read().split('\n')
  logentries = [] 
  for line in loglines:
    if line == "":
      continue
    quotes = line.split('"')
    entry = []
    entry.append(quotes[0].replace('- - ',''))
    entry.append(quotes[1].split()[1])
    entry.append("(%s)" % quotes[2].split()[0])
    if 'Chrome' in quotes[5]:
      entry.append("Chrome")
    elif 'Safari' in quotes[5]:
      entry.append("Safari")
    elif 'Firefox' in quotes[5]:
      entry.append("Firefox")
    else:
      entry.append("Other")
    logentries.append(" ".join(entry))

  errlines = errors.read().split('\n')
  errentries = []
  for line in errlines:
    if line == "":
      continue
    line = line.split(']')[-1]
    entry = []
    eqs = line.split('"')
    print eqs
    if len(eqs) > 1:
      entry.append("..."+eqs[1][-40:])
      entry.append(" -- ")
      entry.append(eqs[2][2:30]+"...")
    else:
      entry.append(eqs[0][:60])
    errentries.append(" ".join(entry))


  bugsurl = "http://www.davesgalaxy.com/trac/report/1?format=rss&sort=ticket&asc=0&USER=Dave"
  user = request.user
  if user.username not in ['Dave','TravelerTC','harj',
                           'ceciliacase','Dan',
                           'Spitnik','JCC_Starguy', 'Wintermute']:
    return HttpResponse("Nice Try.")
  context = {}
  context['lastplayer'] = Player.objects.latest('lastactivity')
  context['totalusers'] = Player.objects.count()
  context['recentusers'] = Player.objects.filter(lastactivity__gt=
                                                 (datetime.datetime.today() -
                                                  datetime.timedelta(hours=24))).count()
  context['logs'] = logentries
  context['errors'] = errentries
  context['bugs'] = feedparser.parse(bugsurl).entries[:5]
  context['totalplanets'] = Planet.objects.count()
  context['ownedplanets'] = Planet.objects.filter(owner__isnull=False).count()
  context['totalfleets'] = Fleet.objects.count()
  context['damagedfleets'] = Fleet.objects.filter(damaged=True).count()
  context['destroyedfleets'] = Fleet.objects.filter(destroyed=True).count()
  return render_to_response('dashboard.xhtml', context, mimetype='application/xhtml+xml')

def preferences(request):
  user = getuser(request)
  player = user.get_profile()
  if request.POST:
    if user.dgingame:
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
    else:
      return sorrydemomode()  
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


def planets(request):
  tabs = [{'id':"allplanetstab",        'name': 'All',         'url':'/planets/list/all/1/'},
          {'id':"coloniesplanetstab",   'name': 'Colonies',    'url':'/planets/list/colonies/1/'},    
          {'id':"territoriesplanetstab",'name': 'Territories', 'url':'/planets/list/territories/1/'},      
          {'id':"provincesplanetstab",  'name': 'Provinces',   'url':'/planets/list/provinces/1/'},     
          {'id':"statesplanetstab",     'name': 'States',      'url':'/planets/list/states/1/'}]
  
  slider = render_to_string('tablist.xhtml',{'tabs':tabs, 'slider': 'planetview'})
  jsonresponse = {'slider':slider, 'killmenu': 1}

  return HttpResponse(simplejson.dumps(jsonresponse))
  
def fleets(request):
  tabs = [{'id':"allfleetstab",         'name': 'All',         'url':'/fleets/list/all/1/'},
          {'id':"scoutsfleetstab",      'name': 'Scouts',      'url':'/fleets/list/scouts/1/'},    
          {'id':"merchantmenfleetstab", 'name': 'Merchants',   'url':'/fleets/list/merchantmen/1/'},      
          {'id':"arcsfleetstab",        'name': 'Arcs',        'url':'/fleets/list/arcs/1/'},     
          {'id':"militaryfleetstab",    'name': 'Military',    'url':'/fleets/list/military/1/'}]
  
  slider =  render_to_string('tablist.xhtml',{'tabs':tabs, 'slider': 'fleetview'})
  jsonresponse = {'slider':slider, 'killmenu': 1}

  return HttpResponse(simplejson.dumps(jsonresponse))


def planetlist(request,type,page=1):
  user = getuser(request)
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


def fleetlist(request,type,page=1):
  user = getuser(request)
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


def sectors(request):
  user = getuser(request)
  if request.POST:
    jsonsectors = {}
    sectors = []
    keys = []
    for key in request.POST:
      if key.isdigit():
        keys.append(key)
    sectors = Sector.objects.filter(key__in=keys)
    for sector in sectors:
      jsonsectors[sector.key] = buildjsonsector(sector, user)
    output = simplejson.dumps( jsonsectors )
    return HttpResponse(output)
  return HttpResponse("Nope")


def testforms(request):
  fleet = Fleet.objects.get(pk=1)
  form = AddFleetForm(instance=fleet)
  return render_to_response('form.xhtml',{'form':form})


def fleetscrap(request, fleet_id):
  user = getuser(request)
  fleet = get_object_or_404(Fleet, id=int(fleet_id))
  if user.dgingame and user == fleet.owner:
    fleet.scrap() 
    jsonresponse = {'killmenu': 1, 'status': 'Fleet Scrapped'}
    return HttpResponse(simplejson.dumps(jsonresponse))
  else:
    return sorrydemomode()
    
def fleetdisposition(request, fleet_id):
  user = getuser(request)
  fleet = get_object_or_404(Fleet, id=int(fleet_id))
  if request.POST:
    print str(request.POST)
  if request.POST and request.POST.has_key('disposition') and user.dgingame and user == fleet.owner:
    disposition = int(request.POST['disposition'])
    fleet.disposition = disposition 
    print "new disposition = " + str(disposition)
    fleet.save()
    jsonresponse = {'status': 'Disposition Changed'}
    return HttpResponse(simplejson.dumps(jsonresponse))
  else:
    return sorrydemomode()

def fleetinfo(request, fleet_id):
  fleet = get_object_or_404(Fleet, id=int(fleet_id))
  fleet.disp_str = DISPOSITIONS[fleet.disposition][1] 
  menu = render_to_string('fleetinfo.xhtml',{'fleet':fleet})
  jsonresponse = {'menu':menu}
  return HttpResponse(simplejson.dumps(jsonresponse))

def planetinfo(request, planet_id):
  planet = get_object_or_404(Planet, id=int(planet_id))
  if planet.owner and planet.owner.get_profile().capital and planet.owner.get_profile().capital == planet:
    planet.capital = 1
  else:
    planet.capital = 0
  foreign = False
  if planet.owner != request.user:
    foreign = True

  upgrades = PlanetUpgrade.objects.filter(planet=planet)

  planet.resourcelist = planet.resourcereport(foreign)
  menu = render_to_string('planetinfo.xhtml',{'planet':planet, 'upgrades':upgrades})
  jsonresponse = {'menu':menu}
  return HttpResponse(simplejson.dumps(jsonresponse))

def upgradelist(request, planet_id):
  curplanet = get_object_or_404(Planet, id=int(planet_id))
  upgrades = curplanet.upgradeslist()
  potentialupgrades = curplanet.buildableupgrades() 
  window = render_to_string('upgradelist.xhtml',{'planet':curplanet,
                                                 'potentialupgrades':potentialupgrades,
                                                 'upgrades':upgrades})
  jsonresponse = {'window': window}
  return HttpResponse(simplejson.dumps(jsonresponse))

def buildfleet(request, planet_id):
  user = getuser(request)
  statusmsg = ""
  player = user.get_profile()
  planet = get_object_or_404(Planet, id=int(planet_id))
  
  if planet.owner != user:
    jsonresponse = {'killmenu':1, 'status': 'Not Your Planet'} 
    return HttpResponse(simplejson.dumps(jsonresponse))

  buildableships = planet.buildableships()
  if request.POST:
    if user.dgingame:
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
        jsonresponse = {'killmenu':1, 'killwindow':1, 'status': 'Fleet Built, Send To?', 
                        'rubberband': [fleet.id,fleet.x,fleet.y]}
        return HttpResponse(simplejson.dumps(jsonresponse))
    else:
      return sorrydemomode()  
  else:
    buildableships = planet.buildableships()
    context = {'shiptypes': buildableships, 
               'planet': planet,
               'tooltips': buildfleettooltips}
    menu = render_to_string('buildfleet.xhtml', context)
    jsonresponse = {'window': menu, 'x':50, 'y':50}
    return HttpResponse(simplejson.dumps(jsonresponse))

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




def getuser(request):
  if request.user.is_authenticated():
    user = request.user
    user.get_profile().lastactivity = datetime.datetime.utcnow()
    user.get_profile().save()
    user.dgingame = True 
  else:
    user = User.objects.get(id=1)
    user.dgingame = False

  return user

def politics(request, action):
  user = getuser(request)
    
  player = user.get_profile()
  statusmsg = ""
  
  if request.POST:
    if user.dgingame:
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
            statusmsg = "Message Sent"
          if action == 'changestatus':
            currelation = player.getpoliticalrelation(otherplayer)
            if currelation != "enemy" and currelation != request.POST[postitem]:
              player.setpoliticalrelation(otherplayer,request.POST[postitem])
              player.save()
              otherplayer.save()
              user.save()
              otheruser.save()
              statusmsg = "Status Changed"
      except:
        raise
    else:
      return sorrydemomode()
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

  slider = render_to_string('neighbors.xhtml', context)
  jsonresponse = {'slider': slider}

  if statusmsg:
    jsonresponse['status'] = statusmsg

  return HttpResponse(simplejson.dumps(jsonresponse))



def messages(request):
  user = getuser(request)
  player = user.get_profile()

  statusmsg = ""
  if request.POST:
    if user.dgingame:
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
            statusmsg = "Message Sent"
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
            statusmsg = "Reply Sent"
    else:
      return sorrydemomode()
  messages = user.to_player.all()
  neighborhood = buildneighborhood(user)
  context = {'messages': messages,
             'neighbors': neighborhood['neighbors'] }
  slider = render_to_string('messages.xhtml', context)
  jsonresponse = {'slider': slider}
  if statusmsg:
    jsonresponse['status'] = statusmsg
  return HttpResponse(simplejson.dumps(jsonresponse))

def printflist(fleets):
  for f in fleets:
    print "u=" + str(f.owner) + " id=" + str(f.id)

def demomap(request):
  if request.user.is_authenticated():
    logout(request)
  return playermap(request, True)

def playermap(request, demo=False):
  user = getuser(request)
  # turn happens at 10am utc, 2am pacific time 
  curtime = datetime.datetime.utcnow()
  endofturn = datetime.datetime(curtime.year, curtime.month, curtime.day, 10, 0, 0)
  timeleft = 0
  if curtime.hour > 10:
    # it's after 2am, and the turn will happen tommorrow at 2am... 
    endofturn = endofturn + datetime.timedelta(days=1)
  timeleft = "+" + str((endofturn-curtime).seconds) + "s"
 
  if not user.dgingame and demo == False:
    return HttpResponseRedirect('/')
 

  nummessages = len(user.to_player.all())
  context = {
             'cx':          user.get_profile().capital.x,
             'cy':          user.get_profile().capital.y,
             'player':      user,
             'demo':        demo,
             'nummessages': nummessages,
             'timeleft':    timeleft}
  
  if Planet.objects.filter(owner=user).count() == 1:
    context['newplayer'] = 1
  
  return render_to_response('show.xhtml', context,
                             mimetype='application/xhtml+xml')

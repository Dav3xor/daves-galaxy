from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from newdominion.dominion.models import *
from newdominion.dominion.constants import *
from newdominion.dominion.util import *
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
from pprint import pprint

import simplejson
import sys
import datetime
import feedparser
import os
def merch(request):
  return render_to_response('merch.xhtml',{})

def scoreboard(request, detail=None):
  scores = []
  base = User.objects.exclude(id=1).values('id','username')
  scores.append({'name':'Highest Society Level',    
                 'q':base.annotate(value=Sum('planet__society')).order_by('-value').filter(value__isnull=False)})
  scores.append({'name':'Most Population', 
                 'q':base.annotate(value=Sum('planet__resources__people')).order_by('-value').filter(value__isnull=False)})
  scores.append({'name':'Most Planets',    
                 'q':base.annotate(value=Count('planet')).order_by('-value').filter(value__isnull=False)})
  scores.append({'name':'Most Fleets',     
                 'q':base.annotate(value=Count('fleet')).order_by('-value').filter(value__isnull=False)})

  scores.append({'name':'Most Money',      
                 'q':base.annotate(value=Sum('planet__resources__quatloos')).order_by('-value').filter(value__isnull=False)})
 
  if detail==None:
    return render_to_response('scoreboard.xhtml', 
                              {'scores':scores})
  else:
    type = int(detail)-1
    return render_to_response('scoreboarddetail.xhtml',{'board':scores[type]})
  

def instrumentality(request,instrumentality_id):
  instrumentality = get_object_or_404(Instrumentality, id=int(instrumentality_id))

  menu = render_to_string('instrumentalityinfo.xhtml', 
                          {'instrumentality':instrumentality})
  jsonresponse = {'pagedata': menu, 
                  'transient': 1,
                  'id': ('instrumentalityinfo'+str(instrumentality_id)), 
                  'title':'Manage Planet'}
  return HttpResponse(simplejson.dumps(jsonresponse))
  
def upgrades(request,planet_id,action='none',upgrade='-1'):
  user = getuser(request)
  curplanet = get_object_or_404(Planet,id=int(planet_id))
  if user.dgingame and curplanet.owner == user:
    if action=="start":
      if not PlanetUpgrade.objects.filter(planet=curplanet,
                                          instrumentality__type=int(upgrade)):
        curplanet.startupgrade(upgrade)
    if action=="scrap":
      scrapupgrade = PlanetUpgrade.objects.filter(planet=curplanet, 
                                               instrumentality__type=int(upgrade))
      if scrapupgrade:
        # in case we have duplicates (mumble mumble)
        for i in scrapupgrade:
          i.scrap()
  return HttpResponseRedirect('/planets/'+planet_id+'/upgradelist/')

def sorrydemomode():
      jsonresponse = {'killmenu':1, 'status': 'Sorry, Demo Mode...'}
      return HttpResponse(simplejson.dumps(jsonresponse))
  
def newroute(request,user):
  circular = False
  if user.dgingame and request.POST:
    if request.POST['circular'] == 'true':
      circular = True

    name = ""
    if request.POST.has_key('name'):
      name = request.POST['name']

    r = Route(owner=user)
    if r.setroute(request.POST['route'],circular,name):
      r.save()
      return r
    else:
      return False
  else:
    return sorrydemomode()

def namedroutes(request,action):
  user = getuser(request)
  buildfleettoggle = False
  clientcommand = ""

  if request.POST and user.dgingame:
    if action == 'add':
      r = newroute(request,user)
      if r:
        clientcommand = {'sectors':{}, 'status': 'Route Built'}
        clientcommand['sectors'] = {'routes':{r.id: r.json()}}
      else:
        clientcommand = {'status': 'Route Error?'}
      return HttpResponse(simplejson.dumps(clientcommand))
  else:
    return sorrydemomode()

def mapmenu(request, action):
  if action == 'root': 
    menu = Menu()
    menu.addtitle('Map Menu:')
    menu.addnamedroute(None);
    menu.addhelp();
    jsonresponse = {'pagedata': menu.render(), 
                    'menu': 1}
    return HttpResponse(simplejson.dumps(jsonresponse))

def routemenu(request, route_id, action):      
  user = getuser(request)
  route = Route.objects.get(id=int(route_id))
  name = route.name
  if name == "":
    name = "Unnamed ("+str(route.id)+")"

  buildfleettoggle = False
  clientcommand = ""
  if request.POST and user.dgingame:
    if action == 'delete' and route.owner == user:
      clientcommand = {'sectors':{}, 
                       'deleteroute': route.id,
                       'status': 'Route Deleted'}
      
      route.fleet_set.clear()
      route.delete()
      
      return HttpResponse(simplejson.dumps(clientcommand))
    if action == 'rename' and route.owner == user:
      route.name = request.POST['name']
      route.save()
      clientcommand = {'sectors':{}, 
                       'status': 'Route Renamed'}
      return HttpResponse(simplejson.dumps(clientcommand))
  if action == 'root': 
    menu = Menu()
    menu.addtitle('Route: '+name)
    menu.addpostitem('deleteroute'+str(route.id),
                 'DELETE ROUTE',
                 '/routes/'+str(route.id)+'/delete/')
    menu.addrenameroute(route)
    if route.fleet_set.all().count() > 0:
      menu.addheader('Fleets On Route')
      for fleet in route.fleet_set.all()[:5]:
        menu.additem('fleetadmin'+str(fleet.id),
                     fleet.shortdescription(),
                     '/fleets/'+str(fleet.id)+'/root/')
    jsonresponse = {'pagedata': menu.render(), 
                    'menu': 1}
    return HttpResponse(simplejson.dumps(jsonresponse))

def fleetmenu(request,fleet_id,action):
  user = getuser(request)
  fleet = get_object_or_404(Fleet, id=int(fleet_id))
  buildfleettoggle = False
  clientcommand = ""

  if request.POST:
    if request.POST.has_key('buildanotherfleet'):
      # if the user built a fleet, and sent it somewhere,
      # he may have specified that he wanted to build another.
      buildfleettoggle = True
    
    x=False
    y=False
    if request.POST.has_key('x') and request.POST.has_key('y'):
      x = float(request.POST['x'])
      y = float(request.POST['y'])

    if user.dgingame and fleet.owner == user:
      if action == 'onto' and request.POST.has_key('route'):
        r = Route.objects.get(id = int(request.POST['route']))
        if r:
          fleet.ontoroute(r,x,y,True)
          if not buildfleettoggle:
            clientcommand = {'sectors':{}, 'reloadfleets': 1, 
                             'status': 'Fleet Routed'}
            clientcommand['sectors'] = buildjsonsectors([fleet.sector],user)
            return HttpResponse(simplejson.dumps(clientcommand))
      elif action == 'routeto':
        r = newroute(request, user)
        if r:
          fleet.ontoroute(r,False,False,True) 
          if not buildfleettoggle:
            clientcommand = {'sectors':{}, 'reloadfleets': 1, 
                             'status': 'Fleet Routed'}
            clientcommand['sectors'] = buildjsonsectors([fleet.sector],user)
            return HttpResponse(simplejson.dumps(clientcommand))
      elif action == 'movetoloc':
        fleet.offroute()
        fleet.gotoloc(request.POST['x'],request.POST['y']);
        if not buildfleettoggle:
          clientcommand = {'sectors':{}, 'reloadfleets': 1, 
                           'status': 'Destination Changed'}
          clientcommand['sectors'] = buildjsonsectors([fleet.sector],user)
          return HttpResponse(simplejson.dumps(clientcommand))
      elif action == 'movetoplanet': 
        planet = get_object_or_404(Planet, id=int(request.POST['planet']))
        fleet.offroute()
        fleet.gotoplanet(planet,True)
        if not buildfleettoggle:
          clientcommand = {'sectors':{}, 'reloadfleets': 1, 
                           'status': 'Destination Changed'}
          clientcommand['sectors'] = buildjsonsectors([fleet.sector],user)
          return HttpResponse(simplejson.dumps(clientcommand))
      else:
        form = FleetAdminForm(request.POST, instance=fleet)
        form.save()

        jsonresponse = {'killmenu':1, 'reloadfleets': 1, 
                        'status': 'Disposition Changed'}
        return HttpResponse(simplejson.dumps(jsonresponse))
      
      if buildfleettoggle:
        planet_id = request.POST['buildanotherfleet']
        planet = Planet.objects.get(id=int(planet_id))
        request.POST = False
        return buildfleet(request,planet_id, planet.sector)
    else:
      return sorrydemomode()

  else:
    if action == 'root':
      menu = Menu()
      menu.additem('fleetinfoitem'+str(fleet.id),
                   'INFO',
                   '/fleets/'+str(fleet.id)+'/info/')
      menu.addmove(fleet)
      menu.addscrap(fleet)
      form = buildform(makefleetadminform(fleet), 
                       {'title': '',
                        'action': '/fleets/'+str(fleet.id)+'/admin/',
                        'name': 'adminform',
                        'tabid': ''})
      jsonresponse = {'pagedata': menu.render()+form, 
                      'menu': 1}
      return HttpResponse(simplejson.dumps(jsonresponse))
    
    elif action == 'onto':
      menu = Menu()
      menu.addtitle('Named Routes:')
      for r in Route.objects.filter(owner=user).exclude(name=""):
        menu.addontoroute(fleet,r)
      jsonresponse = {'pagedata': menu.render(), 
                      'menu': 1}
      return HttpResponse(simplejson.dumps(jsonresponse))

    else:
      jsonresponse = {'status': 'Please Stop.'}
      return HttpResponse(simplejson.dumps(jsonresponse))

def lastreport(request):
  user = getuser(request)
  context = {'lastreport': user.get_profile().lastreport}
  menu = render_to_string('lastreport.xhtml', context)
  jsonresponse = {'pagedata': menu, 
                  'transient': 1,
                  'id': ('lastreport'), 
                  'title':'Last Turn Report'}
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


def manageplanet(request,planet_id):
  user = getuser(request)
  planet = get_object_or_404(Planet, id=int(planet_id))

  if request.POST:
    if user.dgingame and planet.owner == user:
      form = PlanetManageForm(request.POST, instance=planet)
      form.save()
      jsonresponse = {'killtab': 'manageplanet'+str(planet.id), 
                      'reloadplanets': 1,
                      'status': 'Planet Managed'}
      return HttpResponse(simplejson.dumps(jsonresponse))
    else:
      return sorrydemomode()
  else:
    form = buildform(PlanetManageForm(instance=planet),
                     {'title': 'Manage Planet',
                      'insubtab': '#planetmanagetab'+str(planet.id),
                      'action': '/planets/'+str(planet.id)+'/manage/',
                      'name': 'manageform',
                      'tabid': 'manageplanet'+str(planet.id)})
    jsonresponse = {'tab': form, 
                    'id': ('manageplanet'+str(planet.id)), 
                    'title':'Manage Planet'}
    return HttpResponse(simplejson.dumps(jsonresponse))

def planetmenu(request,planet_id,action):
  user = getuser(request)
  planet = get_object_or_404(Planet, id=int(planet_id))
  if action == 'root':
    userfleets = Fleet.objects.filter(Q(destination=planet)|
                                      Q(homeport=planet)|
                                      Q(source=planet),
                                      owner=user,
                                      x=planet.x,y=planet.y).distinct()
    otherfleets = Fleet.objects.filter(Q(destination=planet)|
                                       Q(homeport=planet)|
                                       Q(source=planet),
                                       x=planet.x,y=planet.y).distinct().exclude(owner=user)

   
    if userfleets.count() == 0 and planet.owner != user:
      return planetinfosimple(request, planet_id)

    menu = Menu()
    menu.addtitle(planet.name)
    if user==planet.owner:
      menu.additem('infoitem'+str(planet.id),
                   'INFO',
                   '/planets/'+str(planet.id)+'/manager/0/')
      menu.additem('manageitem'+str(planet.id),
                   'MANAGE PLANET',
                   '/planets/'+str(planet.id)+'/manager/1/')
      menu.additem('budgetitem'+str(planet.id),
                   'BUDGET',
                   '/planets/'+str(planet.id)+'/manager/2/')
      menu.additem('upgradesitem'+str(planet.id),
                   'UPGRADES',
                   '/planets/'+str(planet.id)+'/manager/3/')
      menu.addnamedroute(planet)
      if planet.canbuildships():
        menu.additem('buildfleet'+str(planet.id),
                     'BUILD FLEET',
                     '/planets/'+str(planet.id)+'/buildfleet/')
    else:
      menu.additem('infoitem'+str(planet.id),
                   'INFO',
                   '/planets/'+str(planet.id)+'/simpleinfo/')
    if len(userfleets) > 0:
      menu.addheader('Fleets at Planet')
      for fleet in userfleets[:5]:
        menu.additem('fleetadmin'+str(fleet.id),
                     fleet.shortdescription(),
                     '/fleets/'+str(fleet.id)+'/root/')
    
    if len(otherfleets) > 0:
      menu.addheader('Other Fleets')
      for fleet in otherfleets[:5]:
        menu.additem('fleetadmin'+str(fleet.id),
                     fleet.shortdescription(),
                     '/fleets/'+str(fleet.id)+'/info/')
    
    if action in ['manage']:
      jsonresponse = {'tab': menu.render(), 
                      'id': ('manageplanet'+str(planet.id)), 
                      'title':'Manage Planet'}
    else:
      jsonresponse = {'pagedata': menu.render(), 
                      'menu': 1}
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
  logs = os.popen("tail /var/log/nginx/host.access.log", "r")
  errors = os.popen("tail -n6 /var/log/nginx/host.error.log", "r")

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
    if len(eqs) > 1:
      entry.append("..."+eqs[1][-40:])
      entry.append(" -- ")
      entry.append(eqs[2][2:30]+"...")
    else:
      entry.append(eqs[0][:60])
    errentries.append(" ".join(entry))
 
  bugsurl = "http://dg.hollensbe.org/projects/davesgalaxy/issues.atom?set_filter=1&sort=status,id:desc&key=bac80a758e76dcbd210bd60ee6c64618447b11f0"  

  user = request.user
  if user.username not in ['Dave','TravelerTC',
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
      form = PreferencesForm(request.POST, instance=player)
      form.save()
      jsonresponse = {'showcountdown':player.showcountdown,
                      'resetmap':1, 
                      'killmenu':1, 
                      'status': 'Preferences Saved'}
      return HttpResponse(simplejson.dumps(jsonresponse))
    else:
      return sorrydemomode()  
  context = {'user': user, 'player':player}  


  form = buildform(PreferencesForm(instance=player),
                   {'title': 'Preferences',
                    'action': '/preferences/',
                    'name': 'preferencesform'})
  if (datetime.datetime.now() - user.date_joined).days < 5:
    form += "<script>$('#id_emailreports').parent().parent().hide()</script>"
  jsonresponse = {'slider': form}
  return HttpResponse(simplejson.dumps(jsonresponse))


def buildjsonsector(cursector,curuser,jsonsectors,connections, routes):
  planets = cursector.planet_set.all()
  fleets = curuser.inviewof.filter(sector=cursector)
  jsonsector = {}
  jsonsector['planets'] = {}
  jsonsector['fleets'] = {}

  for planet in planets:
    if planet.owner == curuser:
      jsonsector['planets'][planet.id] = planet.json(connections,1)
    else:
      jsonsector['planets'][planet.id] = planet.json(connections)


  for fleet in fleets:
    if fleet.owner == curuser:
      jsonsector['fleets'][fleet.id] = fleet.json(routes,1)
    else:
      jsonsector['fleets'][fleet.id] = fleet.json(routes)
  jsonsectors[str(cursector.key)] = jsonsector

def buildjsonsectors(sectors,curuser):
  connections = {} 
  jsonsectors = {'sectors':{}, 'routes':{}}
  routes = {} 
  for cursector in sectors:
    buildjsonsector(cursector,curuser,jsonsectors['sectors'],connections,routes)
      

  extrasectors = {}
  for connection in connections:
    sector = connections[connection]
    if not jsonsectors['sectors'].has_key(str(sector)) and sector not in extrasectors:
      extrasectors[sector] = 1

  if len(extrasectors):
    moresectors = Sector.objects.filter(key__in=extrasectors.keys())

    for sector in moresectors:
      if not jsonsectors['sectors'].has_key(str(sector.key)):
        buildjsonsector(sector,curuser,jsonsectors['sectors'],connections,routes)
        extrasectors[sector] = 2
    for sector in extrasectors:
      if extrasectors[sector] == 1 and not jsonsectors['sectors'].has_key(str(sector)):
        jsonsectors['sectors'][str(sector)] = {}
  if len(routes):
    jsonsectors['routes'] = routes
  for connection in connections:
    sector = str(connections[connection])
    if not jsonsectors['sectors'].has_key(sector):
      # ok, if we have a situation were a sector
      # has a planet with a connection, that's centered
      # in another sector, that has a planet with a connection...
      # we have to stop somewhere.  that somewhere is here.
      continue
    if not jsonsectors['sectors'][sector].has_key('connections'):
      jsonsectors['sectors'][sector]['connections'] = []
    jsonsectors['sectors'][sector]['connections'].append(connection)
  return jsonsectors


def helpindex(request):
  topics = sorted([helptopics[x] for x in helptopics], key=itemgetter('index'))
  page = render_to_string('helpindex.xhtml',{'topics': topics})
  jsonresponse = {'pagedata':page}
  return HttpResponse(simplejson.dumps(jsonresponse))

def simplehelp(request, topic):
  page = helptopics[topic]['contents']
  jsonresponse = {'pagedata':page} 
  return HttpResponse(simplejson.dumps(jsonresponse))

def help(request, topic):
  width = 400
  topic = helptopics[topic]
  if topic.has_key('width'):
    width = topic['width']
  page = ""
  page = render_to_string('helpdetail.xhtml',{'width': width, 'contents': topic['contents']})
  jsonresponse = {'pagedata':page} 
  return HttpResponse(simplejson.dumps(jsonresponse))

def planets(request):
  tabs = [{'id':"allplanetstab",        'name': 'All',         'url':'/planets/list/all/1/'},
          {'id':"coloniesplanetstab",   'name': 'Colonies',    'url':'/planets/list/colonies/1/'},    
          {'id':"territoriesplanetstab",'name': 'Territories', 'url':'/planets/list/territories/1/'},      
          {'id':"provincesplanetstab",  'name': 'Provinces',   'url':'/planets/list/provinces/1/'},     
          {'id':"statesplanetstab",     'name': 'States',      'url':'/planets/list/states/1/'}]
  
  slider = render_to_string('tablist.xhtml',{'tabs':tabs, 
                                             'selected':0,
                                             'slider': 'planetview'})
  jsonresponse = {'pagedata':slider, 'killmenu': 1}

  return HttpResponse(simplejson.dumps(jsonresponse))
  
def fleets(request):
  tabs = [{'id':"allfleetstab",         'name': 'All',         'url':'/fleets/list/all/1/'},
          {'id':"scoutsfleetstab",      'name': 'Scouts',      'url':'/fleets/list/scouts/1/'},    
          {'id':"merchantmenfleetstab", 'name': 'Merchants',   'url':'/fleets/list/merchantmen/1/'},      
          {'id':"arcsfleetstab",        'name': 'Arcs',        'url':'/fleets/list/arcs/1/'},     
          {'id':"militaryfleetstab",    'name': 'Military',    'url':'/fleets/list/military/1/'}]
  
  slider =  render_to_string('tablist.xhtml',{'tabs':tabs, 
                                              'selected':0,
                                              'slider': 'fleetview'})
  jsonresponse = {'pagedata':slider, 'killmenu': 1}

  return HttpResponse(simplejson.dumps(jsonresponse))

def planetmanager(request,planet_id, tab_id=0):
  tab_id = int(tab_id)
  planet = get_object_or_404(Planet, id=int(planet_id))
  tabs = [{'id':"planetinfotab"+str(planet_id),   'name': 'Info',   'url':'/planets/'+str(planet_id)+'/info/'},
          {'id':"planetmanagetab"+str(planet_id), 'name': 'Manage', 'url':'/planets/'+str(planet_id)+'/manage/'},
          {'id':"planetbudgettab"+str(planet_id), 'name': 'Budget', 'url':'/planets/'+str(planet_id)+'/budget/'},
          {'id':"planetupgradestab"+str(planet_id), 'name': 'Upgrades', 'url':'/planets/'+str(planet_id)+'/upgradelist/'}]
  slider = render_to_string('tablist.xhtml',{'tabs':tabs, 
                                             'selected': tab_id,
                                             'title':planet.name,
                                             'slider': 'planetmanagertab'+str(planet_id)})
  jsonresponse = {'transient': 1,
                  'pagedata': slider, 
                  'id': ('planetmanager'+str(planet_id)), 
                  'title':'Manage Planet'}
  return HttpResponse(simplejson.dumps(jsonresponse))


def planetlist(request,type,page=1):
  user = getuser(request)
  page = int(page)
  planets = []

  if type == 'all':
    planets = user.planet_set.order_by('name')
  elif type == 'colonies':
    planets = user.planet_set.order_by('name').filter(society__lte=25)
  elif type == 'territories':
    planets = user.planet_set.order_by('name').filter(society__lte=50,society__gt=25)
  elif type == 'provinces':
    planets = user.planet_set.order_by('name').filter(society__lte=75,society__gt=50)
  elif type == 'states':
    planets = user.planet_set.order_by('name').filter(society__gt=75)



  paginator = Paginator(planets, 10)
  curpage = paginator.page(page)
  context = {'page': page,
             'planets': curpage,
             'listtype': type,
             'paginator': paginator}
  jsonresponse = {}
  #return render_to_response('planetlist.xhtml', context)
  #, mimetype='application/xhtml+xml')
  jsonresponse['tab'] = render_to_string('planetlist.xhtml', context)
  output = simplejson.dumps( jsonresponse )
  return HttpResponse(output)

def fleetlist(request,type,page=1):
  user = getuser(request)
  page = int(page)
  fleets = []
  jsonresponse = {}

  if request.POST and user.dgingame and request.POST.has_key('scrapfleet'):
    fleet = get_object_or_404(Fleet, id=int(request.POST['scrapfleet']))
    dofleetscrap(fleet, user, jsonresponse)


  if type == 'all':
    fleets = user.fleet_set.order_by('id').all()
  elif type == 'scouts':
    fleets = user.fleet_set.order_by('id').filter(scouts__gt=0)
  elif type == 'merchantmen':
    fleets = user.fleet_set.order_by('id').filter(Q(merchantmen__gt=0)|Q(bulkfreighters__gt=0))
  elif type == 'arcs':
    fleets = user.fleet_set.order_by('id').filter(arcs__gt=0)
  elif type == 'military':
    fleets = user.fleet_set.order_by('id').all()
    milfleets = []
    for fleet in fleets:
      if fleet.numcombatants() > 0:
        milfleets.append(fleet)
    fleets = milfleets

  paginator = Paginator(fleets, 9)
  curpage = paginator.page(page)
  context = {'page': page,
             'fleets': curpage,
             'path': request.path,
             'listtype': type,
             'paginator': paginator}

  jsonresponse['tab'] = render_to_string('fleetlist.xhtml', context)
  output = simplejson.dumps( jsonresponse )
  return HttpResponse(output)

def getnamedroutes(user, jsonsectors):
  routes = Route.objects.filter(owner=user).exclude(name="")
  if len(routes):
    if not jsonsectors.has_key('routes'):
      jsonsectors['routes'] = {}
    for r in routes:
      if not jsonsectors['routes'].has_key(r.id):
        jsonsectors['routes'][r.id] = r.json()

def sectors(request):
  user = getuser(request)
  if request.POST:
    sectors = []
    keys = []
    for key in request.POST:
      if key.isdigit():
        keys.append(key)
    sectors = Sector.objects.filter(key__in=keys)
    response = {}
    response['sectors'] = buildjsonsectors(sectors, user)
    if request.POST.has_key('getnamedroutes'):
      getnamedroutes(user, response['sectors'])      
    output = simplejson.dumps( response )
    return HttpResponse(output)
  return HttpResponse("Nope")


def testforms(request):
  fleet = Fleet.objects.get(pk=1)
  form = AddFleetForm(instance=fleet)
  return render_to_response('form.xhtml',{'form':form})

def dofleetscrap(fleet, user, jsonresponse):
  if fleet.inport() and user == fleet.owner:
    fleet.scrap() 
    jsonresponse['status'] = 'Fleet Scrapped'
    jsonresponse['sectors'] = {}
    jsonresponse['reloadfleets'] = 1,
    jsonresponse['sectors'] = buildjsonsectors([fleet.sector],user)
    return 1
  else:
    jsonresponse = {'killmenu': 1, 
                    'status': 'Naughty Boy'}
    return 0

def fleetscrap(request, fleet_id):
  user = getuser(request)
  fleet = get_object_or_404(Fleet, id=int(fleet_id))
  jsonresponse = {'killmenu': 1}
  if user.dgingame:
    dofleetscrap(fleet,user,jsonresponse)
    return HttpResponse(simplejson.dumps(jsonresponse))
  else:
    return sorrydemomode()
    
def fleetdisposition(request, fleet_id):
  user = getuser(request)
  fleet = get_object_or_404(Fleet, id=int(fleet_id))
  if request.POST and request.POST.has_key('disposition') and user.dgingame and user == fleet.owner:
    disposition = int(request.POST['disposition'])
    fleet.disposition = disposition 
    fleet.save()
    jsonresponse = {'status': 'Disposition Changed',
                    'reloadfleets': 1,
    }
    return HttpResponse(simplejson.dumps(jsonresponse))
  else:
    return sorrydemomode()

def fleetinfo(request, fleet_id):
  fleet = get_object_or_404(Fleet, id=int(fleet_id))
  fleet.disp_str = DISPOSITIONS[fleet.disposition][1] 
  menu = render_to_string('fleetinfo.xhtml',{'fleet':fleet})
  jsonresponse = {'transient': 1, 
                  'pagedata':menu,
                  'id': ('fleetinfo'+str(fleet.id)), 
                  'title':'Fleet Info'}
  return HttpResponse(simplejson.dumps(jsonresponse))


def planetbudget(request, planet_id):
  planet = get_object_or_404(Planet, id=int(planet_id))
  credits = []
  debits = []
  totalcredits = 0
  totaldebits = 0

  # credits first
  credits.append(['Income Tax',int(planet.nexttaxation())])
  if planet.hasupgrade(Instrumentality.RGLGOVT):
    nexttax = planet.nextregionaltaxation(False)
    totalcredits += nexttax
    credits.append(['Regional Taxes(Projected)', nexttax])

  # then debits
  for upgrade in planet.upgradeslist([PlanetUpgrade.ACTIVE]):
    debits.append([upgrade.instrumentality.name, -1 * int(upgrade.currentcost('quatloos'))]) 
  for upgrade in planet.upgradeslist([PlanetUpgrade.BUILDING]):
    debits.append([upgrade.instrumentality.name, -1 * int(upgrade.currentcost('quatloos'))]) 
 
  upkeep = planet.fleetupkeepcosts()
  if upkeep.has_key('quatloos'):
    debits.append(['Fleet Upkeep', -1 * upkeep['quatloos']])


  if len(credits):
    totalcredits = sum([x[1] for x in credits])
  if len(debits):
    totaldebits = sum([x[1] for x in debits])
  total = totaldebits+totalcredits
  menu = render_to_string('planetbudget.xhtml',{'credits': credits, 
                                                'debits': debits,
                                                'totalcredits': totalcredits,
                                                'totaldebits': totaldebits,
                                                'total': total})
  jsonresponse = {'tab': menu}
  return HttpResponse(simplejson.dumps(jsonresponse))
  
def planetinfosimple(request, planet_id):
  return planetinfo(request, planet_id, True)

def planetinfo(request, planet_id,alone=False):
  planet = get_object_or_404(Planet, id=int(planet_id))
  user = getuser(request)
  if planet.owner and planet.owner.get_profile().capital and planet.owner.get_profile().capital == planet:
    planet.capital = 1
  else:
    planet.capital = 0
  owned = False
  foreign = False
  if planet.owner != request.user:
    foreign = True
  if planet.owner != None:
    owned = True

  capdistance = 0
  if user and user.get_profile().capital != planet:
    capdistance = getdistanceobj(planet,user.get_profile().capital) 

  upgrades = PlanetUpgrade.objects.filter(planet=planet)

  planet.resourcelist = planet.resourcereport(foreign)
  menu = render_to_string('planetinfo.xhtml',{'alone':alone,
                                              'user':user,
                                              'planet':planet, 
                                              'foreign':foreign,
                                              'owned':owned,
                                              'capdistance':capdistance,
                                              'upgrades':upgrades})
  jsonresponse = {}
  if alone:
    jsonresponse = {'pagedata': menu, 
                    'transient': 1,
                    'id': ('buildfleet'+str(planet.id)), 
                    'title':'Planet Info'}
  else:
    jsonresponse = {'tab': menu}
  return HttpResponse(simplejson.dumps(jsonresponse))

def upgradelist(request, planet_id):
  curplanet = get_object_or_404(Planet, id=int(planet_id))
  upgrades = curplanet.upgradeslist()
  for p in upgrades:
    p.instrumentality.shortid = instrumentalitytypes[p.instrumentality.type]['shortid']

  potentialupgrades = curplanet.buildableupgrades()
  for p in potentialupgrades:
    p.shortid = instrumentalitytypes[p.type]['shortid']

  window = render_to_string('upgradelist.xhtml',{'planet':curplanet,
                                                 'potentialupgrades':potentialupgrades,
                                                 'upgrades':upgrades})
  jsonresponse = {'tab': window, 
                  'id': ('upgradelist'+str(curplanet.id)), 
                  'title':'Upgrades'}
  return HttpResponse(simplejson.dumps(jsonresponse))

def buildfleet(request, planet_id, sector=None):
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
                        'reloadfleets': 1,
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
    jsonresponse = {'pagedata': menu, 
                    'transient': 1,
                    'id': ('buildfleet'+str(planet.id)), 
                    'title':'Build Fleet', 
                    'sectors': {},
                    'x':50, 'y':50}
    if sector != None:
      jsonresponse['sectors'] = buildjsonsectors([sector],user)
      
    return HttpResponse(simplejson.dumps(jsonresponse))

def playerinfo(request, user_id):
  user = get_object_or_404(User, id=int(user_id))
  
  user.totalsociety = Planet.objects.filter(owner = user).aggregate(t=Sum('society'))['t']
  user.totalfleets =  Fleet.objects.filter(owner = user).count()
  user.totalplanets =  Planet.objects.filter(owner = user).count()

  user.totalresources=Manifest.objects.filter(planet__owner = user).aggregate(people=Sum('people'),
                                                                                quatloos=Sum('quatloos'),
                                                                                )
  context = {'player': user}
  menu = render_to_string('playerinfo.xhtml', context)
  jsonresponse = {'pagedata': menu, 
                  'transient': 1,
                  'id': ('playerinfo'+str(user_id)), 
                  'title':'Manage Planet'}
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
  
def peace(request,action,other_id=None, msg_id=None): 
  user = getuser(request)
  player = user.get_profile()
 
  otheruser = get_object_or_404(User, id=int(other_id))
  otherplayer = otheruser.get_profile() 
  
  if request.POST or action in ['makealliance', 'makepeace']:
    if user.dgingame:
      if action in ['makepeace','makealliance']:
        if msg_id:
          msg = Message.objects.get(id=int(msg_id))
          if msg.toplayer != user:
            statusmsg = "Lovely"
          elif action=='makepeace':
            if msg.fromplayer.get_profile().getpoliticalrelation(msg.toplayer.get_profile()) == 'enemy':
              msg.fromplayer.get_profile().setpoliticalrelation(msg.toplayer.get_profile(),'neutral')
              statusmsg = "Peace Declared"
              
              # remove last 4 lines from message so user can't use link
              # to declare peace a 2nd time.
              msg.message = '\n'.join(msg.message.splitlines()[:-4])
              msg.message += '\n Peace Declared'
              msg.save()
            else:
              statusmsg = "Not at War?"
          elif action=='makealliance':
            if msg.fromplayer.get_profile().getpoliticalrelation(msg.toplayer.get_profile()) == 'neutral':
              msg.fromplayer.get_profile().setpoliticalrelation(msg.toplayer.get_profile(),'friend')
              statusmsg = "Alliance Made"
              
              # remove last 3 lines from message so user can't use link
              # to declare an alliance a 2nd time.
              msg.message = '\n'.join(msg.message.splitlines()[:-4])
              msg.message += '\n Alliance Made.'
              msg.save()
            else:
              statusmsg = "Not at Peace?"
        jsonresponse = {'status': statusmsg, 
                        'reloadmessages': 1,
                        'reloadneighbors': 1}
        return HttpResponse(simplejson.dumps(jsonresponse))

      elif action in ['sendalliancemsg','sendpeacemsg']:
        template = ""
        statusmsg = ""
        tabid = ""
        msg = Message()
        msg.fromplayer=user
        msg.toplayer=otheruser
        if action == 'sendpeacemsg':
          msg.subject='offer of peace'
          template = 'peacemsg.markdown'
          statusmsg = "Peace Message Sent"
          tabid = 'begforpeace'+str(otheruser.id)
          content = 'begforpeacemsg'
        elif action == 'sendalliancemsg':
          msg.subject='offer of alliance'
          template = 'allymsg.markdown'
          statusmsg = "Alliance Request Sent"
          tabid = 'handoffriendship'+str(otheruser.id)
          content = 'buildalliance'
        # the message needs an id for the template, so save it
        # first.  won't work without this...
        msg.message = ""
        msg.save()
        msg.message = render_to_string(template,
                                     {'user':user, 'msg':msg,
                                      'peacemsg': request.POST[content]})
        msg.save()
        jsonresponse = {'status': statusmsg,
                        'killtab':        tabid}
        return HttpResponse(simplejson.dumps(jsonresponse))
      
      #elif action == 'writepeacemsg':
    else:
      return sorrydemomode()
  else:
    currelation = player.getpoliticalrelation(otherplayer)
    tab = ""
    pageid = ""
    
    if currelation == "enemy" and action =='begforpeace':
      tab = render_to_string('begforpeace.xhtml',
                             {'enemy': otheruser})
      pageid = 'begforpeace'+str(otheruser.id)
    
    if currelation == 'neutral' and action == 'handoffriendship':
      tab = render_to_string('handoffriendship.xhtml',
                             {'other': otheruser})
      pageid = 'handoffriendship'+str(otheruser.id)
    
    jsonresponse = {'pagedata':  tab, 
                    'permanent': 1,
                    'id':        'begforpeace'+str(otheruser.id), 
                    'title':     'Neighbors'}
    return HttpResponse(simplejson.dumps(jsonresponse))


def politics(request, action, page=1):
  user = getuser(request)
  page = int(page)  
  player = user.get_profile()
  statusmsg = ""
  
  if request.POST:
    if user.dgingame:
      try:
        for postitem in request.POST:
          if '-' not in postitem:
            continue
          action, nextrelation = postitem.split('-')
          key = request.POST[postitem]
          
          otheruser = get_object_or_404(User, id=int(key))
          otherplayer = otheruser.get_profile() 
            
          if action == 'changestatus':
            currelation = player.getpoliticalrelation(otherplayer)
            # only go to 'friend' if we have a message through 'peace' above
            if currelation != "enemy" and \
               nextrelation != "friend" and \
               currelation != nextrelation:
              player.setpoliticalrelation(otherplayer,nextrelation)
              player.save()
              otherplayer.save()
              user.save()
              otheruser.save()
              statusmsg = "Status Changed"
      except:
        raise
    else:
      return sorrydemomode()

  neighbors = player.neighbors.order_by('id').exclude(id=player.id)
  paginator = Paginator(neighbors, 8)
  curpage = paginator.page(page)
  
  for neighbor in curpage.object_list:
    neighbor.relation = player.getpoliticalrelation(neighbor)
  context = {'page': page,
             'neighbors': curpage,
             'player': player,
             'url': request.path,
             'paginator': paginator}

  slider = render_to_string('neighbors.xhtml', context)
  jsonresponse = {'pagedata':  slider, 
                  'permanent': 1,
                  'id':        'neighborslist', 
                  'title':     'Neighbors'}

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
              msg.reply_to.clear()
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
  neighbors = User.objects.filter(player__neighbors=player)
  #neighborhood = buildneighborhood(user)
  context = {'messages': messages,
             'neighbors': neighbors }
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
  endofturn = datetime.datetime(curtime.year, curtime.month, curtime.day, 13, 0, 0)
  timeleft = 0
  if curtime.hour > 13:
    # it's after 5am PST, and the turn will happen tommorrow at 5am... 
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

def logoutuser(request):
  logout(request)
  return index(request)

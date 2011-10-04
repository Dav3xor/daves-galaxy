from django.conf.urls.defaults import *
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^prank/$', 'newdominion.prank.views.index'),
    (r'^prank/submit/$', 'newdominion.prank.views.submit'),
    (r'^prank/(?P<category_id>[a-zA-Z]+)/(?P<link_id>\d+).html$', 'newdominion.prank.views.prank'),

    (r'^help/simple/(?P<topic>[a-zA-Z0-9]+)/$', 'newdominion.dominion.views.simplehelp'),
    (r'^help/(?P<topic>[a-zA-Z0-9]+)/$', 'newdominion.dominion.views.help'),
    (r'^help/$', 'newdominion.dominion.views.helpindex'),

    (r'^testactivation/$', 'newdominion.dominion.views.testactivation'),
    
    (r'^merch/$', 'newdominion.dominion.views.merch'),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/', include('registration.urls')),
    (r'^dashboard/', 'newdominion.dominion.views.dashboard'),
    (r'^scoreboard/(?P<detail>\d+)/$', 'newdominion.dominion.views.scoreboard'),
    (r'^about/$', 'newdominion.dominion.views.about'),
    (r'^contact/$', 'newdominion.dominion.views.contact'),
    (r'^faq/$', 'newdominion.dominion.views.faq'),
    (r'^galaxy/$', 'newdominion.dominion.views.galaxy'),
    (r'^roadmap/$', 'newdominion.dominion.views.roadmap'),
    (r'^scoreboard/', 'newdominion.dominion.views.scoreboard'),
    (r'^login/$', 'newdominion.dominion.views.index'),
    (r'^logout/$', 'newdominion.dominion.views.logoutuser'),
    
    (r'^$', 'newdominion.dominion.views.index'),
    
    (r'^sectors/(?P<sector>\d+)/$', 'newdominion.dominion.views.sector'),
    (r'^view/$', 'newdominion.dominion.views.playermap'),
    (r'^demo/$', 'newdominion.dominion.views.demomap'),
    (r'^preferences/$', 'newdominion.dominion.views.preferences'),
    (r'^politics/(?P<action>[a-zA-Z]+)/(?P<page>\d+)/', 'newdominion.dominion.views.politics'),
    (r'^politics/(?P<action>[a-zA-Z]+)/$', 'newdominion.dominion.views.politics'),
    (r'^messages/$', 'newdominion.dominion.views.messages'),

    (r'^peace/(?P<action>[a-zA-Z]+)/(?P<other_id>[0-9]+)/(?P<msg_id>[0-9]+)/$', 'newdominion.dominion.views.peace'),
    (r'^peace/(?P<action>[a-zA-Z]+)/(?P<other_id>[0-9]+)/$', 'newdominion.dominion.views.peace'),
   
    (r'^map/(?P<action>[a-zA-Z]+)/$', 'newdominion.dominion.views.mapmenu'),

    (r'^planets/$', 'newdominion.dominion.views.planets'),
    (r'^planets/list/(?P<type>[a-zA-Z]+)/(?P<page>[0-9]+)/$', 'newdominion.dominion.views.planetlist'),
    (r'^planets/list/(?P<type>[a-zA-Z]+)/$', 'newdominion.dominion.views.planetlist'),
    (r'^planets/(?P<planet_id>\d+)/buildfleet/$', 'newdominion.dominion.views.buildfleet'),
    (r'^planets/(?P<planet_id>\d+)/upgradelist/$', 'newdominion.dominion.views.upgradelist'),
    (r'^planets/(?P<planet_id>\d+)/upgrades/(?P<action>[a-zA-Z]+)/(?P<upgrade>[0-9]+)/$', 'newdominion.dominion.views.upgrades'),
    (r'^planets/(?P<planet_id>\d+)/info/$', 'newdominion.dominion.views.planetinfo'),
    (r'^planets/(?P<planet_id>\d+)/simpleinfo/$', 'newdominion.dominion.views.planetinfosimple'),
    (r'^planets/(?P<planet_id>\d+)/budget/$', 'newdominion.dominion.views.planetbudget'),
    (r'^planets/(?P<planet_id>\d+)/manager/(?P<tab_id>\d+)/$', 'newdominion.dominion.views.planetmanager'),
    (r'^planets/(?P<planet_id>\d+)/manager/$', 'newdominion.dominion.views.planetmanager'),
    (r'^planets/(?P<planet_id>\d+)/manage/$', 'newdominion.dominion.views.manageplanet'),
    (r'^planets/(?P<planet_id>\d+)/(?P<action>[a-zA-Z]+)/$', 'newdominion.dominion.views.planetmenu'),
    
    (r'^instrumentality/(?P<instrumentality_id>\d+)/info/$', 'newdominion.dominion.views.instrumentality'),

    (r'^fleets/$', 'newdominion.dominion.views.fleets'),
    (r'^fleets/list/(?P<type>[a-zA-Z]+)/(?P<page>[0-9]+)/$', 'newdominion.dominion.views.fleetlist'),
    (r'^fleets/list/(?P<type>[a-zA-Z]+)/$', 'newdominion.dominion.views.fleetlist'),
    (r'^fleets/(?P<fleet_id>\d+)/info/$', 'newdominion.dominion.views.fleetinfo'),
    (r'^fleets/(?P<fleet_id>\d+)/scrap/$', 'newdominion.dominion.views.fleetscrap'),
    (r'^fleets/(?P<fleet_id>\d+)/disposition/$', 'newdominion.dominion.views.fleetdisposition'),
    (r'^fleets/(?P<fleet_id>\d+)/(?P<action>[a-zA-Z]+)/$', 'newdominion.dominion.views.fleetmenu'),

    (r'^routes/named/(?P<action>[a-zA-Z]+)/$', 'newdominion.dominion.views.namedroutes'),
    (r'^routes/(?P<route_id>\d+)/(?P<action>[a-zA-Z]+)/$', 'newdominion.dominion.views.routemenu'),
   
    (r'^lastreport/$', 'newdominion.dominion.views.lastreport'),

    (r'^players/(?P<user_id>\d+)/info/$', 'newdominion.dominion.views.playerinfo'),
    (r'^(?P<sector_id>\d+)/$', 'newdominion.dominion.views.sector'),
    (r'^sectors/$', 'newdominion.dominion.views.sectors'),
    (r'^testforms/', 'newdominion.dominion.views.testforms'),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
      {'document_root': settings.MEDIA_ROOT}),

    # Example:
    # (r'^newdominion/', include('newdominion.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.urls),
)

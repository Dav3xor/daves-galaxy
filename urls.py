from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/', include('registration.urls')),
    (r'^login/$', 'newdominion.dominion.views.index'),
    (r'^$', 'newdominion.dominion.views.index'),
    (r'^sectors/(?P<sector>\d+)/$', 'newdominion.dominion.views.sector'),
    (r'^view/$', 'newdominion.dominion.views.playermap'),
    (r'^preferences/$', 'newdominion.dominion.views.preferences'),
    (r'^politics/(?P<action>[a-zA-Z]+)/$', 'newdominion.dominion.views.politics'),
    (r'^messages/(?P<action>[a-zA-Z]+)/$', 'newdominion.dominion.views.messages'),
    (r'^planets/(?P<planet_id>\d+)/buildfleet/$', 'newdominion.dominion.views.buildfleet'),
    (r'^planets/(?P<planet_id>\d+)/info/$', 'newdominion.dominion.views.planetinfo'),
    (r'^planets/(?P<planet_id>\d+)/(?P<action>[a-zA-Z]+)/$', 'newdominion.dominion.views.planetmenu'),
    (r'^fleets/(?P<fleet_id>\d+)/info/$', 'newdominion.dominion.views.fleetinfo'),
    (r'^fleets/(?P<fleet_id>\d+)/(?P<action>[a-zA-Z]+)/$', 'newdominion.dominion.views.fleetmenu'),
    (r'^(?P<sector_id>\d+)/$', 'newdominion.dominion.views.sector'),
    (r'^sectors/$', 'newdominion.dominion.views.sectors'),
    (r'^testforms/', 'newdominion.dominion.views.testforms'),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
      {'document_root': '/home/dave/dev/newdominion/static/'}),

    # Example:
    # (r'^newdominion/', include('newdominion.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)

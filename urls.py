from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^sectors/(?P<sector>\d+)/$', 'newdominion.dominion.views.sector'),
    (r'^view/(?P<player_id>[a-z0-9A-Z-]+)/$', 'newdominion.dominion.views.playermap'),
    (r'^planets/(?P<planet_id>\d+)/(?P<action>[a-zA-Z]+)/$', 'newdominion.dominion.views.planetmenu'),
    (r'^fleets/(?P<fleet_id>\d+)/(?P<action>[a-zA-Z]+)/$', 'newdominion.dominion.views.fleetmenu'),
    (r'^(?P<sector_id>\d+)/$', 'newdominion.dominion.views.sector'),
    (r'^testforms/', 'newdominion.dominion.views.testforms'),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
      {'document_root': '/home/dave/dev/static/'}),

    # Example:
    # (r'^newdominion/', include('newdominion.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)

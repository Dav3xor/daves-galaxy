from django import forms
from django.forms import ModelForm
from newdominion.dominion.models import *

# Create the form class.
class AddFleetForm(ModelForm):
  class Meta:
    model = Fleet
    fields = ('scouts','merchantmen','fighters','frigates',
              'destroyers', 'cruisers', 'battleships',
              'superbattleships', 'carriers')
class FleetAdminForm(ModelForm):
  class Meta:
    model = Fleet
    fields = ('disposition')
class PlanetEconomyForm(ModelForm):
  class Meta:
    model = Planet
    fields = ('openshipyard','opencommodities','opentrade','tariffrate')


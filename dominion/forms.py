from django import forms
from django.forms import ModelForm
from newdominion.dominion.models import *

# Create the form class.
class AddFleetForm(ModelForm):
  class Meta:
    model = Fleet
    fields = ('scouts','merchantmen','arcs','fighters','frigates',
              'destroyers', 'cruisers', 'battleships',
              'superbattleships', 'carriers',)

class FleetAdminForm(ModelForm):
  class Meta:
    model = Fleet
    fields = ('disposition',)

class PlanetManageForm(ModelForm):
  name = forms.CharField(widget=forms.TextInput(attrs={'size': 15}))
  tariffrate = forms.CharField(widget=forms.TextInput(attrs={'size': 3}))
  inctaxrate = forms.CharField(widget=forms.TextInput(attrs={'size': 3}))
  class Meta:
    model = Planet
    fields = ('name','openshipyard','opencommodities','opentrade','tariffrate','inctaxrate',)


from django import forms
from django.forms import ModelForm
from newdominion.dominion.models import *
 
from django.forms.widgets import TextInput
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
 
class SliderWidget(TextInput):
 
  max = 100
  min = 0
  step = 10

  def __init__(self, min=None, max=None, step=None, attrs=None):
    super(SliderWidget, self).__init__(attrs)
    if max:
      self.max = max
    if min:
      self.min = min
    if step:
      self.step = step
 
  def render(self, name, value, attrs=None):
    attrs['type'] = 'hidden'
    final_attrs = self.build_attrs(attrs, name=name)
    slider_id, label_id = 'slider-'+name, 'label-'+name

    #label = '<span class="sliderlabel" id="%s">%2.2f%%</span>' % ('label-'+name,value)
    hidden_field = super(SliderWidget, self).render(name, value, attrs)
    slider = """
     <div>
       <div style="color: white; float: right; font-size: 20px; position:relative; top:0px; right:5px;" id="%(label_id)s">%(value)s%%</div>
       <div class="slider" style="top:2px; margin-right:95px;" id="%(slider_id)s"></div>
     </div>
     <script type="text/javascript">
     $(function() {
       $('#%(slider_id)s').slider({
         min : %(min)s,
         max : %(max)s,
         step : %(step)s,
         value : %(value)s,
         slide : function(event, ui) {
           $('#%(label_id)s').html($('#%(slider_id)s').slider('value')+"%%");
         },
         change : function(event, ui) {
           $('#%(field_id)s').val($('#%(slider_id)s').slider('value'));
           $('#%(label_id)s').html($('#%(slider_id)s').slider('value')+"%%");
         }
       });
     });
     </script>
   """ % { 'slider_id' : slider_id, 
           'field_id' : 'id_'+name, 
           'min' : self.min, 
           'max' : self.max, 
           'step' : self.step, 
           'value' : value,
           'label_id' : label_id }
   
    return mark_safe(hidden_field+slider)





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
  #tariffrate = forms.CharField(widget=forms.TextInput(attrs={'class': 'twentypercent'}))
  #tariffrate = forms.CharField(widget=SliderInput(attrs={'class': 'twentypercent'}))
  #inctaxrate = forms.CharField(widget=forms.TextInput(attrs={'class': 'twentypercent'}))
  tariffrate = forms.FloatField(widget=SliderWidget(min=0, max=20, step=.1))
  inctaxrate = forms.FloatField(widget=SliderWidget(min=0, max=20, step=.1))

  class Meta:
    model = Planet
    fields = ('name','openshipyard','opencommodities','opentrade','tariffrate','inctaxrate',)


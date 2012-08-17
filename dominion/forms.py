from django import forms
from django.forms import ModelForm
from newdominion.dominion.models import *
from newdominion.dominion.util import *
 
from django.forms.widgets import TextInput
from django.forms.util import flatatt
from django.utils.safestring import mark_safe



class ColorWidget(TextInput):
  def __init__(self, attrs=None):
    super(ColorWidget, self).__init__(attrs)

  def render(self, name, value, attrs=None):
    attrs['type'] = 'hidden'
    final_attrs = self.build_attrs(attrs, name=name)
    slider_id, label_id = 'slider-'+name, 'label-'+name

    #label = '<span class="sliderlabel" id="%s">%2.2f%%</span>' % ('label-'+name,value)
    hidden_field = super(ColorWidget, self).render(name, value, attrs)
    slider = """
      <input id="color-change" 
             name="color" 
             size="10"
             type="text" 
             value="%(value)s"/>
      <script>
        pumenu.hide();
        function changecolor(color)
        {
          $('#color-change').value = color;
          $('#prefs-changecolor').show('fast');
        }
        $('#colorpicker').farbtastic('#color-change',changecolor); 
      </script>
      <div id="colorpicker"/>
    """ % {'value': value}
    return mark_safe(hidden_field+slider)

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
       <table><tr><td>
       <div class="slider" style="width:300px; top:2px;" id="%(slider_id)s"></div>
       </td>
       <td>
       <div style="width: 50px; color: white; text-align:right; font-size: 20px;" 
            id="%(label_id)s">%(value)s%%</div>
       </td></tr></table>
     </div>
     <script type="text/javascript">
     $(function() {
       $('#%(slider_id)s').slider({
         min : %(min)s,
         max : %(max)s,
         step : %(step)s,
         value : %(value)s,
         slide : function(event, ui) {
           $('#%(label_id)s').html(ui.value.toFixed(1)+"%%");
           $('#%(field_id)s').val(ui.value);
         },
         change : function(event, ui) {
           $('#%(label_id)s').html($('#%(slider_id)s').slider('value').toFixed(1)+"%%");
           $('#%(field_id)s').val($('#%(slider_id)s').slider('value'));
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

class PreferencesForm(ModelForm):
  color = forms.CharField(widget=ColorWidget())

  def clean_color(self):
    newcolor = self.cleaned_data['color']
    try:
      newcolor = normalizecolor(newcolor)
    except ValueError:
      raise forms.ValidationError("Bad Color?!")
      # do nothing
    return newcolor

  class Meta:
    model = Player
    fields = ('color','emailreports','emailmessages','showcountdown',
              'racename', 'rulername', 'rulertitle', 'politicalname')
    
class PlanetManageForm(ModelForm):
  name = forms.CharField(widget=forms.TextInput(attrs={'size': 15}))
  tariffrate = forms.FloatField(widget=SliderWidget(min=0, max=30, step=.2))
  inctaxrate = forms.FloatField(widget=SliderWidget(min=0, max=30, step=.2))
  
  def clean_tariffrate(self):
    tariffrate = self.cleaned_data['tariffrate']
    if tariffrate < 0.0 or tariffrate > 30.0:
      raise forms.ValidationError(u'tariffrate out of range')
    return tariffrate
  
  def clean_inctaxrate(self):
    inctaxrate = self.cleaned_data['inctaxrate']
    if inctaxrate < 0.0 or inctaxrate > 30.0:
      raise forms.ValidationError(u'inctaxrate out of range')
    return inctaxrate


  class Meta:
    model = Planet
    fields = ('name','openshipyard','opencommodities','opentrade','tariffrate','inctaxrate',)


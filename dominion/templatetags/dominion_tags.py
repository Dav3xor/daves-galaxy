from django import template
import hashlib


register = template.Library()
counter = 1 

class TestPoint(object):
  def __init__(self):
    self.x = 1.5
    self.y = 2.1

@register.filter
def get_attr(obj, val):
  return getattr(obj, val)

@register.simple_tag
def playerinfobutton(player):
  """
  >>> hashlib.md5(playerinfobutton(1)).hexdigest()
  '3b457ee6004cb182e5cef4931b4b3d60'
  >>> hashlib.md5(playerinfobutton(1)).hexdigest()
  '4142ccc320f31cfc776707c06100b33e'
  """
  global counter
  output = """
  <img class="noborder" title="player info"
                       id="playerinfo%d"
                       src="/site_media/infobutton.png"/>
  <script>
    loadtooltip('#playerinfo%d',
                '/players/%s/info/',
                580,'click');
  </script>
  """ % (counter,counter,player)
  counter = (counter%10000)+1
  return output



@register.simple_tag
def planetinfobutton(planet):
  """
  >>> hashlib.md5(planetinfobutton(1)).hexdigest()
  '7c2af7a2269a9279bed2afd3db1d4317'
  >>> hashlib.md5(planetinfobutton(1)).hexdigest()
  '9e8da88e996315d973d9aeb06cead8ba'
  """
  global counter
  output = """
  <img class="noborder" title="planet info"
                       id="planetinfo%d"
                       src="/site_media/infobutton.png"/>
  <script>
    $('#planetinfo%d').click(
      function(event){
        handlebutton('planetmanagertab%d',
                     'planetmanager%d',
                     'planetinfotab%d',
                     'ManagePlanet',
                     '/planets/%d/manager/0/',
                     '/planets/%d/info/');
      });
  </script>
  """ % (counter,counter,planet,planet,planet,planet,planet)
  counter = (counter%10000)+1
  return output




@register.simple_tag
def planetmanagebutton(planet):
  """
  >>> hashlib.md5(planetmanagebutton(1)).hexdigest()
  '2d4c0ee7bee16d2ad1e7b7046778dffd'
  >>> hashlib.md5(planetmanagebutton(1)).hexdigest()
  '024cc2910f2100e7da98f9902fe6edc3'
  """
  global counter
  output = """
  <img class="infobutton" title="Manage" 
                 id="planetmanage%d"
                 src="/site_media/manage.png"/>
  <script>
    $('#planetmanage%d').click(
      function(event){
        handlebutton('planetmanagertab%d',
                     'planetmanager%d',
                     'planetmanagetab%d',
                     'ManagePlanet',
                     '/planets/%d/manager/1/',
                     '/planets/%d/manage/');
      });
  </script>
  """ % (counter,counter,planet,planet,planet,planet,planet)
  counter = (counter%10000)+1
  return output



@register.simple_tag
def planetupgradebutton(planet):
  """
  >>> hashlib.md5(planetupgradebutton(1)).hexdigest()
  '20dda3a904bbff80799a82e485d65ffb'
  >>> hashlib.md5(planetupgradebutton(1)).hexdigest()
  '4f0e536be2d9f14d543cf053605407a5'
  """
  global counter
  output = """
  <img class="infobutton" title="Upgrade" 
                 id="planetupgrade%d"
                 src="/site_media/upgradebutton.png"/>
  <script>
    $('#planetupgrade%d').click(
      function(event){
        handlebutton('planetmanagertab%d',
                     'planetmanager%d',
                     'planetupgradestab%d',
                     'ManagePlanet',
                     '/planets/%d/manager/3/',
                     '/planets/%d/upgradelist/');
      });
  </script>
  """ % (counter,counter,planet,planet,planet,planet,planet)
  counter = (counter%10000)+1
  return output



@register.simple_tag
def buildfleetbutton(planet):
  """
  >>> hashlib.md5(buildfleetbutton(1)).hexdigest()
  '324f0b3532f6f851226b11a74876833b'
  >>> hashlib.md5(buildfleetbutton(1)).hexdigest()
  'ac16dd18c3e7f93f814d7e90a11807bb'
  """
  global counter
  if planet.canbuildships():
    output = """
    <img class="infobutton" title="Construct Fleet" 
           id="planetbuildfleet%d"
           src="/site_media/construct.png"/>
    <script>
      $('#planetbuildfleet%d').click(
        function(event){
          if(!transienttabs.alreadyopen('buildfleet%d')){
            transienttabs.pushtab('buildfleet%d','Build Fleet','',false);
            transienttabs.gettaburl('buildfleet%d',
                                    '/planets/%d/buildfleet/');
            transienttabs.displaytab('buildfleet%d');
          } else {
            transienttabs.removetab('buildfleet%d');
          }
        });
    </script>
    """ % (counter,counter,planet.id,planet.id,planet.id,planet.id,planet.id,planet.id)
  else:
    output = ""
  counter = (counter%10000)+1
  return output



@register.simple_tag
def fleetinfobutton(fleet):
  """
  >>> hashlib.md5(fleetinfobutton(1)).hexdigest()
  '7c2af7a2269a9279bed2afd3db1d4317'
  >>> hashlib.md5(fleetinfobutton(1)).hexdigest()
  '9e8da88e996315d973d9aeb06cead8ba'
  """
  global counter
  output = """
  <img class="noborder" title="fleet info"
                 id="fleetinfo%d"
                 src="/site_media/infobutton.png"/>
  <script>
    loadtooltip('#fleetinfo%d',
                '/fleets/%d/info/',
                380,'click');
  </script>
  """ % (counter,counter,fleet)
  counter = (counter%10000)+1
  return output



@register.simple_tag
def fleetdestinationbutton(fleet):
  """
  >>> hashlib.md5(fleetdestinationbutton(1)).hexdigest()
  '7c2af7a2269a9279bed2afd3db1d4317'
  >>> hashlib.md5(fleetdestinationbutton(1)).hexdigest()
  '9e8da88e996315d973d9aeb06cead8ba'
  """
  global counter
  output = """
  <img class="noborder" title="set destination" 
                 src="/site_media/goto.png"
                 onmouseup="rubberbandfromfleet(%d,%f,%f);"/>
  """ % (fleet.id,fleet.x,fleet.y)
  return output



@register.simple_tag
def fleetscrapbutton(fleet, listtype = 'all', page='1'):
  """
  >>> hashlib.md5(fleetdestinationbutton(1)).hexdigest()
  '7c2af7a2269a9279bed2afd3db1d4317'
  >>> hashlib.md5(fleetdestinationbutton(1)).hexdigest()
  '9e8da88e996315d973d9aeb06cead8ba'
  """
  if fleet.inport():
    output = """
    <img title="scrap fleet" 
         onclick="loadtab('#%sfleetstab',
                          '/fleets/list/%s/%d/',
                          '#fleetview',
                          {'scrapfleet':%d});"
         class="noborder" src="/site_media/scrap.png"/>

    """ % (listtype,listtype,page,fleet.id)
  else:
    output = ""
  return output



@register.simple_tag
def ajaxformbutton(url, text, key, value):
  """
  >>> a = TestPoint()
  >>> hashlib.md5(gotobutton(a)).hexdigest()
  '0e7daee6644f42d2d3730daca55acac9'
  """
  output = """

<input 
  onclick="sendrequest(handleserverresponse,
                       '%s',
                       'POST',
                       {'%s':%s});"
  type="button" 
  value="%s"/>
  """ % (url,key,value,text)
  return output



@register.simple_tag
def gotobutton(location):
  """
  >>> a = TestPoint()
  >>> hashlib.md5(gotobutton(a)).hexdigest()
  '0e7daee6644f42d2d3730daca55acac9'
  """
  output = """
  <img src="/site_media/center.png" 
                       class="noborder"
                       onclick="centermap(%f,%f);"
                       title="center on capital"/>
  """ % (location.x, location.y)
  return output

if __name__ == '__main__':
  import doctest
  doctest.testmod()

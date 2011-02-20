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
  return infopopup('playerinfo', 'player info',
                    '/players/%s/info/'%player)

@register.simple_tag
def shipinfobutton(shiptype):
  """
  >>> hashlib.md5(playerinfobutton(1)).hexdigest()
  '3b457ee6004cb182e5cef4931b4b3d60'
  >>> hashlib.md5(playerinfobutton(1)).hexdigest()
  '4142ccc320f31cfc776707c06100b33e'
  """
  return infopopup('shiptypeinfo', 'ship info',
                    '/help/simple/%s/'%shiptype)


@register.simple_tag
def instrumentalityinfobutton(instrumentalitytype):
  """
  >>> hashlib.md5(playerinfobutton(1)).hexdigest()
  '3b457ee6004cb182e5cef4931b4b3d60'
  >>> hashlib.md5(playerinfobutton(1)).hexdigest()
  '4142ccc320f31cfc776707c06100b33e'
  """
  return infopopup('instrumentalityinfo', 'instrumentality info',
                    '/help/simple/%s/'%instrumentalitytype,400)


@register.simple_tag
def infopopup(objid,title,url,width=580):
  """
  >>> hashlib.md5(playerinfobutton(1)).hexdigest()
  '3b457ee6004cb182e5cef4931b4b3d60'
  >>> hashlib.md5(playerinfobutton(1)).hexdigest()
  '4142ccc320f31cfc776707c06100b33e'
  """
  global counter
  output = """
  <img class="noborder" title="%s"
                       id="%s%d"
                       src="/site_media/infobutton.png"/>
  <script>
    loadtooltip('#%s%d',
                '%s',
                %d,'click');
  </script>
  """ % (title,objid,counter,objid,counter,url,width)
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
  return infopopup('fleetinfo', 'fleet info',
                    '/fleets/%d/info/'%fleet)



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
def playerpicture(player, width, height, background="none"):
  backgrounds = {'none': '',
                 'normal': """
      <g
         id="layer1">
        <rect
           width="120"
           height="170"
           x="0"
           y="0"
           id="rect2385"
           style="opacity:1;
                  fill:url(#linearGradient3163);
                  fill-opacity:1;stroke:#000000;
                  stroke-width:3;stroke-linecap:butt;
                  stroke-linejoin:miter;
                  stroke-miterlimit:4;
                  stroke-dasharray:none;
                  stroke-opacity:1" />
        <path
           d="M 5,165 L 20,140 L 100,140 L 115,165 L 5,165 z"
           id="path3165"
           style="fill:url(#radialGradient3181);
                  fill-opacity:1;
                  fill-rule:evenodd;
                  stroke:#000000;
                  stroke-width:1px;
                  stroke-linecap:butt;
                  stroke-linejoin:miter;
                  stroke-opacity:1" />
      </g>
      """}
  output = """
    <svg
       xmlns:svg="http://www.w3.org/2000/svg"
       xmlns="http://www.w3.org/2000/svg"
       xmlns:xlink="http://www.w3.org/1999/xlink"
       version="1.0"
       viewBox="0 0 120 170"
       width="%d"
       height="%d"
       id="svg2">
      <defs
         id="defs4">
        <linearGradient
           id="linearGradient3175">
          <stop
             id="stop3177"
             style="stop-color:#000000;stop-opacity:1"
             offset="0" />
          <stop
             id="stop3179"
             style="stop-color:#323232;stop-opacity:0.98275864"
             offset="1" />
        </linearGradient>
        <linearGradient
           id="linearGradient3157">
          <stop
             id="stop3159"
             style="stop-color:#000000;stop-opacity:1"
             offset="0" />
          <stop
             id="stop3161"
             style="stop-color:#808041;stop-opacity:1"
             offset="1" />
        </linearGradient>
        <linearGradient
           x1="55"
           y1="-20"
           x2="55"
           y2="170"
           id="linearGradient3163"
           xlink:href="#linearGradient3157"
           gradientUnits="userSpaceOnUse" />
        <radialGradient
           cx="34.583031"
           cy="172.07823"
           r="55.5"
           fx="34.583031"
           fy="172.07823"
           id="radialGradient3181"
           xlink:href="#linearGradient3175"
           gradientUnits="userSpaceOnUse"
           gradientTransform="matrix(1.9641997,-1.0614772,0.6414687,1.1870022,-138.20927,-15.073515)" />
      </defs>
      %s
      %s
    </svg>
  """ % (width, height, backgrounds[background],
         player.get_profile().appearance)
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

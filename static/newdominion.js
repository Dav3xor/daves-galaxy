
var originalview = [];
var mousedown = new Boolean(false);
var offset;
var mouseorigin;
var server = new XMLHttpRequest();
var curfleetid = 0;
var curplanetid = 0;
var rubberband;

function rubberbandfromfleet(fleetid,initialx,initialy)
{
  curfleetid = fleetid;
  killmenu();
  
  rubberband.setAttribute('visibility','visible');
  rubberband.setAttribute('x1',initialx);
  rubberband.setAttribute('y1',initialy);
}

function loadnewmenu()
{
  if((server.readyState == 4) && (server.status == 500)){
    var menu = document.getElementById('menu');
    if(menu){
      w = window.open('');
      w.document.write(server.responseText);
    }
  }
  if ((server.readyState == 4)&&(server.status == 200)){
    var response  = server.responseText;
    var menu = document.getElementById('menu');
    if(menu){
      menu.innerHTML = response;
    }
  }
}

 
function handlemenuitemreq(type, requestedmenu, id)
  {
  var myurl = "/"+type+"/"+id+"/" + requestedmenu + "/";
  server.open("GET", myurl, true);
  server.onreadystatechange = loadnewmenu;
  server.send(null);
  setmenuwaiting();
  }

function sendform(subform,request)
{
  var submission = new Array();
  for(i in subform.getElementsByTagName('select')){
    var formfield = subform.getElementsByTagName('select')[i];
    if(formfield.type == 'select-one'){
      submission.push(formfield.name + "=" + formfield.options[formfield.selectedIndex].value);
    }
  }
  for(i in subform.getElementsByTagName('input')){
    var formfield = subform.getElementsByTagName('input')[i];
    if(formfield.name){
      if(formfield.type=="checkbox"){
        if(formfield.checked){
          submission.push(formfield.name + '=' + formfield.value);
        } else {
          submission.push(formfield.name + '=');
        }
      } else {
        submission.push(formfield.name + '=' + formfield.value);
      }
    }
  }
  submission = submission.join('&');
  server.open('POST', request, true);
  server.setRequestHeader('Content-Type',
                           'application/x-www-form-urlencoded');
  server.onreadystatechange = loadnewmenu;
  server.send(submission); 
  setmenuwaiting();
}



function zoomcircle(evt,factor)
{
  var p = evt.target;
  var radius = p.getAttribute("r");
  radius *= factor;
  p.setAttribute("r", radius);
}

function planethoveron(evt,planet)
{
  zoomcircle(evt,2.0);
  curplanetid = planet;
}

function planethoveroff(evt,planet)
{
  zoomcircle(evt,.5);
  curplanetid = 0;
}

function fleethoveron(evt,fleet)
{
  zoomcircle(evt,2.0);
}

function fleethoveroff(evt,fleet)
{
  zoomcircle(evt,.5);
}


function dofleetmousedown(evt,fleet)
{
  if(curfleetid==fleet){
    curfleetid=0;
    alert("aha");
  } else if(!curfleetid){
    var mapdiv = document.getElementById('mapdiv');
    var newmenu = document.createElement('div');
    newmenu.setAttribute('id','menu');
    newmenu.setAttribute('style','position:absolute; top:'+(evt.clientY+10)+
                         'px; left:'+(evt.clientX+10)+ 'px;');
    newmenu.setAttribute('class','menu');
    handlemenuitemreq('fleets', 'root', fleet);
    mapdiv.appendChild(newmenu);
  } else {
    // this should probably be changed to fleets/1/intercept
    // with all the appropriate logic, etc...
    var curloc = getcurxy(evt);
    movefleettoloc(evt,fleet,curloc);
    curfleetid=0;
  }
}

function movefleettoloc(evt,fleet,curloc)
{
  var request = "/fleets/"+fleet+"/movetoloc/";
  var submission = "x=" + curloc.x + "&y=" + curloc.y;
  server.open('POST', request, true);
  server.setRequestHeader('Content-Type',
                           'application/x-www-form-urlencoded');
  server.onreadystatechange = loadnewmenu;
  server.send(submission); 
  setmenuwaiting();
}

function doplanetmousedown(evt,planet)
{
  if(curfleetid){
    var request = "/fleets/"+curfleetid+"/movetoplanet/";
    var submission = "planet=" + planet;
    server.open('POST', request, true);
    server.setRequestHeader('Content-Type',
                             'application/x-www-form-urlencoded');
    server.onreadystatechange = loadnewmenu;
    server.send(submission); 
    setmenuwaiting();
    curfleetid=0;
  } else {
    var mapdiv = document.getElementById('mapdiv');
    var newmenu = document.createElement('div');
    newmenu.setAttribute('id','menu');
    newmenu.setAttribute('style','position:absolute; top:'+(evt.clientY+10)+
                        'px; left:'+(evt.clientX+10)+
                        'px; background-color: #002244; '+
                        '-moz-border-radius-topright: 10px; '+
                        '-moz-border-radius-bottomleft: 10px; '+
                        'padding-top: 10px; padding-bottom: 10px;');
    handlemenuitemreq('planets', 'root', planet);
    mapdiv.appendChild(newmenu);
  } 
}


function domousedown(evt)
{
  if(evt.preventDefault){
    evt.preventDefault();
  }
  killmenu();
  document.body.style.cursor='move';
  mouseorigin = getcurxy(evt);
  mousedown = true;
}

function domouseup(evt)
{
  if(evt.preventDefault){
    evt.preventDefault();
  }
  if(evt.detail==2){
    zoom(evt,.7);
  }
  document.body.style.cursor='default';
  mousedown = false;
  rubberband.setAttribute('visibility','hidden');
  if((curfleetid)&&(!curplanetid)){
    var curloc = getcurxy(evt);
    movefleettoloc(evt,curfleetid,curloc)
    curfleetid=0;
  }
}

function domousemove(evt)
{
  if(evt.preventDefault){
    evt.preventDefault();
  }             
  if(mousedown == true){
    var viewbox = getviewbox(map);
    var neworigin = getcurxy(evt);
    var dx = (mouseorigin.x - neworigin.x);
    var dy = (mouseorigin.y - neworigin.y);
    viewbox[0] = viewbox[0] + dx;
    viewbox[1] = viewbox[1] + dy;
    map.setAttributeNS(null,"viewBox",viewbox.join(" "));
  }
  if(curfleetid){
    var newcenter = getcurxy(evt);
    rubberband.setAttribute('x2',newcenter.x);
    rubberband.setAttribute('y2',newcenter.y);
  }
}

function init(e)
{
  map = document.getElementById('map');
  rubberband = document.getElementById('rubberband');
  offset = map.createSVGPoint();
  originalview = getviewbox(map);
  setaspectratio();
}

function setaspectratio()
{
  var height = parseFloat(window.innerHeight);
  var width = parseFloat(window.innerWidth);
  var vb = originalview.slice();    // force a deep copy
  if(width>height){
    var aspectratio = height/width;
    var centery = vb[1] + (vb[3]/2.0);
    vb[1] = centery - vb[3]*aspectratio/2.0;
    vb[3] = vb[3]*aspectratio;
    map.setAttributeNS(null,"viewBox",vb.join(" "));
  } else {
    var aspectratio = width/height;
    var centerx = vb[0] + (vb[2]/2.0);
    vb[0] = centerx - vb[2]*aspectratio/2.0;
    vb[2] = vb[2]*aspectratio;
    map.setAttributeNS(null,"viewBox",vb.join(" "));
  }
}

function zoom(evt, magnification)
{
  if(evt.preventDefault){
    evt.preventDefault();
  }
  if(evt.detail == 2){
    var newcenter = getcurxy(evt);

    var halfmag = magnification/2.0;
    var viewbox = getviewbox(map);
    var newviewbox = new Array();
    newviewbox[0] = newcenter.x-(viewbox[2]*halfmag);
    newviewbox[1] = newcenter.y-(viewbox[3]*halfmag);
    newviewbox[2] = viewbox[2]*magnification;
    newviewbox[3] = viewbox[3]*magnification;
    map.setAttributeNS(null,"viewBox",newviewbox.join(" "));
  }
}


function getviewbox(doc)
{
  var newviewbox = doc.getAttributeNS(null,"viewBox").split(/\s*,\s*|\s+/);
  for (i in newviewbox){
    newviewbox[i] = parseFloat(newviewbox[i]);
  }
  return newviewbox;
}

function killmenu()
{
  var oldmenu = document.getElementById('menu');
  if(oldmenu){
    oldmenu.parentNode.removeChild(oldmenu);
  }
}


function setmenuwaiting()
{
  var menu = document.getElementById('menu');
  if(menu){
    menu.innerHTML = '<div><img src="/site_media/ajax-loader.gif">loading...</img></div>';
  }
}



function getcurxy(evt)
{
  var p = map.createSVGPoint();
  p.x = evt.clientX;
  p.y = evt.clientY;
  p = p.matrixTransform(map.getScreenCTM().inverse());
  return p;
}

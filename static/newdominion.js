var svgns = "http://www.w3.org/2000/svg";

var maplayer1;
var maplayer2;
var zoomlevel = 3;
var timeleft = "+500s"
var originalview = [];
var mousedown = new Boolean(false);
var offset;
var mouseorigin;
var map;
var server = new XMLHttpRequest();
var curfleetid = 0;
var curplanetid = 0;
var rubberband;
var youarehere;
var curx, cury;
var mousecounter = 0;

var sectors = [];
var onscreensectors = [];
$(document).ready(function() {
	$('#countdown').countdown({description:'Turn Ends', until: timeleft, format: 'hms'});
});



function getsectors(newsectors,force)
{
  var submission = [];
  // convert newsectors (which comes in as a straight array)
  // over to the loaded sectors array (which is associative...)
  // and see if we have already asked for that sector (or indeed
  // already have it in memory, doesn't really matter...)
  for (sector in newsectors){
    if((force==1)||(!(sector in sectors))){
      submission.push(sector);
      sectors[sector] = "";
    }
  }
  if(submission.length > 0){
    submission = submission.join('&');
    sendrequest(loadnewsectors,"/sectors/",'POST',submission);
    setstatusmsg("Requesting Sectors");
  }
}


function buildsectorfleets(sector,newsectorl1,newsectorl2)
{
  for(fleetkey in sector['fleets']){
    var fleet = sector['fleets'][fleetkey]

    if ('s' in fleet){
      var circle = document.createElementNS(svgns, 'circle');
      var color = $.RGB(fleet.c);
      color[0] = color[0]/20;
      color[1] = color[1]/20;
      color[2] = color[2]/20;
      //alert(color);
      var colorstr = "rgb("+parseInt(color[0])+","+parseInt(color[1])+","+parseInt(color[2])+")"
      //alert(colorstr);
      circle.setAttribute('cx', fleet.x);
      circle.setAttribute('cy', fleet.y);
      circle.setAttribute('r', fleet.s);
      //alert(fleet.s);
      circle.setAttribute('fill',colorstr);
      newsectorl1.appendChild(circle);
    }

    if ('x2' in fleet){
      var line = document.createElementNS(svgns, 'line');
      line.setAttribute('stroke-width', '.02');
      line.setAttribute('stroke', "white");
      line.setAttribute('marker-end', 'url(#endArrow)');
      line.setAttribute('x1', fleet.x);
      line.setAttribute('y1', fleet.y);
      line.setAttribute('x2', fleet.x2);
      line.setAttribute('y2', fleet.y2);
      line.setAttribute('stroke-opacity', '.5');
      newsectorl2.appendChild(line);
    }
    var circle = document.createElementNS(svgns, 'circle');
    var playerowned;
    if ('ps' in fleet){
      playerowned=1;
    } else {
      playerowned=0;
    }
    circle.setAttribute('cx', fleet.x);
    circle.setAttribute('cy', fleet.y);
    circle.setAttribute('r', '.04');
    circle.setAttribute('fill', fleet.c);
    circle.setAttribute('id', 'f'+fleet.i);
    circle.setAttribute('onmouseover',
                        'fleethoveron(evt,"'+fleet.i+'")');
    circle.setAttribute('onmouseout',
                        'fleethoveroff(evt,"'+fleet.i+'")');
    circle.setAttribute('onclick',
                        'dofleetmousedown(evt,"'+fleet.i+'",'+playerowned+')');
    newsectorl2.appendChild(circle);
  } 
}


function buildsectorplanets(sector,newsectorl1, newsectorl2)
{
  for(planetkey in sector['planets']){
    var planet = sector['planets'][planetkey]
    if (((newplayer == 1) && ('pp' in planet))){
      var line = document.createElementNS(svgns, 'line');
      line.setAttribute('stroke-width', '.02');
      line.setAttribute('stroke', '#aaaaaa');
      line.setAttribute('marker-end', 'url(#endArrow)');
      line.setAttribute('x2', planet.x-.2);
      line.setAttribute('y2', planet.y+.3);
      line.setAttribute('x1', planet.x-.7);
      line.setAttribute('y1', planet.y+1.0);
      newsectorl2.appendChild(line);
      youarehere.setAttribute('visibility','visible');
      youarehere.setAttribute('x',planet.x-1.5);
      youarehere.setAttribute('y',planet.y+1.3);
    }

    if ('s' in planet){
      var circle = document.createElementNS(svgns, 'circle');
      var color = $.RGB(planet.h);
      color[0] = color[0]/20;
      color[1] = color[1]/20;
      color[2] = color[2]/20;
      //alert(color);
      var colorstr = "rgb("+parseInt(color[0])+","+parseInt(color[1])+","+parseInt(color[2])+")"
      //alert(colorstr);
      circle.setAttribute('cx',  planet.x);
      circle.setAttribute('cy',  planet.y);
      circle.setAttribute('r',   planet.s);
      //alert(fleet.s);
      circle.setAttribute('fill',colorstr);
      newsectorl1.appendChild(circle);
    }


    if ('cap' in planet){
      var highlight = document.createElementNS(svgns, 'circle');
      highlight.setAttribute('cx', planet.x);
      highlight.setAttribute('cy', planet.y);
      highlight.setAttribute('r', planet.r+.12);
      highlight.setAttribute('stroke', planet.h);
      highlight.setAttribute('stroke-width', '.02');
      highlight.setAttribute('stroke-opacity', '.5');
      newsectorl2.appendChild(highlight);
    }  
    if (planet.h != 0){
      var highlight = document.createElementNS(svgns, 'circle');
      highlight.setAttribute('cx', planet.x);
      highlight.setAttribute('cy', planet.y);
      highlight.setAttribute('r', planet.r+.06);
      highlight.setAttribute('stroke', planet.h);
      highlight.setAttribute('stroke-width', '.04');
      newsectorl2.appendChild(highlight);
    }
    var circle = document.createElementNS(svgns, 'circle');
    var playerowned=0;
    if ('pp' in planet){
      playerowned=1;
    } else {
      playerowned=0;
    }
    circle.setAttribute('id', planet.i);
    circle.setAttribute('cx', planet.x);
    circle.setAttribute('cy', planet.y);
    circle.setAttribute('r', planet.r);
    circle.setAttribute('fill', planet.c);
    circle.setAttribute('onmouseover',
                        'planethoveron(evt,"'+planet.i+'")');
    circle.setAttribute('onmouseout',
                        'planethoveroff(evt,"'+planet.i+'")');
    circle.setAttribute('onclick',
                        'doplanetmousedown(evt,"'+planet.i+'",'+playerowned+')');
    newsectorl2.appendChild(circle);
  }
}

function loadnewsectors()
{
  if((server.readyState == 4) && (server.status == 500)){
    w = window.open('');
    w.document.write(server.responseText);
  }
  if((server.readyState == 4) && (server.status == 200)){
    hidestatusmsg();
    var newsectors = eval("("+server.responseText+")");
    var viewable = viewablesectors(getviewbox(map));
    var deletesectors = [];
    
    for (sector in newsectors){
      if(sector in onscreensectors){
        deletesectors[sector] = 1;
      }
      sectors[sector] = newsectors[sector];
    }


    // first, remove out of view sectors...
    for (key in onscreensectors){
      if ((!(key in viewable))&&(onscreensectors[key]=='+')){
        deletesectors[key] = 1;
      }
    }
    for (key in deletesectors){
      onscreensectors[key] = '-';
      var remsector;
      
      remsector = document.getElementById('sectorl1-'+key);
      if(remsector)maplayer1.removeChild(remsector);

      remsector = document.getElementById('sectorl2-'+key);
      if(remsector)maplayer2.removeChild(remsector);
    }
    adjustview(viewable);
  }
}

function adjustview(viewable)
{
  for (key in viewable){
    //key = viewable[key];
    var sectoridl1 = "sectorl1-"+key;
    var sectoridl2 = "sectorl2-"+key;
    if (((!(key in onscreensectors))||(onscreensectors[key]=='-'))&&(key in sectors)){
      onscreensectors[key] = "+";
      var newsectorl1 = document.createElementNS(svgns, 'g');
      var newsectorl2 = document.createElementNS(svgns, 'g');

      newsectorl2.setAttribute('id', sectoridl2);
      newsectorl2.setAttribute('class', 'mapgroupx');
      
      newsectorl1.setAttribute('id', sectoridl1);
      newsectorl1.setAttribute('class', 'mapgroupx');
      
      var sector = sectors[key];

      buildsectorfleets(sector,newsectorl1,newsectorl2);
      buildsectorplanets(sector,newsectorl1, newsectorl2)

      maplayer1.appendChild(newsectorl1);
      maplayer2.appendChild(newsectorl2);
    }
  }
}

function setxy(evt)
{
  cury = evt.clientY;
  curx = evt.clientX;
}

function movemenu(x,y)
{
  $("#menu").css('top',y);
  $("#menu").css('left',x);
}

function changebuildlist(shiptype, change)
{
  var columns = [];
  var rows = [];
  var numships = [];
  var rowtotal = $('#num-'+shiptype).val();
  var hidebuttons = false;
  
  if (rowtotal == ""){
    rowtotal = 0;
  } else {
    rowtotal = parseInt(rowtotal);
  }
  
  rowtotal += change;
  if (rowtotal < 0){
    rowtotal = 0;
  }

  // set the new number of ships to build
  $('#num-'+shiptype).val(rowtotal);
  $("th[id ^= 'col-']").each(function() {
    // get column headers 
    columns.push($(this).attr('id').split('-')[1])
    });
    
  $("td[id ^= 'row-']").each(function() {
    // get row names
    var curshiptype = $(this).attr('id').split('-')[1];
    rows.push(curshiptype)
    });
  for(column in columns){
    var colname = columns[column];
    var qry = 'required-' + colname;
    var coltotal = 0;
    $("td[id ^= '" +qry+ "']").each(function() {
      var curshiptype = $(this).attr('id').split('-')[2];
      var curnumships = parseInt($('#num-'+curshiptype).val());
      coltotal += (parseInt($(this).html()) * curnumships);
      });
    var available = parseInt($("#available-"+colname).html());
    coltotal = available-coltotal;
    $("#total-"+colname).html(coltotal);
    if(coltotal < 0){
      $("#total-"+colname).css('color','red');
      hidebuttons=true;
    } else {
      $("#total-"+colname).css('color','white');
    }
  }

  // add up ship totals
  var totalships = 0;
  $("input[id ^= 'num-']").each(function() {
    totalships += parseInt($(this).val());
  });

  if(totalships==0){
    hidebuttons = true;
  }

  if(!hidebuttons){
    $("#submit-build").show();
  } else {
    $("#submit-build").hide();
  }

  $("#total-ships").html(totalships);
}

  
function setstatusmsg(msg)
{
  $('#statusmsg').html(msg);
  $('#statusmsg').show("fast");
}

function hidestatusmsg()
{
  $('#statusmsg').hide("fast");
}

function rubberbandfromfleet(fleetid,initialx,initialy)
{
  curfleetid = fleetid;
  killmenu();
  
  setstatusmsg("Select Destination");
  rubberband.setAttribute('visibility','visible');
  rubberband.setAttribute('x1',initialx);
  rubberband.setAttribute('y1',initialy);
}

function loadnewmenu()
{
  if((server.readyState == 4) && (server.status == 500)){
    w = window.open('');
    w.document.write(server.responseText);
  }
  if ((server.readyState == 4)&&(server.status == 200)){
    hidestatusmsg();
    var response  = server.responseText;
    buildmenu(); 
    $('#menu').html(response);
  }
}

function newmenu(request, method, postdata)
{
  setmenuwaiting();
  sendrequest(loadnewmenu,request,method,postdata);
  var mapdiv = document.getElementById('mapdiv');
  var newmenu = buildmenu();    
  mapdiv.appendChild(newmenu);
}
function sendrequest(callback,request,method,postdata)
{
  server.open(method, request, true);
  server.setRequestHeader('Content-Type',
                           'application/x-www-form-urlencoded');
  server.onreadystatechange = callback;
  if(typeof postdata == 'undefined'){
    server.send(null);
  } else {
    server.send(postdata);
  }
  setmenuwaiting();
}

function handlemenuitemreq(type, requestedmenu, id)
{
  var myurl = "/"+type+"/"+id+"/" + requestedmenu + "/";
  sendrequest(loadnewmenu,myurl, "GET");
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
  for(i in subform.getElementsByTagName('button')){
    var formbutton = subform.getElementsByTagName('button')[i];
    submission.push(formbutton.id + "=" + "1");
  }
  for(i in subform.getElementsByTagName('textarea')){
    var textarea = subform.getElementsByTagName('textarea')[i];
    submission.push(textarea.name + '=' + textarea.value);
    }
  for(i in subform.getElementsByTagName('input')){
    var formfield = subform.getElementsByTagName('input')[i];
    if(formfield.name){
      if(formfield.type=="radio"){
        if(formfield.checked){
          submission.push(formfield.name + '=' + formfield.value);
        }
      } else if(formfield.type=="checkbox"){
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
  sendrequest(loadnewmenu,request,'POST',submission);
}

function zoomcircleid(factor,id)
{
  var circle = document.getElementById(id);
  if(circle){
    var radius = circle.getAttribute("r");
    radius *= factor;
    circle.setAttribute("r", radius);
  }
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
  if(curfleetid){
    setstatusmsg("Left Click to Send Fleet to Planet");
  } else if($('#menu').size()==0){
    setstatusmsg("Left Click to Manage Planet");
  }
  setxy(evt);
  zoomcircle(evt,2.0);
  curplanetid = planet;
}

function planethoveroff(evt,planet)
{
  hidestatusmsg();
  setxy(evt);
  zoomcircle(evt,.5);
  curplanetid = 0;
}

function fleethoveron(evt,fleet)
{
  if($('#menu').size()==0){
    setstatusmsg("Left Click to Manage Fleet");
  }
  setxy(evt);
  zoomcircle(evt,2.0);
}

function fleethoveroff(evt,fleet)
{
  hidestatusmsg();
  setxy(evt);
  zoomcircle(evt,.5);
}

function buildmenu()
{
  if($('#menu').size()){
    return $('#menu');
  } else {
    var mapdiv = document.getElementById('mapdiv');
    var newmenu = document.createElement('div');
    newmenu.setAttribute('id','menu');
    newmenu.setAttribute('style','position:absolute; top:'+(cury+10)+
                         'px; left:'+(curx+10)+ 'px;');
    newmenu.setAttribute('class','menu');
    setmenuwaiting()
    return newmenu;
  }
}
function dofleetmousedown(evt,fleet,playerowned)
{
  setxy(evt);
  if(curfleetid==fleet){
    curfleetid=0;
  } else if(!curfleetid){
    var newmenu = buildmenu();
    if(playerowned==1){
      handlemenuitemreq('fleets', 'root', fleet);
    } else {
      handlemenuitemreq('fleets', 'info', fleet);
    }
    var mapdiv = document.getElementById('mapdiv');
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
  setxy(evt);
  var request = "/fleets/"+fleet+"/movetoloc/";
  var submission = "x=" + curloc.x + "&y=" + curloc.y;

  sendrequest(loadnewsectors,request,'POST',submission);
}

function doplanetmousedown(evt,planet,playerowned)
{
  setxy(evt);
  if(curfleetid){
    var request = "/fleets/"+curfleetid+"/movetoplanet/";
    var submission = "planet=" + planet;

    sendrequest(loadnewsectors, request, 'POST', submission);
    curfleetid=0;
  } else {
    var mapdiv = document.getElementById('mapdiv');
    var newmenu = buildmenu();    
    if(playerowned==1){
      handlemenuitemreq('planets', 'root', planet);
    } else {
      handlemenuitemreq('planets', 'info', planet);
    }

    mapdiv.appendChild(newmenu);
  } 
}


function domousedown(evt)
{
  setxy(evt);
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
  setxy(evt);
  if(evt.preventDefault){
    evt.preventDefault();
  }
  if(evt.detail==2){
    zoom(evt,.714285714,getcurxy(evt));
  }
  document.body.style.cursor='default';
  mousedown = false;
  rubberband.setAttribute('visibility','hidden');
  if((curfleetid)&&(!curplanetid)){
    var curloc = getcurxy(evt);
    movefleettoloc(evt,curfleetid,curloc)
    curfleetid=0;
  }

  var dosectors = viewablesectors(getviewbox(map));
  getsectors(dosectors,0);
  adjustview(dosectors);
}


function viewablesectors(viewbox)
{
  var topx = parseInt(viewbox[0]/5.0);
  var topy = parseInt(viewbox[1]/5.0);
  var width = parseInt(viewbox[2]/5.0)+2;
  var height = parseInt(viewbox[3]/5.0)+2;
  var i=0,j=0;
  var dosectors = [];
  for(i=topx;i<topx+width;i++){
    for(j=topy;j<topy+height;j++){
      var cursector = i*1000+j;
      dosectors[cursector.toString()] = 1;
    }
  }
  return dosectors;
}

function domousemove(evt)
{
  if(evt.preventDefault){
    evt.preventDefault();
  }             
  mousecounter++;
  if((mousedown == true)&&(mousecounter%3 == 0)){
    var viewbox = getviewbox(map);
    var neworigin = getcurxy(evt);
    var dx = (mouseorigin.x - neworigin.x);
    var dy = (mouseorigin.y - neworigin.y);
    var dosectors;
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

function init(e,timeleftinturn)
{
  map = document.getElementById('map');
  maplayer1 = document.getElementById('maplayer1');
  maplayer2 = document.getElementById('maplayer2');
  rubberband = document.getElementById('rubberband');
  youarehere = document.getElementById('youarehere');
  offset = map.createSVGPoint();
  originalview = getviewbox(map);
  setaspectratio();
  var dosectors = viewablesectors(originalview);
  getsectors(dosectors,0);

	timeleft = timeleftinturn;
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

function zoommiddle(evt, magnification)
{
  var viewbox = getviewbox(map);
  var newcenter = map.createSVGPoint();
  newcenter.x = viewbox[0]+(viewbox[2]/2.0);
  newcenter.y = viewbox[1]+(viewbox[3]/2.0);
  zoom(evt,magnification,newcenter);
}
function expandtoggle(id)
{
  if($(id).attr('src') == '/site_media/expandup.png'){
    $(id).attr('src', '/site_media/expanddown.png');
  } else {
    $(id).attr('src', '/site_media/expandup.png');
  }
}

function zoom(evt, magnification, newcenter)
{
  if(evt.preventDefault){
    evt.preventDefault();
  }
  var changezoom = 0;
  if((magnification > 1)&&(zoomlevel<6)){
    changezoom = 1;
    zoomlevel++;
  } else if((magnification < 1)&&(zoomlevel>0)){
    changezoom = 1;
    zoomlevel--;
  }
  if(changezoom){
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
  setstatusmsg("Loading...");
  $('#menu').html('<div><img src="/site_media/ajax-loader.gif">loading...</img></div>');
}



function getcurxy(evt)
{
  var p = map.createSVGPoint();
  p.x = evt.clientX;
  p.y = evt.clientY;
  p = p.matrixTransform(map.getScreenCTM().inverse());
  return p;
}

var svgns = "http://www.w3.org/2000/svg";

var map;
var curwidth;
var curheight;
var curcenter;
var maplayer0;
var maplayer1;
var maplayer2;
var routes = [];
var svgmarkers;
var zoomlevel = 3;
var zoomlevels = [100.0,90.0,80.0,60.0,45.0,30.0,15.0];
var timeleft = "+500s";
var originalview = [];
var helpstack = [];
var tips = [];
var mousedown = false;
var mouseorigin;
var server = new XMLHttpRequest();
var resizeTimer = null;
var curfleetid = 0;
var curplanetid = 0;
var currouteid = 0;
var curslider = "";
var rubberband;
var sectorlines;
var youarehere;
//var curx, cury;
var mousepos;
var mousecounter = 0;
var sectors = [];
var sectorsstatus = [];
var transienttabs;
var permanenttabs;
var buildanother = 0;
var currentbuildplanet = "";
var sectorgeneration = 0;



function popfont(id)
{
  var text = document.getElementById(id);
  if(text){
    text.setAttribute("fill","yellow");
  }
}
function unpopfont(id)
{
  var text = document.getElementById(id);
  if(text){
    text.setAttribute("fill","white");
  }
}

function handleerror(response)
{
  var nw = window.open('','MyNewWindow','width=200,height=100,left=200,top=100'); 
  nw.document.write(response.responseText);
  nw.document.close();
}

function getdistance(x1,y1,x2,y2)
{
  var dx = x1-x2;
  var dy = y1-y2;
  return Math.sqrt(dx*dx+dy*dy);
}

function SliderContainer(id, newside)
{
  var side = newside;
  var tabs = {};
  var container = "#"+id;
  var openedtab = "";
  var temphidetab = "";

  this.opened = false;
  this.settabcontent = function(tab, content){
    var tabsel = container + " #"+tab+"content";
    if(content === ""){
      content = '<div><img src="/site_media/ajax-loader.gif">loading...</img></div>';
    }
    $(tabsel).empty().append(content); 
  };

  this.isopen = function(){
    return this.opened;
  }

  this.removetab = function(remid){
    $(container+' #'+remid).remove();
    if(this.opened === true && remid === openedtab){
      this.hidetabs();
    } 
      
  };

  this.alreadyopen = function(tab){
    var checktab = container + " #"+tab;
    if(($(checktab).size() > 0) && (this.opened===true)){
      return true;
    } else {
      return false;
    }
  };



  this.displaytab = function(showtab){
    var showtabsel = container + ' #'+showtab;
    if(this.opened===false){
      $(container + " .slidertab"+side).hide();
      $(container + " .slidertab"+side+" .slidercontent"+side).hide();
      $(container + " .slidertab"+side+" .ph .slidercontent"+side).hide();
      $(showtabsel+"title").show();
      $(showtabsel+"content").show();
      openedtab = showtab;
      this.opened = true;
      $(container).ready(function() {
        $(showtabsel).show('fast');
      });
    }
  };

  this.temphidetabs = function(){
    if(this.opened===true){
      temphidetab = openedtab;
      this.hidetabs();
    }
  };

  this.tempcleartabs = function(){
    temphidetab = "";
  };

  this.tempshowtabs = function(){
    if((this.opened===false)&&(temphidetab !== "")){
      this.displaytab(temphidetab);
    }
    temphidetab = "";
  };

  this.hidetabs = function(){ 
    $(container + " .slidertab"+side+" .ph .slidercontent"+side).hide();
    $(container + " .slidertab"+side+" .slidertitle"+side).show();
    $(container + " .slidertab"+side).show();
    this.opened = false;
    openedtab = "";
  };

  this.reloadtab = function(tab){
    this.gettaburl(tabs[tab]);
  };

  this.gettaburl = function(tab, newurl){
    tabs[tab] = newurl;
    var tabsel = container + " #"+tab+"content";
    $.ajax({ 
      url: newurl, 
      cache: false, 
      dataType: 'json',
      success: function(message) 
      {
        $(tabsel).empty().append(message.pagedata);
      } 
    }); 
  };

  this.closehandler = function(tab,handler){
    var tabsel = container + " #"+tab+"close";
    $(tabsel).bind('click', {'tabcontainer': this}, handler);
  };

  this.pushtab = function(newid, title, contents, permanent){
    var fullpath = container + " " + '#'+newid;
    var content = '';
    tabs[newid] = ''; 
    // if tab already exists, then replace it's content with the new stuff...
    if($(fullpath).size() > 0){
      this.settabcontent(newid, contents);
      return;
    }

    this.hidetabs();

    $('<div id="'+newid+'" class="slidertab'+side+'"/>').appendTo(container);
    $('<div id="'+newid+'title" class="slidertitle'+side+'"/>').appendTo(fullpath);
    
    
    content  = '<div class="ph">';
    content += '  <svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="1" height="1"/>';
    content += '  <div id="'+newid+'content" class="slidercontent'+side+'">'+contents+'</div>';
    content += '</div>';
    $(content).appendTo(fullpath);
    this.settabcontent(newid, contents);
    
    if((side === 'left')||(side === 'right')){
      var svgtitle = "";
      $(fullpath +'title').mouseover(function(){popfont(newid+'titletext');});
      $(fullpath+'title').mouseout(function(){unpopfont(newid+'titletext');});
      if(permanent===false){
        svgtitle  = '<div><img id="'+newid+'close" class="noborder" title="close tab" src="/site_media/scrap.png"/></div>';
      }
      svgtitle += '<svg xmlns="http://www.w3.org/2000/svg" version="1.1"';
      svgtitle += '     id="'+newid+'titletextcontainer" width="14" height="60">';
      svgtitle += '  <text id="'+newid+'titletext" font-size="12"';
      if(side === 'right'){
        svgtitle += '        text-anchor="left" transform="rotate(90)"';
        svgtitle += '        x="17" y="-2" fill="white">';
      } else if (side === 'left'){
        svgtitle += '        text-anchor="end" transform="rotate(-90)"';
        svgtitle += '        x="-10" y="12" fill="white">';
      }
      svgtitle += '    '+title;
      svgtitle += '  </text>';
      svgtitle += '</svg>';
      $(svgtitle).appendTo(fullpath+'title');
     
      // set the height of the the svg container so all the text shows up
      var labeltext = document.getElementById(newid+'titletext');
      var height = labeltext.getComputedTextLength();
      var labelcontainer = document.getElementById(newid+'titletextcontainer');
      
      if(permanent===false){
        labelcontainer.setAttribute('height', height+20);
      } else {
        labelcontainer.setAttribute('height', height+18);
      }

      if(permanent === false){
        this.closehandler(newid, 
                          function(event){
                            var tc = event.data.tabcontainer;
                            tc.removetab(newid);});
      }
    } else {
      $(fullpath+'title').append(title);
    }

    $(fullpath+'title').bind('click', {'tabcontainer': this}, function(event){
      var tc = event.data.tabcontainer;
      if(tc.opened===false){
        tc.displaytab(newid);
      } else {
        tc.hidetabs();
      }
    });
  };
}

function stringprompt(args)
{
  // args: title, headline, submitfunction, cancelfunction, submit, cancel
  //       maxlen, text
  if(typeof stringprompt.counter == 'undefined' ) {
    stringprompt.counter = 0;
  }
  var contents = "";
  var submitid = 'tps'+stringprompt.counter;
  var formid   = 'tpf'+stringprompt.counter;
  var cancelid = 'tpc'+stringprompt.counter;
  var stringid = 'tp'+stringprompt.counter;
  var containerid = 'textprompt'+stringprompt.counter;
  contents += '<div style="min-height: 130px;">';
  contents += '  <h1>' + args.headline + '</h1>';
  contents += '  <form id="'+formid+'" onsubmit="return false;"><table>';
  contents += '    <tr><td colspan="2"><input tabindex="1" maxlength="'+args.maxlen+'" type="text" value="' + args.text + '" id="' + stringid +'" /></td></tr>';
  contents += '    <tr><td><input type="button"  tabindex="3" value="'+args.cancel+'" id="' + cancelid + '" /></td>';
  contents += '    <td style="padding-top:10px;"><input tabindex="2" type="button" value="'+args.submit+'" id="' + submitid + '" /></td></tr>';
  contents += '  </table></form>';
  contents += '</div>';
  contents += '<script>$(document).ready(function(){$("#'+stringid+'").focus();});</script>'
 


  transienttabs.pushtab(containerid, args.title, contents,false);
  transienttabs.displaytab(containerid);
  $('#'+submitid).click(function(event) {
    var string = $('#'+stringid).val();
    args.submitfunction(args,string);
    stopprop(event);
    transienttabs.removetab(containerid);
  });
  $('#'+formid).submit(function(event) {
    $('#'+submitid).trigger('click')
  });

  $('#'+cancelid).click(function(){
    args.cancelfunction(args);
    transienttabs.removetab(containerid);
  });
  $('#'+stringid).focus();
  stringprompt.counter++;

}


function sendrequest(callback,request,method,postdata)
{
  //setmenuwaiting();
  $.ajax( 
  { 
    url: request, 
    cache: false, 
    success: callback,
    type: method,
    data: postdata,
    error: handleerror,
    dataType: 'json'
  });
}

function Point(x,y)
{
  this.x = x;
  this.y = y;
}

function Sector(key,jsondata)
{
  this.json = jsondata;
  this.planets = jsondata.planets;
  this.fleets = jsondata.fleets;
  this.key = key;
}
  
function getcurxy(evt)
{
  var p = new Point(evt.pageX,evt.pageY);
  return p;
}

function setstatusmsg(msg)
{
  $('#statusmsg').html(msg);
  $('#statusmsg').show();
}

function setmenuwaiting()
{
  setstatusmsg("Loading...");
  $('#menu').html('<div><img src="/site_media/ajax-loader.gif">loading...</img></div>');
}

function killmenu()
{
  $('#menu').hide();
}


function hidestatusmsg(msg)
{
  $('#statusmsg').hide();
}

function getviewbox(doc)
{
  var i = 0;
  var newviewbox = doc.getAttributeNS(null,"viewBox").split(/\s*,\s*|\s+/);
  for (i in newviewbox){
    if(typeof i === 'string'){
      newviewbox[i] = parseFloat(newviewbox[i]);
    }
  }
  return newviewbox;
}
         



function setviewbox(viewbox)
{
  curcenter.x = viewbox[0]+(viewbox[2]/2.0);
  curcenter.y = viewbox[1]+(viewbox[3]/2.0);
  curwidth = viewbox[2];
  curheight = viewbox[3];
  map.setAttribute("viewBox",viewbox.join(" "));
  map.setAttribute("width",curwidth);
  map.setAttribute("height",curheight);
  
}

function viewablesectors(viewbox)
{
  var cz =     zoomlevels[zoomlevel];
  var topx =   parseInt((viewbox[0]/cz)/5.0, 10);
  var topy =   parseInt((viewbox[1]/cz)/5.0, 10);
  var width =  parseInt((viewbox[2]/cz)/5.0, 10)+2;
  var height = parseInt((viewbox[3]/cz)/5.0, 10)+2;
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


function buildmarker(color)
{
  marker = document.createElementNS(svgns, 'marker');
  marker.setAttribute('id','marker-'+color.substring(1));
  marker.setAttribute('viewBox','0 0 10 10');
  marker.setAttribute('refX',1);
  marker.setAttribute('refY',5);
  marker.setAttribute('markerUnits','strokeWidth');
  marker.setAttribute('orient','auto');
  marker.setAttribute('markerWidth','5');
  marker.setAttribute('markerHeight','4');
  var pline = document.createElementNS(svgns, 'polyline');
  pline.setAttribute('points','0,0 10,5 0,10 1,5');
  pline.setAttribute('fill',color);
  pline.setAttribute('fill-opacity','1.0');
  marker.appendChild(pline);
  svgmarkers.appendChild(marker);
  return marker;
}

function buildsectorrings()
{
  var cz = zoomlevels[zoomlevel];

  
  vb = getviewbox(map);
  var minx = vb[0]/cz;
  var miny = vb[1]/cz;
  var maxx = minx + vb[2]/cz;
  var maxy = miny + vb[3]/cz;
  
  var angle1 = Math.atan2(1500.0-miny,1500.0-minx);
  var angle2 = Math.atan2(1500.0-miny,1500.0-maxx);
  var angle3 = Math.atan2(1500.0-maxy,1500.0-minx);
  var angle4 = Math.atan2(1500.0-maxy,1500.0-maxx);
  
  var distance1 = getdistance(1500,1500,minx,miny);
  var distance2 = getdistance(1500,1500,maxx,miny);
  var distance3 = getdistance(1500,1500,minx,maxy);
  var distance4 = getdistance(1500,1500,maxx,maxy);
 
  var mindistance = 10000;
  var maxdistance = -10000;

  if (distance1 < mindistance)mindistance = distance1;
  if (distance2 < mindistance)mindistance = distance2;
  if (distance3 < mindistance)mindistance = distance3;
  if (distance4 < mindistance)mindistance = distance4;
  
  if (distance1 > maxdistance)maxdistance = distance1;
  if (distance2 > maxdistance)maxdistance = distance2;
  if (distance3 > maxdistance)maxdistance = distance3;
  if (distance4 > maxdistance)maxdistance = distance4;

  var minangle = 10.0;
  var maxangle = -10.0;

  if (angle1 < minangle)minangle = angle1; 
  if (angle2 < minangle)minangle = angle2; 
  if (angle3 < minangle)minangle = angle3; 
  if (angle4 < minangle)minangle = angle4; 
  
  if (angle1 > maxangle)maxangle = angle1; 
  if (angle2 > maxangle)maxangle = angle2; 
  if (angle3 > maxangle)maxangle = angle3; 
  if (angle4 > maxangle)maxangle = angle4;

  if (mindistance < 50){
    mindistance = 0;
    minangle = 0;
    maxangle = 3.14159*2;
  }

  if((minangle < 0) && (maxangle < 0)){
    minangle+=(3.14159*2);
    maxangle+=(3.14159*2);
    drawlines(minangle,maxangle,mindistance,maxdistance,cz);
  } else if ((minangle < 0) && (maxangle > 0)){
    if (maxangle-minangle > 2){
      minangle+=(3.14159*2);
      drawlines(minangle,maxangle,mindistance,maxdistance,cz);
    } else {
      drawlines(minangle,0,mindistance,maxdistance,cz);
      drawlines(0,maxangle,mindistance,maxdistance,cz);
    }
  } else {
    drawlines(minangle,maxangle,mindistance,maxdistance,cz);
  }

   
}

function drawlines(minangle, maxangle, mindistance, maxdistance,cz){
  if(minangle > maxangle){
    var temp = minangle;
    minangle=maxangle;
    maxangle = temp;
  }
  stepangle = (3.14159*2.0)/128.0;
  // expand drawing to cover enough area off screen
  // to allow the user to pan without pop in/out.
  minangle -= stepangle;
  maxangle += stepangle;
  var sign = '+';
  if(minangle<0){
    sign = '-';
  }
  for (i=80;i>0;i--){
    var ring = document.getElementById("sectorring"+ sign + i);
    if((i*20 > mindistance) && (i*20 < (maxdistance+(maxdistance-mindistance)))){
      if(i<4){
        if(!ring){
          ring = document.createElementNS(svgns,'circle');
          ring.setAttribute('stroke',"#280000");
          ring.setAttribute('fill',"none");
          ring.setAttribute('id',"sectorring"+i);
          ring.setAttribute('stroke-width',"3");
          maplayer0.appendChild(ring);
        }
        ring.setAttribute('cx',1500*cz);
        ring.setAttribute('cy',1500*cz);
        ring.setAttribute('r',i*20*cz);
      } else {
        if(!ring){
          ring = document.createElementNS(svgns,'path');
          ring.setAttribute('stroke',"#280000");
          ring.setAttribute('fill',"none");
          ring.setAttribute('id',"sectorring"+i);
          ring.setAttribute('stroke-width',"3");
          maplayer0.appendChild(ring);
        }
        var radius = i*20*cz;
        var startx = (1500-Math.cos(minangle)*i*20)*cz;
        var starty = (1500-Math.sin(minangle)*i*20)*cz;
        var endx =   (1500-Math.cos(maxangle)*i*20)*cz;
        var endy =   (1500-Math.sin(maxangle)*i*20)*cz;
        var path = "M " + startx + " " + starty + " A " + 
                   radius + " " + radius + " 0 0 1 " + 
                   endx + " " + endy;
        ring.setAttribute('d',path);
      }
    } else if (ring) {
      maplayer0.removeChild(ring);
    }
   
  }
  for (i=-2;i<128;i++){
    var angle = stepangle * i;
    var radial = document.getElementById("sectorradial"+i);

    var startdistance = 0;
    if(!(i%32)){
      startdistance = 20;
    } else if (!(i%16)){
      startdistance = 40;
    } else if (!(i%8)){
      startdistance = 80;
    } else if (!(i%4)){
      startdistance = 160;
    } else if (!(i%2)){
      startdistance = 260;
    } else {
      startdistance = 420;
    }
    if(startdistance < mindistance-(maxdistance-mindistance)){
      startdistance = mindistance-(maxdistance-mindistance);
    }
    if((angle >= minangle) && 
       (angle <= maxangle) && 
       (startdistance<maxdistance)){
      if(!radial){
        radial = document.createElementNS(svgns,'line');
        radial.setAttribute('stroke',"#280000");
        radial.setAttribute('id',"sectorradial"+i);
        radial.setAttribute('stroke-width',"3");
        maplayer0.appendChild(radial);
      }
      radial.setAttribute('x1', (1500-Math.cos(angle)*startdistance)*cz);
      radial.setAttribute('y1', (1500-Math.sin(angle)*startdistance)*cz);
      radial.setAttribute('x2', (1500-Math.cos(angle)*
                                 (maxdistance+(maxdistance-mindistance)))*cz);
      radial.setAttribute('y2', (1500-Math.sin(angle)*
                                 (maxdistance+(maxdistance-mindistance)))*cz);
    } else if (radial) {
      maplayer0.removeChild(radial);
    }
  }
}

function buildroute(r, container, color)
{
  // check to see if the route has been deleted
  if(!(r in routes)){
    return 0;
  }
  var cz = zoomlevels[zoomlevel];
  var route = document.getElementById("rt-"+r);
  if(!route){
    var circular = routes[r].c;
    var points = routes[r].p;
    var points2 = ""
    for (p in points){
      if (points[p].length == 3){
        points2 += (points[p][1]*cz)+","+(points[p][2]*cz)+" ";
      } else {
        points2 += (points[p][0]*cz)+","+(points[p][1]*cz)+" ";
      }
    }
    marker = document.getElementById("marker-"+color.substring(1));
    if(!marker){
      marker = buildmarker(color);
    }
    if(circular){
      route = document.createElementNS(svgns,'polygon');
    } else {
      route = document.createElementNS(svgns,'polyline');
      route.setAttribute('marker-end', 
                         'url(#marker-'+color.substring(1)+')');
    }
    route.setAttribute('fill','none');
    route.setAttribute('stroke', color);
    if('n' in routes[r]){
      route.setAttribute('stroke-width', .15*cz);
    } else {
      route.setAttribute('stroke-width', .1*cz);
    }
    route.setAttribute('id','rt-'+r);
    route.setAttribute('opacity','.15');
    route.setAttribute('points',points2);
    route.setAttribute('stroke-linecap', 'round');
    route.setAttribute('stroke-linejoin', 'round');
    route.setAttribute('onmouseover',
                        'routehoveron(evt,"'+r+'")');
    route.setAttribute('onmouseout',
                        'routehoveroff(evt,"'+r+'")');
    route.setAttribute('onclick',
                        'doroutemousedown(evt,"'+r+'")');
    container.appendChild(route);
  }
  return 1;
}
function buildnamedroutes()
{
  for (route in routes){
    r = routes[route]
    if ('n' in r){
      buildroute(route, maplayer1, '#ffffff');
    }
  }
}
function buildsectorfleets(sector,newsectorl1,newsectorl2)
{
  var fleetkey=0;
  var circle = 0;
  var group = 0;
  var sensegroup = 0;
  var sensecircle = 0;
  var marker = 0;
  var line = 0;
  var cz = zoomlevels[zoomlevel];
  for(fleetkey in sector.fleets){
    if(typeof fleetkey === 'string'){
      var fleet = sector.fleets[fleetkey];
      var playerowned;
      if ('ps' in fleet){
        playerowned=1;
      } else {
        playerowned=0;
      }
      group = document.createElementNS(svgns, 'g');
      group.setAttribute('fill', fleet.c);
      group.setAttribute('id', 'gf'+fleet.i);
      group.setAttribute('stroke', fleet.c);
      group.setAttribute('stroke-width', '.01');
      group.setAttribute('onmouseover',
                          'fleethoveron(evt,"'+fleet.i+'","'+fleet.sl+'")');
      group.setAttribute('onmouseout',
                          'fleethoveroff(evt,"'+fleet.i+'")');
      group.setAttribute('onclick',
                          'dofleetmousedown(evt,"'+fleet.i+'",'+playerowned+')');
      if ('r' in fleet){
        if(!buildroute(fleet.r, newsectorl1, fleet.c)){
          delete fleet.r;
        }
      } 
      if ('s' in fleet){
        sensegroup = document.getElementById("sg-"+fleet.o);
        if(!sensegroup){
          sensegroup = document.createElementNS(svgns,'g');
          sensegroup.setAttribute('fill',fleet.c);
          sensegroup.setAttribute('id','sg-'+fleet.o);
          sensegroup.setAttribute('opacity','.3');
          maplayer0.appendChild(sensegroup);
        }
        sensecircle = document.createElementNS(svgns, 'circle');
        sensecircle.setAttribute('cx', fleet.x*cz);
        sensecircle.setAttribute('cy', fleet.y*cz);
        sensecircle.setAttribute('r', fleet.s*cz);
        sensegroup.appendChild(sensecircle);
      }

      if ('x2' in fleet){
        
        marker = document.getElementById("marker-"+fleet.c.substring(1));
        if(!marker){
          marker = buildmarker(fleet.c);
        }
        line = document.createElementNS(svgns, 'line');

        line.setAttribute('marker-end', 'url(#marker-'+fleet.c.substring(1)+')');
        line.setAttribute('x1', fleet.x*cz);
        line.setAttribute('y1', fleet.y*cz);
        line.setAttribute('x2', fleet.x2*cz);
        line.setAttribute('y2', fleet.y2*cz);
        line.setAttribute('stroke',fleet.c);
        if(fleet.f&4){
          line.setAttribute('stroke-dasharray',(0.09*cz)+","+(0.09*cz));
          line.setAttribute('stroke-width', 0.02*cz);
        } else if(fleet.f&8) {
          line.setAttribute('stroke-dasharray',(0.3*cz)+","+(0.3*cz));
          line.setAttribute('stroke-width', 0.02*cz);
        } else if(fleet.f&16) {
          line.setAttribute('stroke-dasharray',(0.03*cz)+","+(0.09*cz));
          line.setAttribute('stroke-width', 0.03*cz);
        } else if(fleet.f&32) {
          line.setAttribute('stroke-width', 0.03*cz);
        } else {
          line.setAttribute('stroke-width', 0.02*cz);
        }


        group.appendChild(line);
      }
      if(fleet.f&2) {
        circle = document.createElementNS(svgns, 'circle');
        circle.setAttribute('cx', fleet.x*cz);
        circle.setAttribute('cy', fleet.y*cz);
        circle.setAttribute('r', 0.2*cz);
        circle.setAttribute('style','fill:url(#damagedfleet);');
        newsectorl1.appendChild(circle);
      } else if(fleet.f&1) {
        circle = document.createElementNS(svgns, 'circle');
        circle.setAttribute('cx', fleet.x*cz);
        circle.setAttribute('cy', fleet.y*cz);
        circle.setAttribute('r', 0.2*cz);
        circle.setAttribute('style','fill:url(#destroyedfleet);');
        newsectorl1.appendChild(circle);
      }
      circle = document.createElementNS(svgns, 'circle');
      circle.setAttribute('fill', fleet.c);
      circle.setAttribute('cx', fleet.x*cz);
      circle.setAttribute('cy', fleet.y*cz);
      circle.setAttribute('r', 0.04*cz);
      circle.setAttribute('or', 0.04*cz);
      circle.setAttribute('onmouseover','zoomcircle(evt,2.0);');
      circle.setAttribute('onmouseout','zoomcircle(evt,1.0);');
      circle.setAttribute('id', 'f'+fleet.i);
      group.appendChild(circle);
      newsectorl2.appendChild(group);
    }
  } 
}


function buildsectorconnections(sector,newsectorl1, newsectorl2)
{
  var i;
  var cz = zoomlevels[zoomlevel];
  for(i in sector.connections){
    if(typeof i === 'string'){
      var con = sector.connections[i];
      var x1 = con[0][0];
      var y1 = con[0][1];
      var x2 = con[1][0];
      var y2 = con[1][1];
      var angle = Math.atan2(y1-y2,x1-x2);
      var line = document.createElementNS(svgns, 'line');
      line.setAttribute('stroke-width', 0.5);
      line.setAttribute('stroke', '#aaaaaa');

      line.setAttribute('x1', (x1+(Math.cos(angle+3.14159)*0.3))*cz);
      line.setAttribute('y1', (y1+(Math.sin(angle+3.14159)*0.3))*cz);
      line.setAttribute('x2', (x2+(Math.cos(angle)*0.3))*cz);
      line.setAttribute('y2', (y2+(Math.sin(angle)*0.3))*cz);
      newsectorl1.appendChild(line);
    }
  }
}

function buildsectorplanets(sector,newsectorl1, newsectorl2)
{
  var planetkey = 0;
  var highlight = 0;
  var radius = 0;
  var sensegroup = 0;
  var circle = 0;
  var line = 0;
  var cz = zoomlevels[zoomlevel];
  for(planetkey in sector.planets){
    if(typeof planetkey === 'string'){
      var planet = sector.planets[planetkey];
       
      // draw You Are Here and it's arrow if it's a new player
      if (((newplayer === 1) && (planet.f&128))){
        youarehere.setAttribute('visibility','visible');
        youarehere.setAttribute('x',(planet.x-1.5)*cz);
        youarehere.setAttribute('y',(planet.y+1.3)*cz);
        line = document.createElementNS(svgns, 'line');
        line.setAttribute('stroke-width', '1.2');
        line.setAttribute('stroke', '#aaaaaa');
        line.setAttribute('marker-end', 'url(#endArrow)');
        line.setAttribute('x2', (planet.x-0.2)*cz);
        line.setAttribute('y2', (planet.y+0.3)*cz);
        line.setAttribute('x1', (planet.x-0.7)*cz);
        line.setAttribute('y1', (planet.y+1.0)*cz);
        newsectorl2.appendChild(line);
      }
    
      // sensor range
      if (('s' in planet)&&('o' in planet)){
        sensegroup = document.getElementById("sg-"+planet.o);
        if(!sensegroup){
          sensegroup = document.createElementNS(svgns,'g');
          sensegroup.setAttribute('id','sg-'+planet.o);
          sensegroup.setAttribute('fill',planet.h);
          sensegroup.setAttribute('opacity',0.2);
          maplayer0.appendChild(sensegroup);
        }
        circle = document.createElementNS(svgns, 'circle');
        circle.setAttribute('cx',  planet.x*cz);
        circle.setAttribute('cy',  planet.y*cz);
        circle.setAttribute('r',   planet.s*cz);
        sensegroup.appendChild(circle);
      }
      
      // food problem
      if((planet.f&1)||(planet.f&2)){
        highlight = document.createElementNS(svgns, 'circle');
        radius = 0.12;
        if(planet.f&64){
          radius += 0.05;
        }
        highlight.setAttribute('cx', planet.x*cz);
        highlight.setAttribute('cy', planet.y*cz);
        highlight.setAttribute('r', (planet.r+radius)*cz);
        if(planet.f&1){
          highlight.setAttribute('stroke', 'yellow');
        } else {
          highlight.setAttribute('stroke', 'red');
        }  
        highlight.setAttribute('fill', 'none');
        highlight.setAttribute('stroke-width', 0.035*cz);
        newsectorl1.appendChild(highlight);
      }
      

      // rgl govt.
      if (planet.f&4){
        highlight = document.createElementNS(svgns, 'circle');
        highlight.setAttribute('cx', planet.x*cz);
        highlight.setAttribute('cy', planet.y*cz);
        highlight.setAttribute('r', 5*cz);
        highlight.setAttribute('stroke', 'white');
        highlight.setAttribute('fill', 'none');
        highlight.setAttribute('stroke-width', 0.1*cz);
        highlight.setAttribute('stroke-opacity', 0.1);
        newsectorl1.appendChild(highlight);
      }

      // planetary defense
      if (planet.f&256){
        highlight = document.createElementNS(svgns, 'circle');
        highlight.setAttribute('cx', planet.x*cz);
        highlight.setAttribute('cy', planet.y*cz);
        highlight.setAttribute('r', 4*cz);
        highlight.setAttribute('stroke', 'yellow');
        highlight.setAttribute('fill', 'none');
        highlight.setAttribute('stroke-width', 0.02*cz);
        highlight.setAttribute('stroke-opacity', 0.5);
        highlight.setAttribute('stroke-dasharray',(0.3*cz)+","+(0.15*cz));
        newsectorl1.appendChild(highlight);
      }

      // military circle
      if ((planet.f&8)||(planet.f&16)||(planet.f&32)){
        highlight = document.createElementNS(svgns, 'circle');
        radius = 0.12;
        if(planet.f&64){ // capital
          radius += 0.05;
        }
        if((planet.f&1)||(planet.f&2)){ // food scarcity
          radius += 0.05;
        }
        highlight.setAttribute('cx', planet.x*cz);
        highlight.setAttribute('cy', planet.y*cz);
        highlight.setAttribute('r', (planet.r+radius)*cz);
        highlight.setAttribute('stroke', planet.h);
        highlight.setAttribute('fill', 'none');
        highlight.setAttribute('stroke-width', 0.025*cz);
        highlight.setAttribute('stroke-opacity', 0.4);
        highlight.setAttribute('stroke-dasharray',(0.03*cz)+","+(0.02*cz));
      
        if(planet.f&32){  
          highlight.setAttribute('stroke-width',0.050*cz);
        }
        if (planet.f&16) {
          highlight.setAttribute('stroke-dasharray',(0.15*cz)+","+(0.05*cz));
        } 
       

        newsectorl1.appendChild(highlight);
      }
        

      // capital ring
      if (planet.f&64){
        highlight = document.createElementNS(svgns, 'circle');
        highlight.setAttribute('cx', planet.x*cz);
        highlight.setAttribute('cy', planet.y*cz);
        highlight.setAttribute('r', (planet.r+0.12)*cz);
        highlight.setAttribute('stroke', planet.h);
        highlight.setAttribute('stroke-width', 0.02*cz);
        newsectorl1.appendChild(highlight);
      } 

      // inhabited ring
      if (planet.h !== 0){
        highlight = document.createElementNS(svgns, 'circle');
        highlight.setAttribute('cx', planet.x*cz);
        highlight.setAttribute('cy', planet.y*cz);
        highlight.setAttribute('r', (planet.r+0.06)*cz);
        highlight.setAttribute('stroke', planet.h);
        highlight.setAttribute('stroke-width', 0.04*cz);
        newsectorl2.appendChild(highlight);
      }
      circle = document.createElementNS(svgns, 'circle');
      circle.setAttribute("fill",planet.c);
      circle.setAttribute("stroke",'none');
      var playerowned=0;
      if ('pp' in planet){
        playerowned=1;
      } else {
        playerowned=0;
      }
      circle.setAttribute('id', planet.i);
      circle.setAttribute('cx', planet.x*cz);
      circle.setAttribute('cy', planet.y*cz);
      circle.setAttribute('r', planet.r*cz);
      circle.setAttribute('or', planet.r*cz);
      circle.setAttribute('fill', planet.c);
      circle.setAttribute('onmouseover',
                          'planethoveron(evt,"'+planet.i+'","'+planet.n+'")');
      circle.setAttribute('onmouseout',
                          'planethoveroff(evt,"'+planet.i+'")');
      circle.setAttribute('onclick',
                          'doplanetmousedown(evt,"'+planet.i+'",'+playerowned+')');
      newsectorl2.appendChild(circle);
    }
  }
}
    
function adjustview(viewable)
{
  var key;
  
  buildnamedroutes();

  for (key in viewable){
    if( typeof key === 'string'){
      var sectoridl1 = "sectorl1-"+key;
      var sectoridl2 = "sectorl2-"+key;
      if (((key in sectorsstatus)&&(sectorsstatus[key]==='-'))&&(key in sectors)){
        sectorsstatus[key] = "+";
        var newsectorl1 = document.createElementNS(svgns, 'g');
        var newsectorl2 = document.createElementNS(svgns, 'g');

        newsectorl2.setAttribute('id', sectoridl2);
        newsectorl2.setAttribute('class', 'mapgroupx');
        
        newsectorl1.setAttribute('id', sectoridl1);
        newsectorl1.setAttribute('class', 'mapgroupx');
        
        var sector = sectors[key];
        if('fleets' in sector){
          buildsectorfleets(sector,newsectorl1,newsectorl2);
        }
        if('planets' in sector){
          buildsectorplanets(sector,newsectorl1, newsectorl2);
        }
        if('connections' in sector){
          buildsectorconnections(sector,newsectorl1,newsectorl2);
        }

        maplayer1.appendChild(newsectorl1);
        maplayer2.appendChild(newsectorl2);
      }
    }
  }
}

function resetmap(reload)
{
  var key = 0;
  while(maplayer0.hasChildNodes()){
    maplayer0.removeChild(maplayer0.firstChild);
  }

  while(maplayer1.hasChildNodes()){
    maplayer1.removeChild(maplayer1.firstChild);}
  
  while(maplayer2.hasChildNodes()){
    maplayer2.removeChild(maplayer2.firstChild);
  }

  for (key in sectorsstatus){
    if(sectorsstatus[key] === '+'){
      sectorsstatus[key] = '-';
    }
  }
  if(reload){
    sectorsstatus = [];
  }
  var viewable = viewablesectors(getviewbox(map));
  adjustview(viewable);
  buildsectorrings();
  getsectors(viewable,0);
}

function loadnewsectors(response)
{
  //hidestatusmsg("loadnewsectors");
  var sector = 0;
  var key = 0;
  var viewable = viewablesectors(getviewbox(map));
  var deletesectors = [];
 
  if ('routes' in response) {
    for (route in response.routes) {
      routes[route]  = response.routes[route];
      routes[route].p = eval(routes[route].p);
    }
  }
  if ('sectors' in response) {
    for (sector in response.sectors){
      if (typeof sector === 'string' && sector != "routes"){
          
        if ((sector in sectorsstatus) && 
           (sectorsstatus[sector] === '+')){
          deletesectors[sector] = 1;
        }
        sectors[sector] = response.sectors[sector];
        sectorsstatus[sector] = '-';
      }
    }
  }


  // first, remove out of view sectors...
  for (key in sectorsstatus){
    if(typeof key === 'string'){
      if ((!(key in viewable))&&(sectorsstatus[key]==='+')){
        deletesectors[key] = 1;
      }
    }
  }
  for (key in deletesectors){
    if(typeof key === 'string'){
      sectorsstatus[key] = '-';
      var remsector;
      
      remsector = document.getElementById('sectorl1-'+key);
      if(remsector){
        maplayer1.removeChild(remsector);
      }

      remsector = document.getElementById('sectorl2-'+key);
      if(remsector){
        maplayer2.removeChild(remsector);
      }
    }
  }
  adjustview(viewable);
}

function setxy(evt)
{
  mousepos.x = evt.clientX;
  mousepos.y = evt.clientY;
  var curloc = screentogamecoords(evt);
  mousepos.mapx = curloc.x;
  mousepos.mapy = curloc.y;
}

function movemenu(x,y)
{
  $("#menu").css('top',y);
  $("#menu").css('left',x);
}

function buildform(subform)
{
  var submission = {};
  var formfield = 0;
  var formbutton = 0;
  var textarea = 0;
  var i;
  for(i in subform.getElementsByTagName('select')){
    if(typeof i === 'string'){
      formfield = subform.getElementsByTagName('select')[i];
      if((formfield.name)&&(formfield.type === 'select-one')){
        submission[formfield.name] = formfield.options[formfield.selectedIndex].value;
      }
    }
  }
  for(i in subform.getElementsByTagName('button')){
    if(typeof i === 'string'){
      formbutton = subform.getElementsByTagName('button')[i];
      if(formbutton.id){
        submission[formbutton.id] = 1;
      }
    }
  }
  for(i in subform.getElementsByTagName('textarea')){
    if(typeof i === 'string'){
      textarea = subform.getElementsByTagName('textarea')[i];
      if((textarea.name)&&(textarea.value)){
        submission[textarea.name] = textarea.value;
      }
    }
  }
  for(i in subform.getElementsByTagName('input')){
    if(typeof i === 'string'){
      formfield = subform.getElementsByTagName('input')[i];
      if((formfield.name)&&(formfield.value)){
        if(formfield.type==="radio"){
          if(formfield.checked){
            submission[formfield.name] = formfield.value;
          }
        } else if(formfield.type==="checkbox"){
          if(formfield.checked){
            submission[formfield.name] = formfield.value;
          }
        } else {
          submission[formfield.name] = formfield.value;
        }
      }
    }
  }
  return submission;
}



function changebuildlist(planetid, shiptype, change)
{
  var columns = [];
  var column = 0;
  var tid = "#buildfleettable-"+planetid+" ";
  var tbl = $("#buildfleettable-"+planetid);
  var rowtotal = $(tid+'#num-'+shiptype).val();
  var hidebuttons = false;
  
  if (rowtotal === ""){
    rowtotal = 0;
  } else {
    rowtotal = parseInt(rowtotal,10);
  }
  
  rowtotal += change;
  if (rowtotal < 0){
    rowtotal = 0;
  }

  // set the new number of ships to build
  if(change !== 0){
    $(tid+'#num-'+shiptype).val(rowtotal);
  }
  $(tid+"th[id ^= 'col-']").each(function() {
    // get column headers 
    columns.push($(this).attr('id').split('-')[1]);
    });
    
  for(column in columns){
    if(typeof column === 'string'){
      var colname = columns[column];
      var qry = 'required-' + colname;
      var coltotal = 0;
      //$(tid+"td[id ^= '" +qry+ "']").each(function() {
      $(tbl).find("td[id ^= '" +qry+ "']").each(function() {
        var curshiptype = $(this).attr('id').split('-')[2];
        var curnumships = parseInt($(tbl).find('#num-'+curshiptype).val(),10);
        if(isNaN(curnumships)){
          curnumships = 0;
        }
        coltotal += (parseInt($(this).html(),10) * curnumships);
      });
      var available = parseInt($(tbl).find("#available-"+colname).html(), 10);
      coltotal = available-coltotal;
      $(tbl).find("#total-"+colname).html(coltotal);
      if(coltotal < 0){
        $(tbl).find("#total-"+colname).css('color','red');
        hidebuttons=true;
      } else {
        $(tbl).find("#total-"+colname).css('color','white');
      }
    }
  }

  // add up ship totals
  var totalships = 0;
  $(tbl).find("input[id ^= 'num-']").each(function() {
    var numships = parseInt($(this).val(),10);
    if(!isNaN(numships)){
      totalships += numships;
    }
  });

  if(totalships===0){
    hidebuttons = true;
  }

  if(!hidebuttons){
    $(tbl).find("#submit-build-"+planetid).show();
    $(tbl).find("#submit-build-another-"+planetid).show();
  } else {
    $(tbl).find("#submit-build-"+planetid).hide();
    $(tbl).find("#submit-build-another-"+planetid).hide();
  }

  $(tbl).find("#total-ships").html(totalships);
}

function removetooltips()
{
  while(tips.length){
    var id = tips.pop();
    $(id).btOff();
  }
} 
function settooltip(id,tip)
{
  tips.push(id);
  $(id).bt(tip, {fill:"#886600", width: 300, 
           strokeWidth: 2, strokeStyle: 'white', 
           cornerRadius: 10, spikeGirth:20, 
           cssStyles:{color: 'white'}});
}
function loadtooltip(id,url,tipwidth,trigger)  
{ 
  tips.push(id);
  $(id).bt({
    ajaxPath:url,
    fill:"#006655", width: tipwidth,
    trigger:[trigger,trigger],
    strokeWidth: 2, strokeStyle: 'white',
    cornerRadius: 10, spikeGirth: 20});
}

    

function prevdef(event) {
  event.preventDefault();
}
function stopprop(event) {
  event.stopPropagation();
}


function zoomcircleid(factor,id)
{
  var circle = document.getElementById(id);
  if(circle){
    var radius = circle.getAttribute("or");
    radius *= factor;
    circle.setAttribute("r", radius);
    if(id[0]==='f'){
      if(factor>1.0){
        var sf = document.getElementById('selectedfleet');
        sf.appendChild(circle);
      } else {
        var fg = document.getElementById('g'+id);
        fg.appendChild(circle);
      }
    }
  }
}

function zoomcircle(evt,factor)
{
  var p = evt.target;
  var radius = p.getAttribute("or");
  radius *= factor;
  p.setAttribute("r", radius);
}



function screentogamecoords(evt)
{
  var vb = getviewbox(map);
  var curloc = getcurxy(evt);
  var cz = zoomlevels[zoomlevel];
  curloc.x = curloc.x/cz + vb[0]/cz;
  curloc.y = curloc.y/cz + vb[1]/cz;
  return curloc;
}

function ontonamedroute(fleetid, routeid)
{
  submission = {};
  submission.route = routeid;
  sendrequest(handleserverresponse,
              '/fleets/'+fleetid+'/onto/',
              'POST', submission);
}

function RouteBuilder()
{
  var goto;
  var types = {'directto':1, 'routeto':2, 'circleroute':3, 'off': 4};
  var route = [];
  var named = false;

  var directto       = document.getElementById('directto');
  var routeto        = document.getElementById('routeto');
  var circleroute  = document.getElementById('circleroute');
  var type;
  var curfleet;
  
  this.type = types.off;
  this.curfleet = 0;
  this.cancel = function()
  {
    this.type = types.off;
    this.route = [];
    this.named = false;
    circleroute.setAttribute('visibility','hidden');
    routeto.setAttribute('visibility','hidden');
    directto.setAttribute('visibility','hidden');
    this.curfleet = 0;
  }

  this.startcommon = function(fleetid)
  {
    if(fleetid){
      this.curfleet = fleetid;
    } else {
      this.curfleet = 0;
    }
    killmenu();
    transienttabs.temphidetabs();
    permanenttabs.temphidetabs();
    if(buildanother === 1){
      // we are in fleet builder, but
      // user doesn't want to build another fleet...
      transienttabs.removetab('buildfleet'+currentbuildplanet);
      buildanother=0;
    } else if (buildanother === 2){
      transienttabs.hidetabs();
    }
  }
  this.startnamedroute = function(planetid, initialx, initialy, circular)
  {
    if(initialx == 0 && initialy == 0) {
      // not provided, so use the last 'clicked on' x/y
      initialx = mousepos.mapx;
      initialy = mousepos.mapy;
      planetid = undefined;
    }

    this.named = true;
    this.startrouteto(undefined, initialx, initialy, circular, planetid);
  }

  this.startrouteto = function (fleetid, initialx, initialy, circular, planetid)
  {
    this.startcommon(fleetid);
    this.route = [];
    if(planetid){
      this.route[0] = planetid;
    } else {
      this.route[0] = initialx+"/"+initialy;
    }
    var cz = zoomlevels[zoomlevel];
    var coords = (initialx*cz)+","+(initialy*cz)+" "+
                 (initialx*cz)+","+(initialy*cz);
    if(circular){
      this.type = types.circleroute;
      circleroute.setAttribute('visibility','visible');
      circleroute.setAttribute('points',coords);
    } else{
      this.type = types.routeto;
      routeto.setAttribute('visibility','visible');
      routeto.setAttribute('points',coords);
    }
    setstatusmsg('Click in Space for Waypoint, click on Planet to stop at planet, press \'Enter\' to finish');
  }

  this.startdirectto = function (fleetid,initialx,initialy)
  {
    this.startcommon(fleetid);
    this.type = types.directto;
    var cz = zoomlevels[zoomlevel];
    $('#fleets').hide('fast'); 
    directto.setAttribute('visibility','visible');
    directto.setAttribute('x1',initialx*cz);
    directto.setAttribute('y1',initialy*cz);
    directto.setAttribute('x2',initialx*cz);
    directto.setAttribute('y2',initialy*cz);
  }

  this.active = function()
  {
    if(this.type === types.off){
      return 0;
    } else {
      return 1;
    }
  }
  this.addleg = function(evt,planet,x,y)
  {
    if(this.type === types.off){
      return;
    } else if(this.type === types.directto){
      this.finish(evt,planet); 
    } else {
      var curpointstr = ""
      if (this.type === types.routeto) {
        curpointstr = routeto.getAttribute('points');
      } else {
        curpointstr = circleroute.getAttribute('points');
      }
      var points = curpointstr.split(' ');
      var len = points.length;
      if (curpointstr.indexOf(',') === -1) {
        points.push(points[len-2]);
        points.push(points[len-1]);
      } else {
        // use the planet's coordinates if we have them.
        if(planet && x && y){
          points[len-1] = x+","+y;
        }
        points.push(points[len-1]);
      }
      curpointstr = points.join(' ');
      if(this.type === types.routeto){
        routeto.setAttribute('points', curpointstr);
      } else {
        circleroute.setAttribute('points', curpointstr);
      }
      if(planet){
        this.route.push(planet);
      } else {
        curloc = screentogamecoords(evt);
        this.route.push(curloc.x+"/"+curloc.y);
      } 
    }

  }

  this.finish = function(evt,planet)
  {
    curloc = screentogamecoords(evt);
    if(buildanother===2){
      transienttabs.displaytab('buildfleet'+currentbuildplanet);
    }
    directto.setAttribute('visibility','hidden');
    circleroute.setAttribute('visibility','hidden');
    routeto.setAttribute('visibility','hidden');

    transienttabs.tempshowtabs();
    permanenttabs.tempshowtabs();
    
    var request = "";
    var submission = {}
    if(this.type === types.directto){
      if(planet){
        request = "/fleets/"+this.curfleet+"/movetoplanet/";
        submission.planet=planet;
      } else {
        request = "/fleets/"+this.curfleet+"/movetoloc/";
        submission.x = curloc.x;
        submission.y = curloc.y;
      }

    } else {
      request = "/fleets/"+this.curfleet+"/routeto/";
      submission.route = this.route.join(',');
      if (this.type === types.routeto){
        submission.circular = 'false';
      } else {
        submission.circular = 'true';
      }
      this.route = [];
    }
    if(buildanother===2){
      transienttabs.displaytab('buildfleet'+currentbuildplanet);
      submission.buildanotherfleet = currentbuildplanet;
    }
    if(this.named){
      // args: title, headline, submitfunction, cancelfunction, submit, cancel
      args = {'title': 'Named Route',
              'headline': 'Route Name:',
              'maxlen': 20,
              'text': '',
              'submitfunction': function(stuff,string) 
                { 
                  request = "/routes/named/add/";
                  submission.name = string;
                  sendrequest(handleserverresponse,request,'POST',submission);
                }, 
              'cancelfunction': function(){},
              'submit': 'Build Route',
              'cancel': 'Cancel'}
      stringprompt(args);
      this.named = false;
    } else {
      sendrequest(handleserverresponse,request,'POST',submission);
    }
    this.curfleet=0;
    this.type = types.off;
  }
  
  this.update = function (evt,viewbox){
    if (this.type === types.off){
      return;
    }
    var newcenter = getcurxy(evt);
    if(this.type === types.directto){
      directto.setAttribute('x2',newcenter.x+viewbox[0]);
      directto.setAttribute('y2',newcenter.y+viewbox[1]);
    } else {
      var curpointstr = "";
      if (this.type === types.routeto) {
        curpointstr = routeto.getAttribute('points');
      } else {
        curpointstr = circleroute.getAttribute('points');
      }
      var points = curpointstr.split(' ');
      var len = points.length;
      // some browsers give us commas, some don't
      if (curpointstr.indexOf(',') === -1) {
        points[len-2] = (newcenter.x+viewbox[0]);
        points[len-1] = (newcenter.y+viewbox[1]);
      } else {
        points[len-1] = (newcenter.x+viewbox[0])+","+(newcenter.y+viewbox[1]);
      }
      curpointstr = points.join(' ');
      if (this.type === types.routeto) {
        routeto.setAttribute('points', curpointstr);
      } else {
        circleroute.setAttribute('points', curpointstr);
      }

    }
  }
}

function handlekeydown(evt)
{
  if (evt.keyCode == 13){         // enter
    if(routebuilder.active()){
      routebuilder.finish(evt);
      return false;
    }
  } else if (evt.keyCode == 27) { // escape
    if(routebuilder.active()){
      routebuilder.cancel();
      return false;
    }
  } else if ((evt.keyCode === 107)||(evt.keyCode === 187)) {    // +/=  (zoom in)
    //var viewbox = getviewbox(map);
    //var cxy = new Point(viewbox[0]+(viewbox[2]/2.0), 
    //                    viewbox[1]+(viewbox[3]/2.0));
    //zoom(evt,"+",cxy);
  } else if ((evt.keyCode === 109)||(evt.keyCode === 95)) {    // -/_  (zoom out)
    //var viewbox = getviewbox(map);
    //var cxy = new Point(viewbox[0]+(viewbox[2]/2.0), 
    //                    viewbox[1]+(viewbox[3]/2.0));
    //zoom(evt,"-",cxy);
  }

}


function planethoveron(evt,planet,name)
{
  name = "<h1>"+name+"</h1>";
  if(routebuilder.active()){
    setstatusmsg(name+
                 "<div style='padding-left:10px; font-size:10px;'>"+
                 "Left Click to Send Fleet to Planet"+
                 "</div>");
  } else {
    setstatusmsg(name+
                 "<div style='padding-left:10px; font-size:10px;'>"+
                 "Left Click to Manage Planet" +
                 "</div>");
  }
  document.body.style.cursor='pointer';
  setxy(evt);
  zoomcircle(evt,2.0);
  curplanetid = planet;
}

function planethoveroff(evt,planet)
{
  hidestatusmsg("planethoveroff");
  document.body.style.cursor='default';
  setxy(evt);
  zoomcircle(evt,1.0);
  curplanetid = 0;
}

function routehoveron(evt,r)
{
  if((!routebuilder.active()) || (routebuilder.type == 1)){
    if('n' in routes[r]){
      name = routes[r].n;
    } else {
      name = "Unnamed Route ("+r+")";
    }
    
    if(routebuilder.active()){
      setstatusmsg(name+
                   "<div style='padding-left:10px; font-size:10px;'>"+
                   "Left Click to Put Fleet on Route"+
                   "</div>");
    } else {
      setstatusmsg(name+
                   "<div style='padding-left:10px; font-size:10px;'>"+
                   "Left Click for Route Menu"+
                   "</div>");
    }
    document.body.style.cursor='pointer';
    evt.target.setAttribute('opacity','.25');
    setxy(evt);
    currouteid = r;
  }
}

function routehoveroff(evt,route)
{
  if((!routebuilder.active()) || (routebuilder.type == 1)){
    hidestatusmsg("routehoveroff");
    evt.target.setAttribute('opacity','.15');
    document.body.style.cursor='default';
    setxy(evt);
    currouteid = 0;
  }
}

function doroutemousedown(evt,route)
{
  setxy(evt);
  movemenu(mousepos.x+10,mousepos.y+10); 
  if((routebuilder.curfleet)&&(routebuilder.active())&&
     (routebuilder.type == 1 /* directo */)){
    ontonamedroute(routebuilder.curfleet, route);
    routebuilder.cancel();
  } else if (!routebuilder.active()) {
    handlemenuitemreq(evt, '/routes/'+route+'/root/');
  }
}

function fleethoveron(evt,fleet,about)
{
  curfleetid = fleet;
  about = "<h1>"+about+"</h1>";
  setstatusmsg(about+"<div style='padding-left:10px; font-size:10px;'>Left Click to Manage Fleet</div>");
  document.body.style.cursor='pointer';
  setxy(evt);
}

function fleethoveroff(evt,fleet)
{
  curfleetid = 0;
  hidestatusmsg("fleethoveroff");
  document.body.style.cursor='default';
  setxy(evt);
}

function buildmenu()
{
  $('#menu').attr('style','position:absolute; top:'+(mousepos.y+10)+
                       'px; left:'+(mousepos.x+10)+ 'px;');
  $('#menu').show();
}


function handleserverresponse(response)
{
  var id,title,content;
  if ('menu' in response){
    $('#menu').html(response.pagedata);
    $('#menu').show();
  }

  if('transient' in response){
    id = response.id;
    title = response.title;
    content = response.pagedata;
    $('#menu').hide();
    transienttabs.pushtab(id, title, 'hi there1',false);
    transienttabs.settabcontent(id, content);
    transienttabs.displaytab(id);
  }

  if('permanent' in response){
    id = response.id;
    title = response.title;
    content = response.pagedata;
    $('#menu').hide();
    permanenttabs.settabcontent(id, content);
  }

  if ('showcountdown' in response){
    if (response.showcountdown === true){
      $('#countdown').show();
    } else {
      $('#countdown').hide();
    }
  }

  if ('killmenu' in response){
    $('#menu').hide();
  }

  if ('killtab' in response){
    transienttabs.removetab(response.killtab);
  }

  if ('reloadfleets' in response){
    reloadtab('#fleetview');
  }
  if ('reloadplanets' in response){
    reloadtab('#planetview');
  }
  if ('reloadmessages' in response){
    sendrequest(handleserverresponse,
                '/messages/','GET');
  }
  if ('reloadneighbors' in response){
  permanenttabs.gettaburl('neighborslist', '/politics/neighbors/');
    permanenttabs.reloadtab('neighborslist');
  }

  if ('killwindow' in response){
    $('#window').hide();
  }
  if ('status' in response){
    setstatusmsg(response.status);
  } else {
    hidestatusmsg("loadnewmenu");
  }
  if ('rubberband' in response){
    routebuilder.startdirectto(response.rubberband[0],
                               response.rubberband[1],
                               response.rubberband[2]);
  }
  if ('resetmap' in response){
    sectors = [];
    resetmap(true);
  }
  if ('slider' in response){
    $(curslider).html(response.slider);
  }
  if ('sectors' in response){
    loadnewsectors(response.sectors);
  }
  if ('deleteroute' in response){
    var route = document.getElementById("rt-"+response.deleteroute);
    if(route){
      route.parentNode.removeChild(route);
      delete routes[response.deleteroute];
      killmenu();
    }

  }
    
}


function getsectors(newsectors,force,getnamedroutes)
{
  var submission = {};
  var doit = 0;
  var sector = 0;
  sectorgeneration++;
  // convert newsectors (which comes in as a straight array)
  // over to the loaded sectors array (which is associative...)
  // and see if we have already asked for that sector (or indeed
  // already have it in memory, doesn't really matter...)
  for (sector in newsectors){
    if((force===1)||(!(sector in sectorsstatus))){
      sectorsstatus[sector] = sectorgeneration;
      submission[sector]=1;
      doit = 1;
    }
  }
  if(getnamedroutes){
    submission.getnamedroutes="yes";
  }
  if(doit===1){
    sendrequest(handleserverresponse,"/sectors/",'POST',submission);
    setstatusmsg("Requesting Sectors");
  }
}


function loadtab(tab,urlstring, container, postdata) 
{
  var method = 'GET';
  $(container+'-tabs '+'a.current').toggleClass('current');
  $(container+'-tabs '+tab).addClass('current');

  if(postdata !== undefined){
    method = 'POST';
  } else {
    postdata = {};
  }
  if (urlstring.length > 0){
    $(container).attr('currenturl',urlstring);
    $.ajax( 
    { 
      type: method,
      data: postdata,
      error: handleerror,
      dataType: 'json',
      url: urlstring, 
      cache: false, 
      success: function(message) 
      { 
        $(container).empty().append(message.tab); 
        handleserverresponse(message);
      } 
    }); 
  } 
} 


function reloadtab(container)
{
  if($(container).length > 0){
    var url = $(container).attr('currenturl');
    var tab = $(container+'-tabs a.current').attr('id');
    loadtab(tab,url,container);
  }
}

function starthelp()
{
  transienttabs.pushtab('helptab','Help','',false);
                         transienttabs.closehandler('helptab',function(){helpstack = [];});
                         transienttabs.gettaburl('helptab','/help/');
                         transienttabs.displaytab('helptab');
                         $('#slidermenu').hide();
}


function newmenu(request, method, postdata)
{
  sendrequest(handleserverresponse,request,method,postdata);
}

function newslider(request, slider)
{
  killmenu();
  sendrequest(handleserverresponse, request,'GET','');
  curslider = slider;
}


function sendform(subform,request)
{
  var submission = buildform(subform);
  sendrequest(handleserverresponse,request,'POST',submission);
  $('#window').hide();
  setmenuwaiting();
}

function submitbuildfleet(planetid, mode)
{
  buildanother=mode;
  sendform($('#buildfleetform-'+planetid)[0],
           '/planets/'+planetid+'/buildfleet/');
  transienttabs.settabcontent('buildfleet'+planetid, '');
}


function handlebutton(id,container,tabid,title,url,reloadurl){
  if(transienttabs.alreadyopen(id)){
    var cururl = $('#'+id).attr('currenturl');
    if (cururl === reloadurl) {
      transienttabs.removetab(container);
    } else {
      loadtab('#'+tabid,url,'#'+id);
    }
  } else {
    sendrequest(handleserverresponse,url, "GET");
  } 
}

    
function handlemenuitemreq(event, url)
{
  prevdef(event);
  setmenuwaiting();
  sendrequest(handleserverresponse,url, "GET");
}


function dofleetmousedown(evt,fleet,playerowned)
{
  setxy(evt);
  if(routebuilder.active()){
    routebuilder.addleg(evt);
  } else if(!routebuilder.curfleet){
    buildmenu();
    if(playerowned===1){
      handlemenuitemreq(evt, '/fleets/'+fleet+'/root');
    } else {
      handlemenuitemreq(evt, '/fleets/'+fleet+'/info');
    }
  } else {
    // this should probably be changed to fleets/1/intercept
    // with all the appropriate logic, etc...
    var curloc = getcurxy(evt);
    //curfleetid=0;
  }
}


function doplanetmousedown(evt,planet,playerowned)
{
  setxy(evt);
  
  if(routebuilder.active()){
    var cz = zoomlevels[zoomlevel];
    
    var svgplanet = document.getElementById(planet);
    var x  = svgplanet.getAttribute('cx');
    var y  = svgplanet.getAttribute('cy');
    routebuilder.addleg(evt,planet,x,y);
    stopprop(evt);
  } else {
    buildmenu();    
    handlemenuitemreq(evt, '/planets/'+planet+'/root/');
  } 
}


function zoom(evt, magnification, screenloc)
{
  var i=0;
  var zid=0;
  if(evt.preventDefault){
    evt.preventDefault();
  }
  var changezoom = 0;
  var oldzoom = zoomlevels[zoomlevel];
  if((magnification === "+")&&(zoomlevel<6)){
    changezoom = 1;
    zoomlevel++;
  } else if((magnification === "-")&&(zoomlevel>0)){
    changezoom = 1;
    zoomlevel--;
  }
  if(changezoom){
    // manipulate the zoom dots in the UI
    for(i=1;i<=zoomlevel;i++){
      zid = "#zoom"+i;
      $(zid).attr('src','/site_media/blackdot.png');
    }
    for(i=zoomlevel+1;i<7;i++){
      zid = "#zoom"+i;
      $(zid).attr('src','/site_media/whitedot.png');
    }


    var viewbox = getviewbox(map);
    var newzoom = zoomlevels[zoomlevel];
    var newviewbox = [];
    // screenloc is in screen coordinates
    // newcenter is in world coordinates
    var newcenter = new Point((viewbox[0]+screenloc.x)/oldzoom*newzoom,
                              (viewbox[1]+screenloc.y)/oldzoom*newzoom);
    
    newviewbox[0] = newcenter.x-(curwidth/2.0);
    newviewbox[1] = newcenter.y-(curheight/2.0);
    newviewbox[2] = curwidth;
    newviewbox[3] = curheight;
    map.setAttribute("viewBox",newviewbox.join(" "));

    resetmap(false);
  }
}

function init(timeleftinturn,cx,cy)
{
  map = document.getElementById('map');
  maplayer0 = document.getElementById('maplayer0');
  maplayer1 = document.getElementById('maplayer1');
  maplayer2 = document.getElementById('maplayer2');
  svgmarkers = document.getElementById('svgmarkers');
  sectorlines = document.getElementById('sectorlines');
  youarehere = document.getElementById('youarehere');
  curcenter = new Point(cx*zoomlevels[zoomlevel], cy*zoomlevels[zoomlevel]); 
  mousepos = new Point(cx*zoomlevels[zoomlevel], cy*zoomlevels[zoomlevel]); 

  transienttabs = new SliderContainer('transientcontainer', 'right', 50);
  permanenttabs = new SliderContainer('permanentcontainer', 'left', 50);
  routebuilder  = new RouteBuilder();

  permanenttabs.pushtab('neighborslist', 'Neighbors', '', true);
  permanenttabs.pushtab('planetslist', 'Planets', '', true);
  permanenttabs.pushtab('fleetslist', 'Fleets', '', true);
  
  permanenttabs.gettaburl('neighborslist', '/politics/neighbors/');
  permanenttabs.gettaburl('planetslist', '/planets/');
  permanenttabs.gettaburl('fleetslist', '/fleets/');
 
  //transienttabs.removetab('tab2');
  curwidth = $(window).width()-6;
  // apparantly chrome sometimes misreports window height...
  ($(window).height()-8 > $(document).height()-8) ? 
    curheight = $(window).height()-8 : 
    curheight = $(document).height()-8; 

  var vb = [curcenter.x-(curwidth/2.0),
            curcenter.y-(curheight/2.0),
            curwidth, curheight];
  setviewbox(vb);

  movemenu(curwidth/8.0,curheight/4.0);
  

  originalview = getviewbox(map);
  map.setAttribute("viewBox", originalview.join(" "));
  
  buildsectorrings();
  var dosectors = viewablesectors(originalview);
  getsectors(dosectors,0,true);
 
  $(document).keydown(handlekeydown);

  $('#mapdiv').mousedown(function(evt) { 
    setxy(evt);
    if(evt.preventDefault){
      evt.preventDefault();
    }
    removetooltips();
    $('div.slideoutcontents').hide('fast');
    //$('div.slideoutcontentscontents').empty();
    document.body.style.cursor='move';
    mousedown = true;
    mouseorigin = getcurxy(evt);
  }); 

  $('#mapdiv').mousemove(function(evt) { 
    var viewbox = getviewbox(map);
    if(evt.preventDefault){
      evt.preventDefault();
    }             

    if(mousedown === true){
      mousecounter++;
      if(mousecounter%3 === 0){
        killmenu();
        permanenttabs.temphidetabs();
        transienttabs.temphidetabs();
        var neworigin = getcurxy(evt);
        var dx = (mouseorigin.x - neworigin.x);
        var dy = (mouseorigin.y - neworigin.y);
        viewbox[0] = viewbox[0] + dx;
        viewbox[1] = viewbox[1] + dy;
        setviewbox(viewbox);
        mouseorigin = neworigin;
      }
    }
    routebuilder.update(evt,viewbox);
  });
  $('#mapdiv').mouseup(function(evt) { 
    setxy(evt);
    if(evt.preventDefault){
      evt.preventDefault();
    }
    if(evt.detail===2){
      var cxy = getcurxy(evt);
      zoom(evt,"-",cxy);
      killmenu();
    } else if ((!routebuilder.active())&&
               (!currouteid)&&(!curplanetid)&&(!curfleetid)&&
               (!transienttabs.isopen())&&
               (!permanenttabs.isopen())&&
               ($('#menu').css('display') == 'none')&&
               (mousecounter < 3)){
      buildmenu();    
      handlemenuitemreq(evt, '/map/root/');
    } else if((!routebuilder.active())&&
               (!currouteid)&&(!curplanetid)&&(!curfleetid)&&
               ($('#menu').css('display') == 'none')&&
               (mousecounter < 3)){
      permanenttabs.hidetabs();
      transienttabs.hidetabs();
    } else if($('#menu').css('display') != 'none'){
      killmenu();
    }

    document.body.style.cursor='default';
    mousedown = false;
    if((!currouteid)&&(!curplanetid)&&(routebuilder.active())){
      routebuilder.addleg(evt);
    }
    if(mousecounter){
      if(mousecounter > 1){
        transienttabs.tempshowtabs();
        permanenttabs.tempshowtabs();
      }
      mousecounter=0;
    } else {
      transienttabs.tempcleartabs();
      permanenttabs.tempcleartabs();
    }
    buildsectorrings();
    var dosectors = viewablesectors(getviewbox(map));
    getsectors(dosectors,0);
    adjustview(dosectors);
  
  });

function resizewindow() { 
  var newwidth = $(window).width();
  var newheight = $(window).height();
  if(newwidth !== 0){
    curwidth = newwidth-6;
  }
  if(newheight !== 0){
    curheight = newheight-8;
  }
  var viewbox = getviewbox(map);
  viewbox[2]=curwidth;
  viewbox[3]=curheight;
  setviewbox(viewbox);
}

  $(window).bind('resize', function() {
    if (resizeTimer) {
      clearTimeout(resizeTimer);
    }
    resizeTimer = setTimeout(resizewindow, 100);
  });
	$('#countdown').countdown({
    description:'Turn Ends', 
    until: timeleftinturn, format: 'hms',
    onExpiry: function () {
      $('#countdown').unbind();
      $('#countdown').remove();
      $('#countdown2').show();
      $('#countdown2').countdown({
        description:'Reload Wait',
        until: "+"+(600+Math.floor(Math.random()*600)), format: 'hms',
        expiryUrl: "/view/"
      });
    }
  });
  
}

function centermap(x,y)
{
  var vb = getviewbox(map);
  x *= zoomlevels[zoomlevel];
  y *= zoomlevels[zoomlevel];

  vb[0] = x-(vb[2]/2.0);
  vb[1] = y-(vb[3]/2.0);
  setviewbox(vb);

  resetmap(false);
}

function zoommiddle(evt, magnification)
{
  var p = new Point(curwidth/2.0,curheight/2.0);
  zoom(evt,magnification,p);
}
function expandtoggle(id)
{
  if($(id).attr('src') === '/site_media/expandup.png'){
    $(id).attr('src', '/site_media/expanddown.png');
  } else {
    $(id).attr('src', '/site_media/expandup.png');
  }
}




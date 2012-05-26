/*

Copyright (c) 1012 David Case

Permission is hereby granted, free of charge, to any person 
obtaining a copy of this software and associated documentation 
files (the "Software"), to deal in the Software without 
restriction, including without limitation the rights to use, 
copy, modify, merge, publish, distribute, sublicense, and/or 
sell copies of the Software, and to permit persons to whom the 
Software is furnished to do so, subject to the following 
conditions:

The above copyright notice and this permission notice shall be 
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY 
KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE 
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE 
USE OR OTHER DEALINGS IN THE SOFTWARE.

*/


var svgns = "http://www.w3.org/2000/svg";

var protocolversion;
var timeleft = "+500s";
var statustimerid = 0;
var helpstack = [];
var tips = [];
var mousedown = false;
var server = new XMLHttpRequest();
var resizeTimer = null;
var inputtaken = 0;
var mousecounter = 0;
var transienttabs;
var permanenttabs;
var buildanother = 0;
var currentbuildplanet = "";
var tradearrow = [[ 0.0, -0.0],
                  [-0.5, -.25],
                  [-0.5, -.3],
                  [-0.3, -.3],
                  [-0.3, -.5],
                  [ 0.3, -.5],
                  [ 0.3, -.3],
                  [ 0.5, -.3],
                  [ 0.5, -.25]];
var curfleetid = 0;
var curplanetid = 0;
var currouteid = 0;
var curarrowid = 0;
var curslider = "";

var gm;

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

// Jonas Raoni Soares Silva
// http://jsfromhell.com/math/is-point-in-poly [v1.0]
function pointinpoly(poly, pt){
	for(var c = false, i = -1, l = poly.length, j = l - 1; ++i < l; j = i)
		((poly[i].y <= pt.y && pt.y < poly[j].y) || (poly[j].y <= pt.y && pt.y < poly[i].y))
		&& (pt.x < (poly[j].x - poly[i].x) * (pt.y - poly[i].y) / (poly[j].y - poly[i].y) + poly[i].x)
		&& (c = !c);
	return c;
}

function GameMap(cx,cy)
{
  // cx and cy contain map coordinates for the
  // initial center of the map

  this.zoomlevel    = 3;
  this.zoomlevels   = [480.0,250.0,130.0,70.0,40.0,25.0,15.0];
  
  this.map          = document.getElementById('map');
  this.maplayer0    = document.getElementById('maplayer0');
  this.maplayer1    = document.getElementById('maplayer1');
  this.maplayer2    = document.getElementById('maplayer2');
  this.svgmarkers   = document.getElementById('svgmarkers');
  this.youarehere   = document.getElementById('youarehere');
  
  // translate distance from map to screen coords
  this.td = function(distance){
    return distance * this.zoomlevels[this.zoomlevel];
  }

  this.mousepos     = new Point(this.td(cx), this.td(cy)); //last reported mouse position
  this.mouseorigin  = new Point(this.td(cx), this.td(cy)); // used to determine the x/y offset for mouse panning
  this.capitolpos   = new Point(cx,cy);
  
  
  this.curcenter    = new Point(this.td(cx), this.td(cy)); 
  this.mapwidth     = $(window).width()/this.zoomlevels[this.zoomlevel];
  this.mapheight    = $(window).height()/this.zoomlevels[this.zoomlevel];
  this.screenwidth  = $(window).width();
  this.screenheight = $(window).height();
  this.topleft      = new Point(this.curcenter.x-(this.screenwidth/2.0),
                                this.curcenter.y-(this.screenheight/2.0));
  this.playercolors = [];


  this.map.setAttribute("width",this.screenwidth);
  this.map.setAttribute("height",this.screenheight);



  this.sectorgeneration = 0;
  this.friends          = [];
  this.enemies          = [];
  this.sectors          = [];
  this.routes           = [];
  this.sectorsstatus    = [];
  
  this.scene = new QUAD.init({'x':0,'y':0,
                            'w':this.screenwidth,
                            'h':this.screenheight,
                            'maxChildren':5,
                            'maxDepth':5});
  this.curarrow = false;

  // translate x from map to screen
  this.tx = function(x) {
    return (x * this.zoomlevels[this.zoomlevel]) - this.topleft.x;
  }

  // translate y from map to screen
  this.ty = function(y){
    return (y * this.zoomlevels[this.zoomlevel]) - this.topleft.y;
  }

  // current magnification factor
  this.getmagnification = function(){
    return this.zoomlevels[this.zoomlevel];
  }

  this.screentogamecoords = function(evt,sx,sy){
    var curloc = getcurxy(evt);
    if(sx){
      curloc = new Point(sx,sy);
    }
    var cz = this.getmagnification();
    curloc.x = (this.topleft.x + curloc.x)/cz;
    curloc.y = (this.topleft.y + curloc.y)/cz;
    return curloc;
  }

  this.buildsectorkey = function(mx,my){
    return (Math.floor(mx/5.0)*1000 + Math.floor(my/5.0)).toString();
  }

  this.setxy = function(evt)
  {
    this.mousepos.x = evt.clientX;
    this.mousepos.y = evt.clientY;
    var curloc = this.screentogamecoords(evt);
    this.mousepos.mapx = curloc.x;
    this.mousepos.mapy = curloc.y;
  }

  this.centermap = function(mx,my){
    mx *= this.getmagnification();
    my *= this.getmagnification();
   
    this.curcenter.x = mx;
    this.curcenter.y = my;
    this.topleft.x = mx-(this.screenwidth/2.0);
    this.topleft.y = my-(this.screenheight/2.0);

    this.resetmap(false);
  }

  this.panmap = function(dx,dy,loadnewsectors){
    this.curcenter.x += dx;
    this.curcenter.y += dy;
    this.topleft.x = this.curcenter.x-(this.screenwidth/2.0);
    this.topleft.y = this.curcenter.y-(this.screenheight/2.0);

    if(loadnewsectors){
      this.resetmap(false);
    }
  }

  this.resize = function(){
    setstatusmsg($(window).width());
    var newwidth = $(window).width();
    var newheight = $(window).height();
    if(newwidth !== 0){
      this.screenwidth = newwidth-6;
      this.curcenter.x = this.topleft.x+this.screenwidth/2.0;
    }
    if(newheight !== 0){
      this.screenheight = newheight-8;
      this.curcenter.y = this.topleft.y+this.screenheight/2.0;
    }
    this.map.setAttribute("width",this.screenwidth);
    this.map.setAttribute("height",this.screenheight);
    this.resetmap(false);
  }
  
  this.eatmouseclick = function(evt){
    var x = evt.pageX;
    var y = evt.pageY;
    var potentials = this.scene.retrieve({'x':x,'y':y });
    for (i in potentials){
      potential = potentials[i];
      if ((potential.type=='arrow')&&
          (pointinpoly(potential.poly, {'x':x,'y':y}))){
        potential.action(evt);
        return true;
      }
    }
    return false;
  }
  this.dohover = function(evt){
    var x = evt.pageX;
    var y = evt.pageY;
    var potentials = this.scene.retrieve({'x':x,'y':y });
    var hovered = false;
    //setstatusmsg(potentials.length);
    for (i in potentials){
      potential = potentials[i];
      if ((potential.type=='arrow')&&
          (pointinpoly(potential.poly, {'x':x,'y':y}))){
        potential.mouseover(evt);
        this.curarrow = potential.id;
        hovered = true;
      }
    }
    if((!hovered)&&(this.curarrow)){
      arrowmouseout(this.curarrow);
      this.curarrow = false;
    }
  }

  this.zoom = function(evt, magnification, screenloc){
    var i=0;
    var zid=0;
    var changezoom = 0;
    var oldzoom = this.getmagnification();
    var newzoomlevel=0;
    if((magnification === "+")&&(this.zoomlevel<6)){
      changezoom = 1;
      this.zoomlevel++;
    } else if((magnification === "-")&&(this.zoomlevel>0)){
      changezoom = 1;
      this.zoomlevel--;
    } else if (newzoomlevel = parseInt(magnification)) {
      changezoom = 1;
      if((newzoomlevel >= 0)&&(newzoomlevel <= 5)){
        this.zoomlevel = newzoomlevel;
      }
    }

    
    if(changezoom){
      // manipulate the zoom dots in the UI
      for(i=1;i<=this.zoomlevel;i++){
        zid = "#zoom"+i;
        $(zid).attr('src','/site_media/blackdot.png');
      }
      for(i=this.zoomlevel+1;i<7;i++){
        zid = "#zoom"+i;
        $(zid).attr('src','/site_media/whitedot.png');
      }

      var newzoom = this.getmagnification();
      
      this.curcenter.x = this.curcenter.x/oldzoom*newzoom;
      this.curcenter.y = this.curcenter.y/oldzoom*newzoom;
      this.topleft.x   = this.curcenter.x-(this.screenwidth/2.0);
      this.topleft.y   = this.curcenter.y-(this.screenheight/2.0);
      this.resetmap(false);
    }
  }

  this.zoommiddle = function(evt, magnification)
  {
    var p = new Point(this.screenwidth/2.0,this.screenheight/2.0);
    this.zoom(evt,magnification,p);
  }

  this.getsectors = function(newsectors,force,getnamedroutes)
  {
    var submission = {};
    var doit = 0;
    var sector = 0;
    this.sectorgeneration++;
    // convert newsectors (which comes in as a straight array)
    // over to the loaded sectors array (which is associative...)
    // and see if we have already asked for that sector (or indeed
    // already have it in memory, doesn't really matter...)
    for (sector in newsectors){
      if((force===1)||(!(sector in this.sectorsstatus))){
        this.sectorsstatus[sector] = this.sectorgeneration;
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

  this.adjustview = function(viewable)
  {
    var key;
    
    buildnamedroutes();

    for (key in viewable){
      if( typeof key === 'string'){
        var sectoridl1 = "sectorl1-"+key;
        var sectoridl2 = "sectorl2-"+key;
        if (((key in this.sectorsstatus)&&
             (this.sectorsstatus[key]==='-'))&&
            (key in this.sectors)){
          this.sectorsstatus[key] = "+";
          var newsectorl1 = document.createElementNS(svgns, 'g');
          var newsectorl2 = document.createElementNS(svgns, 'g');

          newsectorl2.setAttribute('id', sectoridl2);
          newsectorl2.setAttribute('class', 'mapgroupx');
          
          newsectorl1.setAttribute('id', sectoridl1);
          newsectorl1.setAttribute('class', 'mapgroupx');
          
          var sector = this.sectors[key];
          buildsectorfleets(sector,newsectorl1,newsectorl2);
          buildsectorplanets(sector,newsectorl1, newsectorl2);
          buildsectorconnections(sector,newsectorl1,newsectorl2);

          gm.maplayer1.appendChild(newsectorl1);
          gm.maplayer2.appendChild(newsectorl2);
        }
      }
    }
  }


  this.loadnewsectors = function(response){
    //hidestatusmsg("loadnewsectors");
    var sector = 0;
    var key = 0;
    var viewable = this.viewablesectors();
    var deletesectors = [];
   
    if ('routes' in response) {
      for (route in response.routes) {
        this.routes[route]  = response.routes[route];
        this.routes[route].p = eval(this.routes[route].p);
      }
    }
    if ('sectors' in response) {
      for (sector in response.sectors){
        if (typeof sector === 'string' && sector != "routes"){
            
          if ((sector in this.sectorsstatus) && 
             (this.sectorsstatus[sector] === '+')){
            deletesectors[sector] = 1;
          }
          this.sectors[sector] = response.sectors[sector];
          this.sectorsstatus[sector] = '-';
        }
      }
    }
    if ('colors' in response) {
      for (i in response.colors){
        gm.playercolors[response.colors[i][0]] = response.colors[i].slice(1);
      }
    }

    // first, remove out of view sectors...
    for (key in this.sectorsstatus){
      if(typeof key === 'string'){
        if ((!(key in viewable))&&(this.sectorsstatus[key]==='+')){
          deletesectors[key] = 1;
        }
      }
    }
    for (key in deletesectors){
      if(typeof key === 'string'){
        this.sectorsstatus[key] = '-';
        var remsector;
        
        remsector = document.getElementById('sectorl1-'+key);
        if(remsector){
          this.maplayer1.removeChild(remsector);
        }

        remsector = document.getElementById('sectorl2-'+key);
        if(remsector){
          this.maplayer2.removeChild(remsector);
        }
      }
    }
    this.adjustview(viewable);
  }

  this.viewablesectors = function()
  {
    var cz     = gm.getmagnification();
    var topx   = parseInt((this.topleft.x/cz)/5.0);
    var topy   = parseInt((this.topleft.y/cz)/5.0);
    var width  = ((this.screenwidth/cz)/5.0)+1;
    var height = ((this.screenheight/cz)/5.0)+1;
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
  
  this.resetmap = function(reload)
  {
    var key = 0;
    
    this.scene.clear();
    while(this.maplayer0.hasChildNodes()){
      this.maplayer0.removeChild(this.maplayer0.firstChild);
    }

    while(this.maplayer1.hasChildNodes()){
      this.maplayer1.removeChild(this.maplayer1.firstChild);}
    
    while(this.maplayer2.hasChildNodes()){
      this.maplayer2.removeChild(this.maplayer2.firstChild);
    }

    for (key in this.sectorsstatus){
      if(this.sectorsstatus[key] === '+'){
        this.sectorsstatus[key] = '-';
      }
    }
    if(reload){
      this.sectorsstatus = [];
    }
    var viewable = this.viewablesectors();
    buildsectorrings();
    this.adjustview(viewable);
    routebuilder.redraw();
    this.getsectors(viewable,0);
  }
}

function SliderContainer(id, newside)
{
  var side = newside;
  var tabs = {};
  var container = "#"+id;
  var temphidetab = "";

  this.openedtab = "";
  this.opened = false;
  this.curtabtakesinput = false;

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

  this.takesinput = function(tab){
    var settab = container + " #"+tab;
    $(settab).attr('takesinput',1);
  }


  this.removetab = function(remid){
    remtab = container+' #'+remid;
    $(remtab).remove();
    if(this.opened === true && remid === this.openedtab){
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
      if ($(showtabsel).attr('takesinput')){
        this.curtabtakesinput = true;
        inputtaken++;
      }
      $(container + " .slidertab"+side).hide();
      $(container + " .slidertab"+side+" .slidercontent"+side).hide();
      $(container + " .slidertab"+side+" .ph .slidercontent"+side).hide();
      $(showtabsel+"title").show();
      $(showtabsel+"content").show();
      this.openedtab = showtab;
      this.opened = true;
      $(container).ready(function() {
        $(showtabsel).show('fast');
      });
    }
  };

  this.temphidetabs = function(){
    if(this.opened===true){
      temphidetab = this.openedtab;
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
    if((this.curtabtakesinput)&&(inputtaken>0)){
      inputtaken--;
      this.curtabtakesinput = false;
    }
    $(container + " .slidertab"+side+" .ph .slidercontent"+side).hide();
    $(container + " .slidertab"+side+" .slidertitle"+side).show();
    $(container + " .slidertab"+side).show();
    this.opened = false;
    this.openedtab = "";
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
  if('subhead' in args){
    contents += '  <h3>' + args.subhead + '</h3><br/><br/>';
  }
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
  if(args.numeric){ 
    $('#'+stringid).numeric({'min':args.min,'max':args.max});
  }
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

  clearTimeout(statustimerid);
  $('#statusmsg').html(msg);
  $('#statusmsg').show();
}

function showbadge(badge){
  setstatusmsg("<img class='noborder' width='150' height='150' src='/site_media/badges/"+badge+".png'/>");
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
  statustimerid=setTimeout("$('#statusmsg').hide();",1000);
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
  gm.svgmarkers.appendChild(marker);
  return marker;
}

function buildsectorrings()
{
  var cz = gm.getmagnification();

  
  var minx = gm.topleft.x/cz;
  var miny = gm.topleft.y/cz;
  var maxx = minx + gm.screenwidth/cz;
  var maxy = miny + gm.screenheight/cz;
  
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
    drawlines(minangle,maxangle,mindistance,maxdistance);
  } else if ((minangle < 0) && (maxangle > 0)){
    if (maxangle-minangle > 2){
      minangle+=(3.14159*2);
      drawlines(minangle,maxangle,mindistance,maxdistance);
    } else {
      drawlines(minangle,0,mindistance,maxdistance);
      drawlines(0,maxangle,mindistance,maxdistance);
    }
  } else {
    drawlines(minangle,maxangle,mindistance,maxdistance);
  }

   
}

function drawlines(minangle, maxangle, mindistance, maxdistance){
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
          ring.setAttribute('stroke',"#FF0000");
          ring.setAttribute('fill',"none");
          ring.setAttribute('id',"sectorring"+i);
          ring.setAttribute('stroke-width',".3");
          gm.maplayer0.appendChild(ring);
        }
        ring.setAttribute('cx',gm.tx(1500));
        ring.setAttribute('cy',gm.ty(1500));
        ring.setAttribute('r',gm.td(i*20));
      } else {
        if(!ring){
          ring = document.createElementNS(svgns,'path');
          ring.setAttribute('stroke',"#ff0000");
          ring.setAttribute('fill',"none");
          ring.setAttribute('id',"sectorring"+i);
          ring.setAttribute('stroke-width',".3");
          gm.maplayer0.appendChild(ring);
        }
        var radius = gm.td(i*20);
        var startx = gm.tx(1500-Math.cos(minangle)*i*20);
        var starty = gm.ty(1500-Math.sin(minangle)*i*20);
        var endx =   gm.tx(1500-Math.cos(maxangle)*i*20);
        var endy =   gm.ty(1500-Math.sin(maxangle)*i*20);
        var path = "M " + startx + " " + starty + " A " + 
                   radius + " " + radius + " 0 0 1 " + 
                   endx + " " + endy;
        ring.setAttribute('d',path);
      }
    } else if (ring) {
      gm.maplayer0.removeChild(ring);
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
        radial.setAttribute('stroke',"#ff0000");
        radial.setAttribute('id',"sectorradial"+i);
        radial.setAttribute('stroke-width',".3");
        gm.maplayer0.appendChild(radial);
      }
      radial.setAttribute('x1', gm.tx(1500-Math.cos(angle)*startdistance));
      radial.setAttribute('y1', gm.ty(1500-Math.sin(angle)*startdistance));
      radial.setAttribute('x2', gm.tx(1500-Math.cos(angle)*
                                 (maxdistance+(maxdistance-mindistance))));
      radial.setAttribute('y2', gm.ty(1500-Math.sin(angle)*
                                 (maxdistance+(maxdistance-mindistance))));
    } else if (radial) {
      gm.maplayer0.removeChild(radial);
    }
  }
}

function buildroute(r, container, color)
{
  // check to see if the route has been deleted
  if(!(r in gm.routes)){
    return 0;
  }
  var route = document.getElementById("rt-"+r);
  if(!route){
    var circular = gm.routes[r].c;
    var points = gm.routes[r].p;
    var points2 = ""
    for (p in points){
      if (points[p].length == 3){
        points2 += gm.tx(points[p][1])+","+gm.ty(points[p][2])+" ";
      } else if (points[p].length == 2) {
        points2 += gm.tx(points[p][0])+","+gm.ty(points[p][1])+" ";
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
    if('n' in gm.routes[r]){
      route.setAttribute('stroke-width', gm.td(.15));
    } else {
      route.setAttribute('stroke-width', gm.td(.1));
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
  for (route in gm.routes){
    r = gm.routes[route]
    if ('n' in r){
      buildroute(route, gm.maplayer1, '#ffffff');
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
  for(fleetkey in sector.fleets){
    if(typeof fleetkey === 'string'){
      var fleet = sector.fleets[fleetkey];
      var gid = 'gf'+fleet.i;
      var playerowned;
      var color = gm.playercolors[fleet.o][0];

      if ('ps' in fleet){
        playerowned=1;
      } else {
        playerowned=0;
      }
      group = document.createElementNS(svgns, 'g');
      group.setAttribute('fill', color);
      group.setAttribute('id', gid);
      group.setAttribute('stroke', color);
      group.setAttribute('stroke-width', '.01');
      group.setAttribute('onmouseover',
                         'fleethoveron(evt,"'+fleet.i+'",'+fleet.x+','+fleet.y+');');
      group.setAttribute('onmouseout', 
                         'fleethoveroff(evt,"'+fleet.i+'")');
      group.setAttribute('onclick', 
                         'dofleetmousedown(evt,"'+fleet.i+'",'+playerowned+')');
      if ('r' in fleet){
        if(!buildroute(fleet.r, newsectorl1, color)){
          delete fleet.r;
        }
      } 
      if ('s' in fleet){
        sensegroup = document.getElementById("sg-"+fleet.o);
        if(!sensegroup){
          sensegroup = document.createElementNS(svgns,'g');
          sensegroup.setAttribute('fill',color);
          sensegroup.setAttribute('id','sg-'+fleet.o);
          sensegroup.setAttribute('opacity','.3');
          gm.maplayer0.appendChild(sensegroup);
        }
        sensecircle = document.createElementNS(svgns, 'circle');
        sensecircle.setAttribute('cx', gm.tx(fleet.x));
        sensecircle.setAttribute('cy', gm.ty(fleet.y));
        sensecircle.setAttribute('r', gm.td(fleet.s));
        sensegroup.appendChild(sensecircle);
      }

      if ('x2' in fleet){
        
        marker = document.getElementById("marker-"+color.substring(1));
        if(!marker){
          marker = buildmarker(color);
        }

        points = ""
        line = document.createElementNS(svgns,'polyline');
        points += gm.tx(fleet.x)+","+gm.ty(fleet.y)+" "+gm.tx(fleet.x2)+","+gm.ty(fleet.y2);
        if ('r' in fleet) {
          var circular = gm.routes[fleet.r].c;
          var routepoints = gm.routes[fleet.r].p;
          if (routepoints[fleet.cl].length===2) {
            points += " " + 
                      gm.tx(routepoints[fleet.cl][0]) + "," + 
                      gm.ty(routepoints[fleet.cl][1]);
          } else if (routepoints[fleet.cl].length===3) {
            points += " " + 
                      gm.tx(routepoints[fleet.cl][1]) + "," + 
                      gm.ty(routepoints[fleet.cl][2]);
          }
        }
        line.setAttribute('points',points);
        line.setAttribute('marker-end', 'url(#marker-'+color.substring(1)+')');
        line.setAttribute('stroke',color);
        line.setAttribute('fill','none');
        if((fleet.f&4)){  // scout
          if(gm.zoomlevel<5){
            line.setAttribute('stroke-dasharray',gm.td(0.09)+","+gm.td(0.09));
            line.setAttribute('opacity', .5);
          } else {
            line.setAttribute('opacity', .25);
          }
          line.setAttribute('stroke-width', .2 + gm.td(0.03));
        } else if((fleet.f&8)) { // arc
          line.setAttribute('stroke-dasharray',gm.td(0.3)+","+gm.td(0.3));
          line.setAttribute('stroke-width', .2 + gm.td(0.03));
        } else if((fleet.f&16)) { // merchant
          if(gm.zoomlevel<5){
            line.setAttribute('stroke-dasharray',gm.td(0.03)+","+gm.td(0.09));
            line.setAttribute('opacity', .7);
          } else {
            line.setAttribute('opacity', .35);
          }
          line.setAttribute('stroke-width', .2 + gm.td(0.04));
        } else if(fleet.f&32) { // military
          line.setAttribute('stroke-width', .2 + gm.td(0.05));
        } else { // "other"
          line.setAttribute('stroke-width', .2 + gm.td(0.03));
        }


        group.appendChild(line);
      }
      if(fleet.f&2) {
        // damaged
        circle = document.createElementNS(svgns, 'circle');
        circle.setAttribute('cx', gm.tx(fleet.x));
        circle.setAttribute('cy', gm.ty(fleet.y));
        circle.setAttribute('r', gm.td(0.2));
        circle.setAttribute('style','fill:url(#damagedfleet);');
        newsectorl1.appendChild(circle);
      } else if(fleet.f&1) {
        // destroyed
        circle = document.createElementNS(svgns, 'circle');
        circle.setAttribute('cx', gm.tx(fleet.x));
        circle.setAttribute('cy', gm.ty(fleet.y));
        circle.setAttribute('r', gm.td(0.2));
        circle.setAttribute('style','fill:url(#destroyedfleet);');
        newsectorl1.appendChild(circle);
      }
      // the fleet itself
      circle = document.createElementNS(svgns, 'circle');
      circle.setAttribute('fill', color);
      circle.setAttribute('cx', gm.tx(fleet.x));
      circle.setAttribute('cy', gm.ty(fleet.y));
      circle.setAttribute('r', gm.td(0.04));
      circle.setAttribute('or', gm.td(0.04));
      var cid = 'f'+fleet.i;
      circle.setAttribute('id', cid );
      group.appendChild(circle);
      newsectorl2.appendChild(group);
    }
  } 
}


function buildsectorconnections(sector,newsectorl1, newsectorl2)
{
  var i;
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

      line.setAttribute('x1', gm.tx((x1+(Math.cos(angle+3.14159)*0.3))));
      line.setAttribute('y1', gm.ty((y1+(Math.sin(angle+3.14159)*0.3))));
      line.setAttribute('x2', gm.tx((x2+(Math.cos(angle)*0.3))));
      line.setAttribute('y2', gm.ty((y2+(Math.sin(angle)*0.3))));
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
  for(planetkey in sector.planets){
    if(typeof planetkey === 'string'){
      var planet = sector.planets[planetkey];
      var color = '#FFFFFF';
      if('o' in planet){
        color = gm.playercolors[planet.o][0];
      }
      
      var iscapital = ((planet.o in gm.playercolors)&&
                       (gm.playercolors[planet.o][1]==planet.i)) ? true:false;
      // draw You Are Here and it's arrow if it's a new player
      if (((newplayer === 1) && (planet.f&128))){
        gm.youarehere.setAttribute('visibility','visible');
        gm.youarehere.setAttribute('x',gm.tx(planet.x-1.5));
        gm.youarehere.setAttribute('y',gm.ty(planet.y+1.3));
        line = document.createElementNS(svgns, 'line');
        line.setAttribute('stroke-width', '1.2');
        line.setAttribute('stroke', '#aaaaaa');
        line.setAttribute('marker-end', 'url(#endArrow)');
        line.setAttribute('x2', gm.tx(planet.x-0.2));
        line.setAttribute('y2', gm.ty(planet.y+0.3));
        line.setAttribute('x1', gm.tx(planet.x-0.7));
        line.setAttribute('y1', gm.ty(planet.y+1.0));
        newsectorl2.appendChild(line);
      }
    
      // sensor range
      if (('s' in planet)&&('o' in planet)){
        var opacity = .35 - ((gm.zoomlevel+1)/35.0);
        sensegroup = document.getElementById("sg-"+planet.o);
        if(!sensegroup){
          sensegroup = document.createElementNS(svgns,'g');
          sensegroup.setAttribute('id','sg-'+planet.o);
          sensegroup.setAttribute('fill',color);
          sensegroup.setAttribute('opacity',opacity);
          gm.maplayer0.appendChild(sensegroup);
        }
        circle = document.createElementNS(svgns, 'circle');
        circle.setAttribute('cx',  gm.tx(planet.x));
        circle.setAttribute('cy',  gm.ty(planet.y));
        circle.setAttribute('r',   gm.td(planet.s));
        sensegroup.appendChild(circle);
      }
      if(planet.f&2048) {
        // damaged
        circle = document.createElementNS(svgns, 'circle');
        circle.setAttribute('cx', gm.tx(planet.x));
        circle.setAttribute('cy', gm.ty(planet.y));
        circle.setAttribute('r', gm.td(planet.r+.5));
        circle.setAttribute('style','fill:url(#damagedplanet);');
        newsectorl1.appendChild(circle);
      }

      // food problem
      if((planet.f&1)||(planet.f&2)){
        highlight = document.createElementNS(svgns, 'circle');
        radius = 0.12;
        if(iscapital){
          radius += 0.05;
        }
        highlight.setAttribute('cx', gm.tx(planet.x));
        highlight.setAttribute('cy', gm.ty(planet.y));
        highlight.setAttribute('r', gm.td(planet.r+radius));
        if(planet.f&1){
          highlight.setAttribute('stroke', 'yellow');
        } else {
          highlight.setAttribute('stroke', 'red');
        }  
        highlight.setAttribute('fill', 'none');
        highlight.setAttribute('stroke-width', gm.td(0.035));
        newsectorl1.appendChild(highlight);
      }
      

      // rgl govt.
      if (planet.f&4){
        highlight = document.createElementNS(svgns, 'circle');
        highlight.setAttribute('cx', gm.tx(planet.x));
        highlight.setAttribute('cy', gm.ty(planet.y));
        highlight.setAttribute('r', gm.td(5));
        highlight.setAttribute('stroke', 'white');
        highlight.setAttribute('fill', 'none');
        highlight.setAttribute('stroke-width', gm.td(0.1));
        highlight.setAttribute('stroke-opacity', 0.1);
        newsectorl1.appendChild(highlight);
      }

      // planetary defense
      if ((planet.f&256)&&(gm.zoomlevel < 6)){
        highlight = document.createElementNS(svgns, 'circle');
        highlight.setAttribute('cx', gm.tx(planet.x));
        highlight.setAttribute('cy', gm.ty(planet.y));
        highlight.setAttribute('r', gm.td(4.0));
        var linelength = (gm.td(4.0) * Math.PI * 2.0)/50.0;
        if (('o' in planet)&&('e'+planet.o in gm.enemies)){
          highlight.setAttribute('stroke', '#FFAA44');
          highlight.setAttribute('stroke-opacity', 1.0);
          highlight.setAttribute('stroke-width', gm.td(0.03));
        } else {
          highlight.setAttribute('stroke', '#AAFF44');
          highlight.setAttribute('stroke-opacity', 0.5);
          highlight.setAttribute('stroke-width', gm.td(0.02));
        }
        highlight.setAttribute('fill', 'none');
        highlight.setAttribute('stroke-dasharray',linelength*.7+","+linelength*.3);
        newsectorl1.appendChild(highlight);
      }
     
      // farm subsidy
      if ((planet.f&128)&&(planet.f&512)){
        highlight = document.createElementNS(svgns, 'circle');
        radius = 0.16;
        if(iscapital){ // capital
          radius += 0.05;
        }
        if((planet.f&1)||(planet.f&2)){ // food scarcity
          radius += 0.05;
        }
        if (((planet.f&8)||(planet.f&16)||(planet.f&32))&&(gm.zoomlevel < 5)){
          radius += .1;
        }
        var linelength = (gm.td(radius+planet.r) * Math.PI * 2.0)/12.0;
        highlight.setAttribute('cx', gm.tx(planet.x));
        highlight.setAttribute('cy', gm.ty(planet.y));
        highlight.setAttribute('r', gm.td(planet.r+radius));
        highlight.setAttribute('stroke', 'green');
        highlight.setAttribute('fill', 'none');
        highlight.setAttribute('stroke-width', gm.td(0.15));
        highlight.setAttribute('stroke-opacity', .3);
        highlight.setAttribute('stroke-dasharray',linelength*.5+","+ linelength*.5);
        
        newsectorl1.appendChild(highlight);
      }
      
      // drill subsidy
      if ((planet.f&128)&&(planet.f&1024)){
        highlight = document.createElementNS(svgns, 'circle');
        radius = 0.12;
        if(iscapital){ // capital
          radius += 0.05;
        }
        if((planet.f&1)||(planet.f&2)){ // food scarcity
          radius += 0.05;
        }
        if (((planet.f&8)||(planet.f&16)||(planet.f&32))&&(gm.zoomlevel < 5)){
          radius += .1;
        }
        var linelength = (gm.td(radius+planet.r) * Math.PI * 2.0)/12.0;
        highlight.setAttribute('cx', gm.tx(planet.x));
        highlight.setAttribute('cy', gm.ty(planet.y));
        highlight.setAttribute('r', gm.td(planet.r+radius));
        highlight.setAttribute('stroke', 'yellow');
        highlight.setAttribute('fill', 'none');
        highlight.setAttribute('stroke-width', gm.td(0.07));
        highlight.setAttribute('stroke-opacity', .2);
        highlight.setAttribute('stroke-dasharray',linelength*.8+","+ linelength*.2);
        
        newsectorl1.appendChild(highlight);
      }

      // military circle
      if (((planet.f&8)||(planet.f&16)||(planet.f&32))&&(gm.zoomlevel < 5)){
        highlight = document.createElementNS(svgns, 'circle');
        radius = 0.12;
        if(iscapital){ // capital
          radius += 0.05;
        }
        if((planet.f&1)||(planet.f&2)){ // food scarcity
          radius += 0.05;
        }
        highlight.setAttribute('cx', gm.tx(planet.x));
        highlight.setAttribute('cy', gm.ty(planet.y));
        highlight.setAttribute('r', gm.td(planet.r+radius));
        highlight.setAttribute('stroke', color);
        highlight.setAttribute('fill', 'none');
        highlight.setAttribute('stroke-width', gm.td(0.02));
        highlight.setAttribute('stroke-opacity', 0.4);
        var linelength = (gm.td(radius+planet.r) * Math.PI * 2.0)/35.0;
        highlight.setAttribute('stroke-dasharray',linelength*.5+","+linelength*.5);
      
        if(planet.f&32){
          // matter synth 2
          highlight.setAttribute('stroke-width',gm.td(0.050));
        }
        if (planet.f&16) {
          // military base
          var linelength = (gm.td(radius+planet.r) * Math.PI * 2.0)/10.0;
          highlight.setAttribute('stroke-dasharray',linelength*.75+","+linelength*.25);
        } 
       

        newsectorl1.appendChild(highlight);
      }
        

      // capital ring
      if (iscapital) {
        highlight = document.createElementNS(svgns, 'circle');
        highlight.setAttribute('cx', gm.tx(planet.x));
        highlight.setAttribute('cy', gm.ty(planet.y));
        highlight.setAttribute('r', gm.td(planet.r+0.12));
        highlight.setAttribute('stroke', color);
        highlight.setAttribute('stroke-width', gm.td(0.02));
        newsectorl1.appendChild(highlight);
      } 

      // inhabited ring
      if (planet.o){
        highlight = document.createElementNS(svgns, 'circle');
        highlight.setAttribute('cx', gm.tx(planet.x));
        highlight.setAttribute('cy', gm.ty(planet.y));
        highlight.setAttribute('r', gm.td(planet.r+0.06));
        highlight.setAttribute('stroke', color);
        highlight.setAttribute('stroke-width', gm.td(0.04));
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
      // the star itself
      circle.setAttribute('id', 'p'+planet.i);
      circle.setAttribute('cx', gm.tx(planet.x));
      circle.setAttribute('cy', gm.ty(planet.y));
      circle.setAttribute('ox', planet.x);
      circle.setAttribute('oy', planet.y);
      circle.setAttribute('r', gm.td(planet.r));
      circle.setAttribute('or', gm.td(planet.r));
      circle.setAttribute('fill', planet.c);
      circle.setAttribute('onmouseover',
                          'planethoveron(evt,"'+planet.i+'","'+planet.n+'")');
      circle.setAttribute('onmouseout',
                          'planethoveroff(evt,"'+planet.i+'")');
      circle.setAttribute('onclick',
                          'doplanetmousedown(evt,"'+planet.i+'")');
      newsectorl2.appendChild(circle);
    }
  }
}


function inviewplanets(func,fleet)
{
  var sectorkey, planetkey, arrowkey;
  viewable = gm.viewablesectors();
  for (sectorkey in viewable){
    if ((sectorkey in gm.sectors)&&
        (sectorkey in gm.sectorsstatus)&&
        (gm.sectorsstatus[sectorkey]='+')){
      sector = gm.sectors[sectorkey];
      sectorl1 = document.getElementById('sectorl1-'+sectorkey);

      if('planets' in sector){
        for (planetkey in sector.planets){
          if(typeof planetkey === 'string'){
            var planet = sector.planets[planetkey];
            func(planet,fleet,sectorl1);
          }
        }
      }
    }
  }
}

function removearrow(planet,fleet,sectorl1)
{
  var arrow = document.getElementById("arrow-"+planet.i);
  if(arrow){
    sectorl1.removeChild(arrow);
  }
}

function buildarrow(planet,fleet,sectorl1)
{
  var color = 'white';
  // military
  if (!(fleet)){
    return;
  }
  if (!('f' in fleet)){
    fleet = getfleet(fleet.i, fleet.x, fleet.y);
    if(!(fleet)){
      return;
    }
  }
  if (fleet.f&4){
    return;
  }
  if (fleet.f&32){
    if (!('o' in planet)){
      return;
    }
    if (!('e'+planet.o in gm.enemies)){
      return;
    }
    color = 'orange';
  }

  // trade
  if (fleet.f&16){
    if(!((planet.f&64)||(planet.f&128))){
      return;
    }
  }

  //arc
  if (fleet.f&8){
    if(('o' in planet)&&(planet.o != fleet.o)){
      return;
    }
    if(planet.p > 10000){
      return;
    }
  }
    
  var arrow = document.createElementNS(svgns, 'polygon');
  var arrowid = "arrow-"+planet.i;
  var angle = (3.14159/2.0)+Math.atan2(fleet.y-planet.y,fleet.x-planet.x);
  var points = "";
  var poly = [];
  var x = 0.0;
  var y = 0.0;
  var yoff = 0.0;
  bbox = [10000,10000,-10000,-10000];
  for (i in tradearrow){
    yoff = tradearrow[i][1] - planet.r - .2 
    x = gm.tx(planet.x + tradearrow[i][0]*Math.cos(angle) - yoff*Math.sin(angle));
    y = gm.ty(planet.y + tradearrow[i][0]*Math.sin(angle) + yoff*Math.cos(angle));
    points += x + "," + y + " ";
    if(x<bbox[0])bbox[0]=x;
    if(x>bbox[2])bbox[2]=x;
    if(y<bbox[1])bbox[1]=y;
    if(y>bbox[3])bbox[3]=y;
    poly.push({'x':x,'y':y});
  }
  if(bbox[0]+bbox[2] < 0)return;
  if(bbox[1]+bbox[3] < 0)return;
  if(bbox[2]>gm.screenwidth)return;
  if(bbox[3]>gm.screenheight)return;
  gm.scene.insert({
    'x'         :bbox[0]+((bbox[2]-bbox[0])/2.0),
    'y'         :bbox[1]+((bbox[3]-bbox[1])/2.0),
    'w'         :bbox[2]-bbox[0],
    'h'         :bbox[3]-bbox[1],
    'type'      :'arrow',
    'poly'      :poly,
    'id'        :arrowid,
    'hoverstate':false,
    'mouseover' :function(evt){arrowmouseover(evt,arrowid,planet.n,fleet.ps);},
    'mouseout'  :function(evt){arrowmouseout(arrowid);},
    'action'    :function(evt){doplanetmousedown(evt,planet.i);}
  }); 

  arrow.setAttribute('fill', color);
  arrow.setAttribute('stroke',color);
  arrow.setAttribute('stroke-width',3);
  arrow.setAttribute('fill-opacity', '.2');
  arrow.setAttribute('stroke-opacity', '.3');
  arrow.setAttribute('id', arrowid); 
  arrow.setAttribute('points', points);
  sectorl1.appendChild(arrow);
}
          

function getfleet(fleetid, mx, my)
{
  var sectorkey = gm.buildsectorkey(mx,my);
  fleetid = parseInt(fleetid);
  if (sectorkey in gm.sectors){
    var sector = gm.sectors[sectorkey];
    for (i in sector.fleets){
      fleet = sector.fleets[i];
      if (fleet.i === fleetid){
        return fleet;
      }
    }
  }
}

function getplanet(planetid, mx, my)
{
  var sectorkey = gm.buildsectorkey(mx,my);
  planetid = parseInt(planetid);
  if (sectorkey in gm.sectors){
    var sector = gm.sectors[sectorkey];
    for (i in sector.planets){
      planet = sector.planets[i];
      if (planet.i === planetid){
        return planet;
      }
    }
  }
}


function movemenu(sx,sy)
{
  $("#menu").css('top',sy);
  $("#menu").css('left',sx);
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
  }
}





function ontonamedroute(fleetid, args)
{
  // routeid, x, y, leg   
  sendrequest(handleserverresponse,
              '/fleets/'+fleetid+'/onto/',
              'POST', args);
}

function RouteBuilder()
{
  var types = {'directto':1, 'routeto':2, 'circleroute':3, 'off': 4};
  this.named = false;

  this.routeto        = document.getElementById('routeto');
  this.circleroute    = document.getElementById('circleroute');
  
  this.type;
  this.curfleet;
  
  this.type = types.off;
  this.curfleet = 0;
  this.route = [];
  this.cancel = function()
  {
    if(this.type != types.off){
      inviewplanets(removearrow,this.curfleet);
    }

    this.type = types.off;
    this.route = [];
    this.named = false;
    this.circleroute.setAttribute('visibility','hidden');
    this.routeto.setAttribute('visibility','hidden');
    this.curfleet = 0;
  }

  this.startcommon = function(fleet)
  {
    if((fleet)&&(fleet.i != -1)){
      if (!('f' in fleet)){
        fleet = getfleet(fleet.i, fleet.x, fleet.y);
      }
      this.curfleet = fleet;
      // build goto arrows
      if(gm.zoomlevel<5){
        inviewplanets(buildarrow,this.curfleet);
        gm.dohover({pageX:gm.mousepos.x, pageY:gm.mousepos.y});
      }
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
    } else if (buildanother === 2){
      transienttabs.hidetabs();
    }
  }
  this.startnamedroute = function(planetid, loc, circular)
  {
    if(loc.x == 0 && loc.y == 0) {
      // not provided, so use the last 'clicked on' x/y
      loc.x = gm.mousepos.mapx;
      loc.y = gm.mousepos.mapy;
    }

    this.named = true;
    this.startrouteto({'i':-1, 'x':loc.x, 'y':loc.y}, 
                      circular, planetid);
  }
  
  this.redraw = function()
  {
    var cz = gm.getmagnification();
    if(this.type === types.off){
      return 0;
    } else {
      var newpoints = "";
      for (var i = 0; i < this.route.length; i++) {
        newpoints += gm.tx(this.route[i][0]) + ','+
                     gm.ty(this.route[i][1]) + ' ';
      }
        
      if ((this.type === types.routeto)||
          (this.type === types.directto)){
        this.routeto.setAttribute('points', newpoints);
      } else if (this.type === types.circleroute) {
        this.circleroute.setAttribute('points', newpoints);
      }
      if(gm.zoomlevel<5){
        inviewplanets(removearrow,null);
        inviewplanets(buildarrow,this.curfleet);
      }
    }

  }

  this.startrouteto = function (fleet, circular, planetid)
  {
    this.startcommon(fleet);
    this.route = [];
    if(planetid != -1){
      this.route.push([fleet.x,fleet.y,planetid]);
    } else {
      this.route.push([fleet.x,fleet.y]);
    }
    var coords = gm.tx(this.route[0][0])+","+gm.ty(this.route[0][1])+" "+
                 gm.tx(gm.mousepos.mapx)+","+gm.ty(gm.mousepos.mapy);
    if(circular){
      this.type = types.circleroute;
      this.circleroute.setAttribute('points',coords);
      this.circleroute.setAttribute('visibility','visible');
    } else{
      this.type = types.routeto;
      this.routeto.setAttribute('points',coords);
      this.routeto.setAttribute('visibility','visible');
    }
    setstatusmsg('Click in Space for Waypoint, click on Planet to stop at planet, press \'Enter\' to finish, \'Escape\' to Cancel');
  }

  this.startdirectto = function (fleet)
  {
    this.startcommon(fleet);
    this.type = types.directto;
    $('#fleets').hide('fast'); 
    this.route[0] = [fleet.x,fleet.y];
    var coords = gm.tx(fleet.x)+","+gm.ty(fleet.y)+" "+
                 gm.tx(gm.mousepos.mapx)+","+gm.ty(gm.mousepos.mapy);
    this.routeto.setAttribute('points',coords);
    this.routeto.setAttribute('visibility','visible');
  }

  this.active = function()
  {
    if(this.type === types.off){
      return 0;
    } else {
      return 1;
    }
  }
  this.addleg = function(evt,planet)
  {
    if(this.type === types.off){
      return;
    } else if(this.type === types.directto){
      this.finish(evt,planet); 
    } else {
      if(planet){
        var svgplanet = document.getElementById("p"+planet);
        var x  = (svgplanet.getAttribute('ox'));
        var y  = (svgplanet.getAttribute('oy'));
        this.route.push([x,y,planet]);
      } else {
        var curloc = gm.screentogamecoords(evt);
        this.route.push([curloc.x,curloc.y]);
      } 
      this.redraw();
    }
  }

  this.finish = function(evt,planet)
  {
    curloc = gm.screentogamecoords(evt);
    inviewplanets(removearrow,null);
    this.circleroute.setAttribute('visibility','hidden');
    this.routeto.setAttribute('visibility','hidden');

    transienttabs.tempshowtabs();
    permanenttabs.tempshowtabs();
    
    var request = "";
    var submission = {}
    if(this.type === types.directto){
      if(planet){
        request = "/fleets/"+this.curfleet.i+"/movetoplanet/";
        submission.planet=planet;
      } else {
        request = "/fleets/"+this.curfleet.i+"/movetoloc/";
        submission.x = curloc.x;
        submission.y = curloc.y;
      }

    } else {
      request = "/fleets/"+this.curfleet.i+"/routeto/";
      for (i in this.route){
        if (this.route[i].length === 3){
          this.route[i] = this.route[i][2];
        } else {
          this.route[i] = this.route[i][0] + '/' + this.route[i][1];
        }
      }

      submission.route = this.route.join(',');
      if (this.type === types.routeto){
        submission.circular = 'false';
      } else {
        submission.circular = 'true';
      }
      this.route = [];
    }
    if(buildanother===2){
      // transienttabs.displaytab('buildfleet'+currentbuildplanet);
      submission.buildanotherfleet = currentbuildplanet;
    }
    if(buildanother===1){
      buildanother=0;
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
                  if(string){
                    submission.name = string;
                  } else {
                    submission.name = "Name Me!";
                  }
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
  
  this.update = function (evt){
    if (this.type === types.off){
      return;
    }
    var newcenter = getcurxy(evt);
    var curpointstr = "";
    if (this.type === types.circleroute) {
      curpointstr = this.circleroute.getAttribute('points');
    } else {
      curpointstr = this.routeto.getAttribute('points');
    }
    var points = curpointstr.split(' ');
    var len = points.length;
    // some browsers give us commas, some don't
    if (curpointstr.indexOf(',') === -1) {
      points[len-2] = (newcenter.x);
      points[len-1] = (newcenter.y);
    } else {
      points[len-1] = (newcenter.x)+","+(newcenter.y);
    }
    curpointstr = points.join(' ');
    if (this.type === types.circleroute) {
      this.circleroute.setAttribute('points', curpointstr);
    } else {
      this.routeto.setAttribute('points', curpointstr);
    }

  }
}

function handlekeydown(evt)
{
  if(inputtaken == 0){
    if (evt.keyCode == 13){         // enter
      if(routebuilder.active()){
        routebuilder.finish(evt);
        return false;
      }
    } else if (evt.keyCode == 27) { // escape
      if(routebuilder.active()){
        if(buildanother){
          sendrequest(handleserverresponse,
                      '/fleets/'+routebuilder.curfleet.i+'/scrap/',
                      'POST');
        }
        routebuilder.cancel();
          
        buildanother = 0;
        return false;
      }
    } else if ((evt.keyCode === 61)||
               (evt.keyCode === 107)||
               (evt.keyCode === 187)) {    // +/=  (zoom in)
      gm.zoommiddle(evt,'-');
    } else if ((evt.keyCode === 109)||
               (evt.keyCode === 189)||
               (evt.keyCode === 95)) {    // -/_  (zoom out)
      gm.zoommiddle(evt,'+');
    } else if (evt.keyCode === 38) {                             // uparrow (pan up)
      gm.panmap(0, gm.screenheight*(-.3),true);
    } else if (evt.keyCode === 40) {                             // downarrow (pan down)
      gm.panmap(0, gm.screenheight*(.3),true);
    } else if (evt.keyCode === 37) {
      gm.panmap(gm.screenwidth*(-.3),0,true);
    } else if (evt.keyCode === 39) {
      gm.panmap(gm.screenwidth*(.3),0,true);
    }
  }

}


// svg setAttribute expects a string!?!
function arrowmouseover(evt,arrowid,name,foreign)
{
  var arrow = document.getElementById(arrowid);
  if(arrow){
    arrow.setAttribute('fill-opacity', '.3');
    arrow.setAttribute('stroke-opacity', '.4');
    var statusmsg = "<h1>"+name+"</h1>";
    //statusmsg += "<div>Accepts Foreign Trade</div>";
    statusmsg += "<div style='font-size:10px;'>Left Click to Send Fleet to Planet</div>";
    setstatusmsg(statusmsg);
    curarrowid = arrowid;
  }
}

function arrowmouseout(arrowid)
{
  var arrow = document.getElementById(arrowid);
  if (arrow){
    arrow.setAttribute('fill-opacity', '.2');
    arrow.setAttribute('stroke-opacity', '.3');
    hidestatusmsg("arrowmouseout");
  }
  curarrowid = 0;
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
  gm.setxy(evt);
  zoomcircleid(2.0,"p"+planet);
  curplanetid = planet;
}

function planethoveroff(evt,planet)
{
  hidestatusmsg("planethoveroff");
  document.body.style.cursor='default';
  gm.setxy(evt);
  zoomcircleid(1.0,"p"+planet);
  curplanetid = 0;
}

function routehoveron(evt,r)
{
  if((!routebuilder.active()) || (routebuilder.type == 1)){
    if('n' in gm.routes[r]){
      name = gm.routes[r].n;
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
    
    if('n' in gm.routes[r]){
      evt.target.setAttribute('stroke-width',gm.td(.2));
    } else {
      evt.target.setAttribute('stroke-width',gm.td(.15));
    }

    gm.setxy(evt);
    currouteid = r;
  }
}

function routehoveroff(evt,route)
{
  if((!routebuilder.active()) || (routebuilder.type == 1)){
    hidestatusmsg("routehoveroff");
    evt.target.setAttribute('opacity','.15');
    document.body.style.cursor='default';
    
    if('n' in gm.routes[route]){
      evt.target.setAttribute('stroke-width',gm.td(.15));
    } else {
      evt.target.setAttribute('stroke-width',gm.td(.1));
    }

    gm.setxy(evt);
    currouteid = 0;
  }
}

function doroutemousedown(evt,route)
{
  gm.setxy(evt);
  movemenu(gm.mousepos.x+10,gm.mousepos.y+10); 
  if ((routebuilder.curfleet)&&(routebuilder.active())){
    // routeid, x, y, leg   
    var newroute = {};
    newroute.route = route;
    newroute.sx = gm.mousepos.mapx;
    newroute.sy = gm.mousepos.mapy;
    ontonamedroute(routebuilder.curfleet.i, newroute);
    routebuilder.cancel();
  } else if (!routebuilder.active()) {
    handlemenuitemreq(evt, '/routes/'+route+'/root/');
  }
}

function fleethoveron(evt,fleetid,x,y)
{
  fleet = getfleet(fleetid,x,y);
  curfleetid = fleetid;
  about = "";
  if ('nm' in fleet){
    about += "<h1>"+fleet.nm+"</h1>";  
    about += "<h3>"+fleet.sl+"</h3>";
  } else {
    about = "<h1>"+fleet.sl+"</h1>";
  }
  about+="<hr/>";
  if (fleet.f & 2){
    about += "<div style='color:yellow;'>Damaged</div>";
  }
  if (fleet.f & 1){
    about += "<div style='color:red;'>Destroyed</div>";
  }
  setstatusmsg(about+"<div style='padding-left:10px; font-size:10px;'>Left Click to Manage Fleet</div>");
  document.body.style.cursor='pointer';
  zoomcircleid(2.0,"f"+fleetid);
  gm.setxy(evt);
}

function fleethoveroff(evt,fleet)
{ 
  curfleetid = 0;
  hidestatusmsg("fleethoveroff");
  document.body.style.cursor='default';
  zoomcircleid(1.0,"f"+fleet);
  gm.setxy(evt);
}

function buildmenu()
{
  $('#menu').attr('style','position:absolute; top:'+(gm.mousepos.y+10)+
                       'px; left:'+(gm.mousepos.x+10)+ 'px;');
  $('#menu').show();
}


function handleserverresponse(response)
{
  var id,title,content;
  if ('menu' in response){
    $('#menu').html(response.pagedata);
    $('#menu').show();
  }

  if(('protocolversion' in response)&&(response.protocolversion != protocolversion)){
    $('#protocolwarning').show()
  }
    
  if('transient' in response){
    id = response.id;
    title = response.title;
    content = response.pagedata;
    $('#menu').hide();
    transienttabs.pushtab(id, title, 'hi there1',false);
    transienttabs.settabcontent(id, content);
    if('takesinput' in response){
      transienttabs.takesinput(id);
    }
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
  if ('newfleet' in response){
    routebuilder.startdirectto(response.newfleet);
  }
  if ('fleetmoved' in response){
    if(buildanother===2){
      //transienttabs.displaytab('buildfleet'+currentbuildplanet);
      submitbuildfleet(currentbuildplanet,2);
    }
  }
    
  if ('buildfleeterror' in response){
    transienttabs.removetab('buildfleet'+currentbuildplanet);
    routebuilder.cancel();
    buildanother=0;
  }
  if ('resetmap' in response){
    sectors = [];
    gm.resetmap(true);
  }
  if ('slider' in response){
    $(curslider).html(response.slider);
  }
  if ('sectors' in response){
    gm.loadnewsectors(response.sectors);
  }
  if ('deleteroute' in response){
    var route = document.getElementById("rt-"+response.deleteroute);
    if(route){
      route.parentNode.removeChild(route);
      delete gm.routes[response.deleteroute];
      killmenu();
    }

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
  if (buildanother == 2){
    transienttabs.hidetabs();
  } else {
    transienttabs.settabcontent('buildfleet'+planetid, '');
  }
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
  var curloc = getcurxy(event);
  gm.setxy(event);
  
  var args = {};
 
  args.x = gm.mousepos.mapx;
  args.y = gm.mousepos.mapy;
  sendrequest(handleserverresponse,url, "GET", args);
}


function dofleetmousedown(evt,fleet,playerowned)
{
  gm.setxy(evt);
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


function doplanetmousedown(evt,planet)
{
  gm.setxy(evt);
  if(routebuilder.active()){
    routebuilder.addleg(evt,planet);
    stopprop(evt);
  } else {
    buildmenu();    
    handlemenuitemreq(evt, '/planets/'+planet+'/root/');
  } 
}



function init(timeleftinturn,cx,cy, protocol)
{
  var curwidth = $(window).width()-6;
  var curheight = 0;
  
  // apparantly chrome sometimes misreports window height...
  ($(window).height()-8 > $(document).height()-8) ? 
    curheight = $(window).height()-8 : 
    curheight = $(document).height()-8; 

  gm = new GameMap(cx,cy);
  var cz = gm.getmagnification();
  protocolversion = protocol;

  transienttabs = new SliderContainer('transientcontainer', 'right', 50);
  permanenttabs = new SliderContainer('permanentcontainer', 'left', 50);
  routebuilder  = new RouteBuilder();

  permanenttabs.pushtab('neighborslist', 'Neighbors', '', true);
  permanenttabs.pushtab('planetslist', 'Planets', '', true);
  permanenttabs.pushtab('fleetslist', 'Fleets', '', true);
  
  permanenttabs.gettaburl('neighborslist', '/politics/neighbors/');
  permanenttabs.gettaburl('planetslist', '/planets/');
  permanenttabs.gettaburl('fleetslist', '/fleets/');
 
  var vb = [gm.curcenter.x-(curwidth/2.0),
            gm.curcenter.y-(curheight/2.0),
            curwidth, curheight];

  movemenu(curwidth/8.0,curheight/4.0);
  

  
  buildsectorrings();
  var dosectors = gm.viewablesectors();
  gm.getsectors(dosectors,0,true);
 
  $(document).keydown(handlekeydown);

  $('#mapdiv').mousedown(function(evt) { 
    gm.setxy(evt);
    if(evt.preventDefault){
      evt.preventDefault();
    }
    removetooltips();
    $('div.slideoutcontents').hide('fast');
    document.body.style.cursor='move';
    gm.mouseorigin = getcurxy(evt);
    mousedown = true;
  }); 

  $('#mapdiv').mousemove(function(evt) { 
    if(evt.preventDefault){
      evt.preventDefault();
    }             
    gm.setxy(evt);
    gm.dohover(evt);

    if(mousedown === true){
      mousecounter++;
      if(mousecounter%3 === 0){
        killmenu();
        permanenttabs.temphidetabs();
        transienttabs.temphidetabs();
        var neworigin = getcurxy(evt);
        
        var dx = (gm.mouseorigin.x - neworigin.x);
        var dy = (gm.mouseorigin.y - neworigin.y);
        gm.panmap(dx,dy);
        gm.mouseorigin = neworigin;
        gm.resetmap();
      }
    }
    routebuilder.update(evt);
  });
  $('#mapdiv').mouseup(function(evt) { 
    gm.setxy(evt);
    if(evt.preventDefault){
      evt.preventDefault();
    }
    if(evt.detail===2){
      var cxy = getcurxy(evt);
      gm.zoom(evt,"-",cxy);
      killmenu();
    } else if ((!routebuilder.active())&&
               (!currouteid)&&(!curplanetid)&&(!curfleetid)&&(!curarrowid)&&
               (!transienttabs.isopen())&&
               (!permanenttabs.isopen())&&
               ($('#menu').css('display') == 'none')&&
               (mousecounter < 3)){
      buildmenu();    
      handlemenuitemreq(evt, '/map/root/');
    } else if((!routebuilder.active())&&
               (!currouteid)&&(!curplanetid)&&(!curfleetid)&&(!curarrowid)&&
               ($('#menu').css('display') == 'none')&&
               (mousecounter < 3)){
      permanenttabs.hidetabs();
      transienttabs.hidetabs();
    } else if($('#menu').css('display') != 'none'){
      killmenu();
    } else if((curarrowid)&&(!curplanetid)&&(!currouteid)&&(!curfleetid)){
      gm.mouseorigin = getcurxy(evt);
      gm.eatmouseclick(evt);
      curarrowid=0;
    }

    document.body.style.cursor='default';
    mousedown = false;
    if((!curfleetid)&&(!currouteid)&&(!curplanetid)&&(!curarrowid)&&(routebuilder.active())&&(mousecounter<3)){
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
    var dosectors = gm.viewablesectors();
    gm.getsectors(dosectors,0);
    gm.adjustview(dosectors);
  
  });

  function resizewindow() { 
    gm.resize();
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
        until: "+"+(3500+Math.floor(Math.random()*600)), format: 'hms',
        expiryUrl: "/view/"
      });
    }
  });
  
}



function expandtoggle(id)
{
  if($(id).attr('src') === '/site_media/expandup.png'){
    $(id).attr('src', '/site_media/expanddown.png');
  } else {
    $(id).attr('src', '/site_media/expandup.png');
  }
}




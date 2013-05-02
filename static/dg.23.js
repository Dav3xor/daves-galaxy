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
var buttoncounter = 1000;
var transienttabs;
var permanenttabs;
var buildanother = 0;
var currentbuildplanet = "";
var planetlistresource = 0;
var tradearrow = [[ 0.0, -0.0],
                  [-0.5, -.25],
                  [-0.5, -.3],
                  [-0.3, -.3],
                  [-0.3, -.5],
                  [ 0.3, -.5],
                  [ 0.3, -.3],
                  [ 0.5, -.3],
                  [ 0.5, -.25]];

var buttontypes = {
  'planetinfo':["handlebutton('planetmanagertab@counter', " +
                              "'planetmanager@counter', " +
                              "'planetinfotab@id', " +
                              "'ManagePlanet', " +
                              "'/planets/@id/manager/0/', " +
                              "'/planets/@id/info/');",
                'infobutton','Planet Info','planetinfo'],
  'planetmanage':["handlebutton('planetmanagertab@counter', " +
                              "'planetmanager@counter', " +
                              "'planetmanagetab@id', " +
                              "'ManagePlanet', " +
                              "'/planets/@id/manager/1/', " +
                              "'/planets/@id/manage/');",
                  'manage','Manage Planet','planetmanage'],
  'planetupgrade':["handlebutton('planetmanagertab@counter', " +
                              "'planetmanager@counter', " +
                              "'planetupgradestab@id', " +
                              "'ManagePlanet', " +
                              "'/planets/@id/manager/3/', " +
                              "'/planets/@id/manage/');",
                  'upgradebutton','Manage Upgrades','planetupgrade'],
  'fleetinfo':["loadtooltip('#fleetinfo@counter','/fleets/@id/info/','click');",
               'infobutton','Fleet Info', 'fleetinfo'],
  'fleetbuild':["handlebuildbutton(@id)",
                'construct','Construct Fleet','planetbuildfleet'],
  'fleetscrap':["sendrequest(handleserverresponse," +
                             "'/fleets/@id/scrap/'," +
                             "'GET');",
                'scrap', 'Scrap Fleet', 'fleetscrap']
                
                
                
                };

var curfleetid = 0;
var curplanetid = 0;
var currouteid = 0;
var curarrowid = 0;
var curslider = "";

var gm;
var pumenu;

function HTMLEncode(str){
  var i = str.length,
      aRet = [];

  while (i--) {
    var iC = str[i].charCodeAt();
    if (iC < 65 || iC > 127 || (iC>90 && iC<97)) {
      aRet[i] = '&#'+iC+';';
    } else {
      aRet[i] = str[i];
    }
   }
  return aRet.join('');    
}

// ye-olde fisher-yates, cribbed from
// http://stackoverflow.com/questions/962802/is-it-correct-to-use-javascript-array-sort-method-for-shuffling
function shuffle(array) {
    var tmp, current, top = array.length;

    if(top) while(--top) {
    	current = Math.floor(Math.random() * (top + 1));
    	tmp = array[current];
    	array[current] = array[top];
    	array[top] = tmp;
    }

    return array;
}

function getFunction(f, value) { return function(){f.apply(null, value);}; } 

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

function PopUpMenu()
{
  this.menu = $('#menu');
  this.x = 0;
  this.y = 0;
  this.hide = function(){
    this.menu.hide('fast');
  }
  this.ishidden =function(){
    return $('#menu').css('display') == 'none';
  }
  this.setlocation = function(x,y) {
    this.x = x;
    this.y = y;
  }
  this.waiting = function() {
    this.menu.html('<div><img src="/site_media/ajax-loader.gif">loading...</img></div>');
  }
  this.set = function(contents) {
    this.menu.hide('fast');
    this.menu.html(contents);
    setTimeout(function () {
      var cx = pumenu.x +30;
      var cy = pumenu.y +30;
      if (pumenu.menu.height() + pumenu.y > $(window).height() - 90) {
        cy = Math.max(30, pumenu.y - pumenu.menu.height() - 30);
      }
      if (pumenu.menu.width() + pumenu.x > $(window).width() - 200) {
        cx = Math.max(10, pumenu.x - pumenu.menu.width() - 30);
      }
      pumenu.menu.attr('style','position:absolute; top: '+ cy +
                           'px; left:'+ cx + 'px;');
      pumenu.menu.show('fast');
    },200);
  } 
}
function JobQueue()
{
  var pqself = this;
  this.queue = [];
  this.stopped = true;
  this.timer = 0;
  this.addjob = function(job,args) {
    // haha, closures...
    var func = getFunction(job, args);

    this.queue.push(func);
    if(this.stopped){
      this.start();
    }
  }
  this.runqueue = function() {
    if (this.queue.length > 0){
      var job = this.queue.shift();
      job();
      //setstatusmsg(this.queue.length);
      if(this.queue.length == 0){
        clearInterval(this.timer);
        this.stopped = true;
        //setstatusmsg("stopped");
      }
    }
  }
  this.start = function() {
    if(this.stopped){
      this.timer = setInterval(function(){pqself.runqueue()},500);
      this.stopped = false;
    }
  }
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
  
  this.gwidth = 3000.0;
  this.gheight = 3000.0;
  this.gmidx = this.gwidth/2.0;
  this.gmidy = this.gheight/2.0;
  
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
  this.planets          = [];
  this.fleets           = [];
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

  this.sendsectorrequest = function (getsectors,getnamedroutes) {
    var submission = {};
    for (sector in getsectors) {
      submission[getsectors[sector]] = 1;
    }

    if(getnamedroutes){
      submission.getnamedroutes="yes";
    }
    sendrequest(handleserverresponse,"/sectors/",'POST',submission);
    setstatusmsg("Requesting Sectors");
  }
  
  this.getsectors = function(newsectors,force,getnamedroutes)
  {
    var submitsectors = [];
    var sector = 0;
    this.sectorgeneration++;

  

    //newsectors = shuffle(newsectors);
    // convert newsectors (which comes in as a straight array)
    // over to the loaded sectors array (which is associative...)
    // and see if we have already asked for that sector (or indeed
    // already have it in memory, doesn't really matter...)
    for (sector in newsectors){
      if((force===1)||(!(sector in this.sectorsstatus))){
        this.sectorsstatus[sector] = this.sectorgeneration;
        submitsectors.push(sector);
      }
    }
    if(submitsectors.length > 0) {  
      var start = 0;
      var atatime = 20;
      submitsectors = shuffle(submitsectors);
      while(start < submitsectors.length) {
        var numtoget = Math.min(atatime,submitsectors.length-start);
        var end = start+numtoget;
        var sectorslice = submitsectors.slice(start,end);
        
        jq.addjob(gm.sendsectorrequest,[sectorslice,getnamedroutes]);
        start += numtoget;
      }
    }

  }

  this.adjustview = function(viewable)
  {
    var key;
    

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
          buildsectornebulae(sector,newsectorl1);
          buildsectorfleets(sector,newsectorl1,newsectorl2);
          buildsectorplanets(sector,newsectorl1, newsectorl2);
          buildsectorconnections(sector,newsectorl1,newsectorl2);

          gm.maplayer1.appendChild(newsectorl1);
          gm.maplayer2.appendChild(newsectorl2);
        }
      }
    }
    buildnamedroutes();
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
          if ('nebulae' in response.sectors[sector]){
            response.sectors[sector].nebulae = eval('('+response.sectors[sector].nebulae+')');
          }
          if ('planets' in response.sectors[sector]){
            var planetids = [];
            for(planet in response.sectors[sector].planets){
              planet = response.sectors[sector].planets[planet]
              this.planets[planet[gm.pd.id]] = planet;
              planetids.push(planet[gm.pd.id]);
            }
            response.sectors[sector].planets = planetids;
          }
          if ('fleets' in response.sectors[sector]){
            var fleetids = [];
            for(fleet in response.sectors[sector].fleets){
              fleet = response.sectors[sector].fleets[fleet]
              this.fleets[fleet[gm.fd.id]] = fleet;
              fleetids.push(fleet[gm.fd.id]);
            }
            response.sectors[sector].fleets = fleetids;
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


    gm.youarehere.setAttribute('x',-1000);
    gm.youarehere.setAttribute('y',-1000);
          

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
  
  this.gettabhsr = function(tab, newurl){
    tabs[tab] = newurl;
    sendrequest(handleserverresponse,
                newurl, 'GET');
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
  contents += '    <tr><td colspan="2">';
  contents += '      <input tabindex="1" maxlength="'+args.maxlen+'" type="text" value="' + HTMLEncode(args.text) + '" id="' + stringid +'" />';
  contents += '    </td></tr>';
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
  
  var angle1 = Math.atan2(gm.gmidx-miny,gm.gmidy-minx);
  var angle2 = Math.atan2(gm.gmidx-miny,gm.gmidy-maxx);
  var angle3 = Math.atan2(gm.gmidx-maxy,gm.gmidy-minx);
  var angle4 = Math.atan2(gm.gmidx-maxy,gm.gmidy-maxx);
  
  var distance1 = getdistance(gm.gmidx,gm.gmidy,minx,miny);
  var distance2 = getdistance(gm.gmidx,gm.gmidy,maxx,miny);
  var distance3 = getdistance(gm.gmidx,gm.gmidy,minx,maxy);
  var distance4 = getdistance(gm.gmidx,gm.gmidy,maxx,maxy);
 
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
        ring.setAttribute('cx',gm.tx(gm.gmidx));
        ring.setAttribute('cy',gm.ty(gm.gmidy));
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
        var startx = gm.tx(gm.gmidx-Math.cos(minangle)*i*20);
        var starty = gm.ty(gm.gmidy-Math.sin(minangle)*i*20);
        var endx =   gm.tx(gm.gmidx-Math.cos(maxangle)*i*20);
        var endy =   gm.ty(gm.gmidy-Math.sin(maxangle)*i*20);
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
      radial.setAttribute('x1', gm.tx(gm.gmidx-Math.cos(angle)*startdistance));
      radial.setAttribute('y1', gm.ty(gm.gmidy-Math.sin(angle)*startdistance));
      radial.setAttribute('x2', gm.tx(gm.gmidx-Math.cos(angle)*
                                 (maxdistance+(maxdistance-mindistance))));
      radial.setAttribute('y2', gm.ty(gm.gmidy-Math.sin(angle)*
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
    if (gm.zoomlevel < 6) {
      route.setAttribute('onmouseover',
                          'routehoveron(evt,"'+r+'")');
      route.setAttribute('onmouseout',
                          'routehoveroff(evt,"'+r+'")');
      route.setAttribute('onclick',
                          'doroutemousedown(evt,"'+r+'")');
    }
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

function buildsectornebulae(sector,sectorl1)
{
  function drawnebulae(nebulae, color, opacity)
    {
    for (var i=0; i < nebulae.length; i++){
      for (var j=0; j < nebulae[i].length; j++){
        if(j>0)continue; // skip holes, they're crap (remove later)
        var points = "";
        var poly = document.createElementNS(svgns, 'polygon');
        for (var k=0; k < nebulae[i][j].length; k+=2){
          points += gm.tx(nebulae[i][j][k]) + "," + gm.ty(nebulae[i][j][k+1]) + " ";
        }
        poly.setAttribute('fill', color);
        poly.setAttribute('stroke','none');
        poly.setAttribute('fill-opacity', opacity);
        poly.setAttribute('points', points);
        sectorl1.appendChild(poly);
      }
    }
  }
  if ('nebulae' in sector){
    var nebulae = sector.nebulae;  
    if ('1' in nebulae){
      drawnebulae(nebulae['1'],'#AA7755',.25) 
    }
    if ('2' in nebulae){
      drawnebulae(nebulae['2'],'#AA7755',.1) 
    }

  }
}
    

function buildsectorfleets(sector,newsectorl1,newsectorl2)
{
  var fleetkey=0;
  var fleet;
  var circle = 0;
  var group = 0;
  var sensegroup = 0;
  var sensecircle = 0;
  var marker = 0;
  var line = 0;

  
  for(fleetkey in sector.fleets){
    if(typeof fleetkey === 'string'){
      fleet = gm.fleets[sector.fleets[fleetkey]];
      var id = fleet[gm.fd.id];
      var flags = fleet[gm.fd.flags];
      var x = fleet[gm.fd.x];
      var y = fleet[gm.fd.y];
      var x2 = fleet[gm.fd.dx];
      var y2 = fleet[gm.fd.dy];
      var owner = fleet[gm.fd.owner_id];
      var route = fleet[gm.fd.route_id];
      var gid = 'gf'+id;
      var playerowned;
      var color = gm.playercolors[owner][0];
      if (fleet[gm.fd.owner_id] == gm.player_id){
        playerowned=1;
      } else {
        playerowned=0;
      }
      group = document.createElementNS(svgns, 'g');
      group.setAttribute('fill', color);
      group.setAttribute('id', gid);
      group.setAttribute('stroke', color);
      group.setAttribute('stroke-width', '.01');
      if (gm.zoomlevel < 6) {
        group.setAttribute('onmouseover',
                           'fleethoveron(evt,"'+id+'",'+x+','+y+');');
        group.setAttribute('onmouseout', 
                           'fleethoveroff(evt,"'+id+'")');
        group.setAttribute('onclick', 
                           'dofleetmousedown(evt,"'+id+'",'+playerowned+')');
      }
      if (route){
        if(!buildroute(route, newsectorl1, color)){
          //delete fleet.r;
        }
      } 
      if (fleet[gm.fd.sensorrange]>0){
        sensegroup = document.getElementById("sg-"+owner);
        if(!sensegroup){
          sensegroup = document.createElementNS(svgns,'g');
          sensegroup.setAttribute('fill',color);
          sensegroup.setAttribute('id','sg-'+owner);
          sensegroup.setAttribute('opacity','.3');
          gm.maplayer0.appendChild(sensegroup);
        }
        sensecircle = document.createElementNS(svgns, 'circle');
        sensecircle.setAttribute('cx', gm.tx(x));
        sensecircle.setAttribute('cy', gm.ty(y));
        sensecircle.setAttribute('r', gm.td(fleet[gm.fd.sensorrange]));
        sensegroup.appendChild(sensecircle);
      }

      if ((x2 != x)&&(y2 != y)&&(x2 != undefined)&&(y2 != undefined)){
        marker = document.getElementById("marker-"+color.substring(1));
        if(!marker){
          marker = buildmarker(color);
        }

        points = ""
        line = document.createElementNS(svgns,'polyline');

        var vlength = getdistance(x,y,x2,y2);
        if (vlength > .4) {
          var vangle = Math.atan2(y-y2,x-x2);
          x2 =  x2+(Math.cos(vangle)*0.3);
          y2 =  y2+(Math.sin(vangle)*0.3);
        }






        points += gm.tx(x)+","+gm.ty(y)+" "+gm.tx(x2)+","+gm.ty(y2);
        if (route) {
          var circular = gm.routes[route].c;
          var routepoints = gm.routes[route].p;
          if (routepoints[fleet[gm.fd.curleg]].length===2) {
            points += " " + 
                      gm.tx(routepoints[fleet[gm.fd.curleg]][0]) + "," + 
                      gm.ty(routepoints[fleet[gm.fd.curleg]][1]);
          } else if (routepoints[fleet[gm.fd.curleg]].length===3) {
            points += " " + 
                      gm.tx(routepoints[fleet[gm.fd.curleg]][1]) + "," + 
                      gm.ty(routepoints[fleet[gm.fd.curleg]][2]);
          }
        }
        line.setAttribute('points',points);
        line.setAttribute('marker-end', 'url(#marker-'+color.substring(1)+')');
        line.setAttribute('stroke',color);
        line.setAttribute('fill','none');
        if((flags&gm.ff.scout)){  // scout
          if(gm.zoomlevel<5){
            line.setAttribute('stroke-dasharray',gm.td(0.09)+","+gm.td(0.09));
            line.setAttribute('opacity', .5);
          } else {
            line.setAttribute('opacity', .25);
          }
          line.setAttribute('stroke-width', .2 + gm.td(0.03));
        } else if((flags&gm.ff.colonization)) { // arc
          line.setAttribute('stroke-dasharray',gm.td(0.3)+","+gm.td(0.3));
          line.setAttribute('stroke-width', .2 + gm.td(0.03));
        } else if((flags&gm.ff.merchant)) { // merchant
          if(gm.zoomlevel<5){
            line.setAttribute('stroke-dasharray',gm.td(0.03)+","+gm.td(0.09));
            line.setAttribute('opacity', .7);
          } else {
            line.setAttribute('opacity', .35);
          }
          line.setAttribute('stroke-width', .2 + gm.td(0.04));
        } else if(flags&gm.ff.military) { // military
          line.setAttribute('stroke-width', .2 + gm.td(0.05));
        } else { // "other"
          line.setAttribute('stroke-width', .2 + gm.td(0.03));
        }


        group.appendChild(line);
        
      }
      if(flags&gm.ff.damaged) {
        // damaged
        circle = document.createElementNS(svgns, 'circle');
        circle.setAttribute('cx', gm.tx(x));
        circle.setAttribute('cy', gm.ty(y));
        circle.setAttribute('r', gm.td(0.2));
        circle.setAttribute('style','fill:url(#damagedfleet);');
        newsectorl1.appendChild(circle);
      } else if(flags&gm.ff.destroyed) {
        // destroyed
        circle = document.createElementNS(svgns, 'circle');
        circle.setAttribute('cx', gm.tx(x));
        circle.setAttribute('cy', gm.ty(y));
        circle.setAttribute('r', gm.td(0.2));
        circle.setAttribute('style','fill:url(#destroyedfleet);');
        newsectorl1.appendChild(circle);
      }
      // the fleet itself
      circle = document.createElementNS(svgns, 'circle');
      

      circle.setAttribute('fill', color);
      circle.setAttribute('cx', gm.tx(x));
      circle.setAttribute('cy', gm.ty(y));
      circle.setAttribute('r', gm.td(0.04));
      circle.setAttribute('or', gm.td(0.04));
      var cid = 'f'+id;
      circle.setAttribute('id', cid );
      
      if (flags&gm.ff.pirated) {
        // pirated
        var animation = document.createElementNS(svgns, 'animate');
        animation.setAttribute('attributeName','fill');
        animation.setAttribute('from',color);
        animation.setAttribute('to','white');
        animation.setAttribute('values',  'gray;gray;red;white');
        animation.setAttribute('keyTimes','0.0;0.95;.96;1.0');
        animation.setAttribute('dur','3.0');
        animation.setAttribute('repeatCount','indefinite');
        circle.appendChild(animation);
      }
      
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
      var planet    = gm.planets[sector.planets[planetkey]];
      var color     = '#FFFFFF';
      var x         = planet[gm.pd.x];
      var y         = planet[gm.pd.y];
      var owner     = planet[gm.pd.owner_id];
      var id        = planet[gm.pd.id];
      var r    = planet[gm.pd.r];
      var flags     = planet[gm.pd.flags];
      if(owner){
        color = gm.playercolors[owner][0];
      }
      
      var iscapital = ((owner in gm.playercolors)&&
                       (gm.playercolors[owner][1]==id)) ? true:false;
      // draw You Are Here and it's arrow if it's a new player
      if (((newplayer === 1) && (planet[gm.pd.owner_id] === gm.player_id))){
        if(((gm.ty(y) > 0)&&(gm.ty(y) < gm.screenheight))&&
           ((gm.tx(x) > 0)&&(gm.tx(x) < gm.screenwidth))){
          gm.youarehere.setAttribute('visibility','visible');
          gm.youarehere.setAttribute('font-size',gm.td(.2));
          gm.youarehere.setAttribute('x',gm.tx(x-1.5));
          gm.youarehere.setAttribute('y',gm.ty(y+1.3));
          line = document.createElementNS(svgns, 'line');
          line.setAttribute('stroke-width', gm.td(.03));
          line.setAttribute('stroke', '#ffffff');
          line.setAttribute('marker-end', 'url(#endArrow)');
          line.setAttribute('x2', gm.tx(x-0.2));
          line.setAttribute('y2', gm.ty(y+0.3));
          line.setAttribute('x1', gm.tx(x-0.7));
          line.setAttribute('y1', gm.ty(y+1.0));
          newsectorl2.appendChild(line);
        } else {
          gm.youarehere.setAttribute('visibility','hidden');
        }

      }
    
      // sensor range
      if ((planet[gm.pd.sensorrange])&&(planet[gm.pd.owner_id])){
        var opacity = .35 - ((gm.zoomlevel+1)/35.0);
        sensegroup = document.getElementById("sg-"+owner);
        if(!sensegroup){
          sensegroup = document.createElementNS(svgns,'g');
          sensegroup.setAttribute('id','sg-'+owner);
          sensegroup.setAttribute('fill',color);
          sensegroup.setAttribute('opacity',opacity);
          gm.maplayer0.appendChild(sensegroup);
        }
        circle = document.createElementNS(svgns, 'circle');
        circle.setAttribute('cx',  gm.tx(x));
        circle.setAttribute('cy',  gm.ty(y));
        circle.setAttribute('r',   gm.td(planet[gm.pd.sensorrange]));
        sensegroup.appendChild(circle);
      }
      if(flags&gm.pf.damaged) {
        // damaged
        circle = document.createElementNS(svgns, 'circle');
        circle.setAttribute('cx', gm.tx(x));
        circle.setAttribute('cy', gm.ty(y));
        circle.setAttribute('r', gm.td(r+.5));
        circle.setAttribute('style','fill:url(#damagedplanet);');
        newsectorl1.appendChild(circle);
      }

      // food problem
      if((flags&gm.pf.food_subsidy)||(flags&gm.pf.famine)){
        highlight = document.createElementNS(svgns, 'circle');
        radius = 0.12;
        if(iscapital){
          radius += 0.05;
        }
        highlight.setAttribute('cx', gm.tx(x));
        highlight.setAttribute('cy', gm.ty(y));
        highlight.setAttribute('r', gm.td(r+radius));
        if(flags&1){
          highlight.setAttribute('stroke', 'yellow');
        } else {
          highlight.setAttribute('stroke', 'red');
        }  
        highlight.setAttribute('fill', 'none');
        highlight.setAttribute('stroke-width', gm.td(0.035));
        newsectorl1.appendChild(highlight);
      }
      

      // rgl govt.
      if (flags&gm.pf.rgl_govt){
        highlight = document.createElementNS(svgns, 'circle');
        highlight.setAttribute('cx', gm.tx(x));
        highlight.setAttribute('cy', gm.ty(y));
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
        highlight.setAttribute('cx', gm.tx(x));
        highlight.setAttribute('cy', gm.ty(y));
        highlight.setAttribute('r', gm.td(4.0));
        var linelength = (gm.td(4.0) * Math.PI * 2.0)/50.0;
        if ((owner)&&('e'+owner in gm.enemies)){
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
      if ((planet[gm.pd.owner_id]===gm.player_id)&&(flags&gm.pf.farm_subsidies)){
        highlight = document.createElementNS(svgns, 'circle');
        radius = 0.16;
        if(iscapital){ // capital
          radius += 0.05;
        }
        if((flags&gm.pf.food_subsidy)||(flags&gm.pf.famine)){ // food scarcity
          radius += 0.05;
        }
        if (((flags&gm.pf.mattersynth1)||
             (flags&gm.pf.military_base)||
             (flags&gm.pf.matter_synth2))&&
             (gm.zoomlevel < 5)){
          radius += .1;
        }
        var linelength = (gm.td(radius+r) * Math.PI * 2.0)/12.0;
        highlight.setAttribute('cx', gm.tx(x));
        highlight.setAttribute('cy', gm.ty(y));
        highlight.setAttribute('r', gm.td(r+radius));
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
        if((flags&gm.pf.food_subsidy)||(flags&gm.pf.famine)){ // food scarcity
          radius += 0.05;
        }
        if (((flags&gm.pf.matter_synth1)||
             (flags&gm.pf.military_base)||
             (flags&gm.pf.matter_synth2))&&(gm.zoomlevel < 5)){
          radius += .1;
        }
        var linelength = (gm.td(radius+r) * Math.PI * 2.0)/12.0;
        highlight.setAttribute('cx', gm.tx(x));
        highlight.setAttribute('cy', gm.ty(y));
        highlight.setAttribute('r', gm.td(r+radius));
        highlight.setAttribute('stroke', 'yellow');
        highlight.setAttribute('fill', 'none');
        highlight.setAttribute('stroke-width', gm.td(0.07));
        highlight.setAttribute('stroke-opacity', .2);
        highlight.setAttribute('stroke-dasharray',linelength*.8+","+ linelength*.2);
        
        newsectorl1.appendChild(highlight);
      }

      // military circle
      if (((flags&gm.pf.matter_synth1)||
           (flags&gm.pf.military_base)||
           (flags&gm.pf.matter_synth2))&&(gm.zoomlevel < 5)){
        highlight = document.createElementNS(svgns, 'circle');
        radius = 0.12;
        if(iscapital){ // capital
          radius += 0.05;
        }
        if((flags&gm.pf.food_subsidy)||
           (flags&gm.pf.famine)){ // food scarcity
          radius += 0.05;
        }
        highlight.setAttribute('cx', gm.tx(x));
        highlight.setAttribute('cy', gm.ty(y));
        highlight.setAttribute('r', gm.td(r+radius));
        highlight.setAttribute('stroke', color);
        highlight.setAttribute('fill', 'none');
        highlight.setAttribute('stroke-width', gm.td(0.02));
        highlight.setAttribute('stroke-opacity', 0.4);
        var linelength = (gm.td(radius+planet.r) * Math.PI * 2.0)/35.0;
        highlight.setAttribute('stroke-dasharray',linelength*.5+","+linelength*.5);
      
        if(flags&gm.pf.matter_synth2){
          // matter synth 2
          highlight.setAttribute('stroke-width',gm.td(0.050));
        }
        if (flags&gm.pf.military_base) {
          // military base
          var linelength = (gm.td(radius+r) * Math.PI * 2.0)/10.0;
          highlight.setAttribute('stroke-dasharray',linelength*.75+","+linelength*.25);
        } 
       

        newsectorl1.appendChild(highlight);
      }
        

      // capital ring
      if (iscapital) {
        highlight = document.createElementNS(svgns, 'circle');
        highlight.setAttribute('cx', gm.tx(x));
        highlight.setAttribute('cy', gm.ty(y));
        highlight.setAttribute('r', gm.td(r+0.12));
        highlight.setAttribute('stroke', color);
        highlight.setAttribute('stroke-width', gm.td(0.02));
        newsectorl1.appendChild(highlight);
        
        // capital defense
        var capdef = document.createElementNS(svgns, 'circle');
        capdef.setAttribute('cx', gm.tx(x));
        capdef.setAttribute('cy', gm.ty(y));
        capdef.setAttribute('r', gm.td(1.5));
        capdef.setAttribute('stroke', 'red');
        capdef.setAttribute('fill', 'none');
        capdef.setAttribute('stroke-width', gm.td(0.02));
        capdef.setAttribute('stroke-dasharray',gm.td(0.09)+","+gm.td(0.09));
        newsectorl1.appendChild(capdef);
      } 

      // inhabited ring
      if (owner){
        highlight = document.createElementNS(svgns, 'circle');
        highlight.setAttribute('cx', gm.tx(x));
        highlight.setAttribute('cy', gm.ty(y));
        highlight.setAttribute('r', gm.td(r+0.06));
        highlight.setAttribute('stroke', color);
        highlight.setAttribute('stroke-width', gm.td(0.04));
        newsectorl2.appendChild(highlight);
      }
      circle = document.createElementNS(svgns, 'circle');
      circle.setAttribute("fill",planet[gm.pd.hexcolor]);
      circle.setAttribute("stroke",'none');
      var playerowned=0;
      if ('pp' in planet){
        playerowned=1;
      } else {
        playerowned=0;
      }
      // the star itself
      circle.setAttribute('id', 'p'+id);
      circle.setAttribute('cx', gm.tx(x));
      circle.setAttribute('cy', gm.ty(y));
      circle.setAttribute('ox', x);
      circle.setAttribute('oy', y);
      circle.setAttribute('r', gm.td(r));
      circle.setAttribute('or', gm.td(r));
      if (gm.zoomlevel < 6) {
        circle.setAttribute('onmouseover',
                            'planethoveron(evt,"'+id+'","'+x+'","'+y+'")');
        circle.setAttribute('onmouseout',
                            'planethoveroff(evt,"'+id+'")');
        circle.setAttribute('onclick',
                            'doplanetmousedown(evt,"'+id+'")');
      }
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
          planetkey = sector.planets[planetkey].toString();
          if(typeof planetkey === 'string'){
            var planet = gm.planets[planetkey];
            func(planet,fleet,sectorl1);
          }
        }
      }
    }
  }
}

function removearrow(planet,fleet,sectorl1)
{
  var arrow = document.getElementById("arrow-"+planet[gm.pd.id]);
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
  
  var flags = fleet[gm.fd.flags];
  var planetflags = planet[gm.pd.flags];

  if (flags&gm.ff.scout){
    return;
  }
  if (flags&gm.ff.military){
    if (!(planet[gm.pd.owner_id])){
      return;
    }
    if (!('e'+planet[gm.pd.owner_id] in gm.enemies)){
      return;
    }
    color = 'orange';
  }

  // trade
  if (flags&gm.ff.merchant){
    if(!((planetflags&gm.pf.open_trade)||
         (planet[gm.pd.owner_id]===gm.player_id))){
      return;
    }
  }

  //arc
  if (flags&gm.ff.colonization){
    if((planet[gm.pd.owner_id])&&(planet[gm.pd.owner_id] != fleet[gm.fd.owner_id])){
      return;
    }
    if(planet[gm.pd.resourcelist][gm.md.people] > 10000){
      return;
    }
  }
    
  var arrow = document.createElementNS(svgns, 'polygon');
  var arrowid = "arrow-"+planet[gm.pd.id];
  var angle = (3.14159/2.0)+Math.atan2(fleet[gm.fd.y]-planet[gm.pd.y],
                                       fleet[gm.fd.x]-planet[gm.pd.x]);
  var points = "";
  var poly = [];
  var x = 0.0;
  var y = 0.0;
  var yoff = 0.0;
  bbox = [10000,10000,-10000,-10000];
  for (i in tradearrow){
    yoff = tradearrow[i][1] - planet[gm.pd.r] - .2 
    x = gm.tx(planet[gm.pd.x] + tradearrow[i][0]*Math.cos(angle) - yoff*Math.sin(angle));
    y = gm.ty(planet[gm.pd.y] + tradearrow[i][0]*Math.sin(angle) + yoff*Math.cos(angle));
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
    'mouseover' :function(evt){arrowmouseover(evt,
                                              arrowid,
                                              planet,
                                              fleet[gm.fd.owner_id]==gm.player_id);},
    'mouseout'  :function(evt){arrowmouseout(arrowid);},
    'action'    :function(evt){doplanetmousedown(evt,
                                                 planet[gm.pd.id]);}
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
          

function getfleet(fleetid)
{
  if (fleetid in gm.fleets){
    return gm.fleets[fleetid];
  } else {
    return false;
  }
}

function getplanet(planetid)
{
  if (planetid in gm.planets){
    return gm.planets[planetid];
  } else {
    return false;
  }
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
    this.curfleet = fleet;
    // build goto arrows
    if(gm.zoomlevel<5){
      inviewplanets(buildarrow,this.curfleet);
      gm.dohover({pageX:gm.mousepos.x, pageY:gm.mousepos.y});
    }
    pumenu.hide();
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
    this.startrouteto(-1, loc, 
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

  this.startrouteto = function (fleet, loc, circular, planetid)
  {
    this.startcommon(fleet);
    this.route = [];
    var startx = 0.0;
    var starty = 0.0;
    if(fleet == -1){
      startx = loc.x;
      starty = loc.y;
    } else {
      startx = fleet[gm.fd.x];
      starty = fleet[gm.fd.y];
    }



    if (planetid != -1){
      this.route.push([startx,starty,planetid]);
    } else {
      this.route.push([startx,starty]);
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
    this.route[0] = [fleet[gm.fd.x],fleet[gm.fd.y]];
    var coords = gm.tx(fleet[gm.fd.x])+","+gm.ty(fleet[gm.fd.y])+" "+
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

  this.finish = function(evt,planetid)
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
      if(planetid){
        request = "/fleets/"+this.curfleet[gm.fd.id]+"/movetoplanet/";
        submission.planet=planetid;
      } else {
        request = "/fleets/"+this.curfleet[gm.fd.id]+"/movetoloc/";
        submission.x = curloc.x;
        submission.y = curloc.y;
      }

    } else {
      request = "/fleets/"+this.curfleet[gm.fd.id]+"/routeto/";
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
                      '/fleets/'+routebuilder.curfleet[gm.fd.id]+'/scrap/',
                      'POST');
        }
        routebuilder.cancel();
          
        buildanother = 0;
        return false;
      } else {
        transienttabs.hidetabs();
        permanenttabs.hidetabs();
        pumenu.hide();
      }
    } else if ((evt.keyCode === 61)||
               (evt.keyCode === 107)||
               (evt.keyCode === 187)) {    // +/=  (zoom in)
      gm.zoommiddle(evt,'-');
    } else if ((evt.keyCode === 109)||
               (evt.keyCode === 189)||
               (evt.keyCode === 173)||
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
function arrowmouseover(evt,arrowid,planet,foreign)
{
  var arrow = document.getElementById(arrowid);
  if(arrow){
    arrow.setAttribute('fill-opacity', '.3');
    arrow.setAttribute('stroke-opacity', '.4');
    var statusmsg = "<h1>"+planet[gm.pd.name]+"</h1>";
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

function planethoveron(evt,planet,x,y)
{
  var planet    = getplanet(planet)
  var owner     = planet[gm.pd.owner_id]
  var id        = planet[gm.pd.id]
  var flags     = planet[gm.pd.flags];
  var iscapital = ((owner in gm.playercolors)&&
                   (gm.playercolors[owner][1]==id)) ? true:false;
  var status =  "<h1>"+planet[gm.pd.name]+"</h1>"+
                "<table>"+
                "<tr>"+
                "  <td class='rowheader'>Population:</td>"+
                "  <td class='rowitem'>"+planet[gm.pd.resourcelist][gm.md.people]+"</td>"+
                "</tr>"+
                "<tr>"+
                "  <td class='rowheader'>Society:</td>"+
                "  <td class='rowitem'>"+planet[gm.pd.society]+"</td>"+
                "</tr>"
  if(iscapital){
      status += "<tr><td class='rowheader'>Point of Interest:</td><td class='rowitem'>Capital</td></tr>";
  }
  if(flags&gm.pf.open_trade){
      status += "<tr><td class='rowheader'>Foreign Trade:</td><td class='rowitem'>Yes</td></tr>";
  }
  if(flags&gm.pf.damaged){
      status += "<tr><td class='rowheader'>Status:</td><td class='rowitem'>Under Attack!</td></tr>";
  }
  if(flags&gm.pf.famine){
      status += "<tr><td class='rowheader'>Emergency:</td><td class='rowitem'>Famine Conditions</td></tr>";
  } else if(flags&gm.pf.food_subsidy){
      status += "<tr><td class='rowheader'>Warning:</td><td class='rowitem'>Emergency Food Subsidies Active</td></tr>";
  }
      status += "</table><hr/>"+
                "<div style='padding-left:10px; font-size:10px;'>"
  if(routebuilder.active()){
      status += "Left Click to Send Fleet to Planet";
  } else {
      status += "Left Click to Manage Planet";
  }
      status += "</div>";
  setstatusmsg(status);

  document.body.style.cursor='pointer';
  gm.setxy(evt);
  zoomcircleid(2.0,"p"+id);
  curplanetid = id;
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
  pumenu.setlocation(gm.mousepos.x,gm.mousepos.y);
  if ((routebuilder.curfleet)&&(routebuilder.active())){
    // routeid, x, y, leg   
    var newroute = {};
    newroute.route = route;
    newroute.sx = gm.mousepos.mapx;
    newroute.sy = gm.mousepos.mapy;
    ontonamedroute(routebuilder.curfleet[gm.fd.id], newroute);
    routebuilder.cancel();
  } else if (!routebuilder.active()) {
    handlemenuitemreq(evt, '/routes/'+route+'/root/');
  }
}

function fleethoveron(evt,fleetid,x,y)
{
  fleet      = getfleet(fleetid);
  flags      = fleet[gm.fd.flags];
  id         = fleet[gm.fd.id];
  curfleetid = fleetid;
  about      = "<h3>Fleet:</h3><table>";
  if (fleet[gm.fd.name]){
    about += "<tr><td>Name:</td><td>"+fleet[gm.fd.name]+"</td></tr>";  
  }
  about += "<tr><td>Id:</td><td>"+fleet[gm.fd.id]+"</td></tr>";  
    
  about += "<tr><td>Society:</td><td>"+fleet[gm.fd.society]+"</td></tr>";

  if (fleet[gm.fd.destination_id]) {
    var planet = getplanet(fleet[gm.fd.destination_id]);
    if(planet){
      about += "<tr><td>Destination:</td><td>"+planet[gm.pd.name]+" ("+planet[gm.pd.id]+")</td></tr>";
    } else {
      about += "<tr><td>Destination:</td><td>"+fleet[gm.fd.destination_id] + "(planet)</td></tr>";
    }
  } else if ((fleet[gm.fd.x] != fleet[gm.fd.x2]) || (fleet[gm.fd.y] != fleet[gm.fd.y2])){
    about += "<tr><td>Destination:</td><td>"+fleet[gm.fd.x].toFixed(1)+","+fleet[gm.fd.y].toFixed(1)+" (location)</td></tr>";
  } 

  about+="<tr><td colspan='3'><hr/></td></tr>";
  if (flags & gm.ff.damaged){
    about += "<tr><td>Status:</td><td><div style='color:yellow;'>Damaged</div></td></tr>";
  }
  if (flags & gm.ff.destroyed){
    about += "<tr><td>Status:</td><td><div style='color:red;'>Destroyed</div></td></tr>";
  }

  var headerprinted=false;
  for(var i=0;i<fleet[gm.fd.shiplist].length;i++){
    if(fleet[gm.fd.shiplist][i] > 0){
      if (!headerprinted) {
        about += "<tr><td colspan='2'>Composition:</td></tr>";
        headerprinted = true;
      }
      about += "<tr><td/><td style='font-size:smaller'>"+gm.sa[i]+"</td><td>"+fleet[gm.fd.shiplist][i]+"</td></tr>";
    }
  }



  about += "</table>";
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



function handleserverresponse(response)
{
  var id,title,content;
  if ('menu' in response){
    pumenu.set(response.pagedata);
  }

  if(('protocolversion' in response)&&(response.protocolversion != protocolversion)){
    $('#protocolwarning').show()
  }
    
  if('transient' in response){
    id = response.id;
    title = response.title;
    content = response.pagedata;
    pumenu.hide();
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
    pumenu.hide();
    permanenttabs.settabcontent(id, content);
  }

  if ('showcountdown' in response){
    if (response.showcountdown === true){
      $('#countdown').show();
    } else {
      $('#countdown').hide();
    }
  }

  if ('planetlist' in response){
    loadplanetlist(response['planetlist'],response['commodities']);
  }    

  if ('fleetlist' in response){
    loadfleetlist(response['fleetlist'],response['shiptypes']);
  }    
  
  if ('killmenu' in response){
    pumenu.hide();
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
      pumenu.hide();
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
  pumenu.hide();
  sendrequest(handleserverresponse, request,'GET','');
  curslider = slider;
}


function sendform(subform,request)
{
  var submission = buildform(subform);
  sendrequest(handleserverresponse,request,'POST',submission);
  $('#window').hide();
  pumenu.waiting();
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
function handlebuildbutton(id){
  if(!transienttabs.alreadyopen('buildfleet'+id)){
    transienttabs.pushtab('buildfleet'+id,'Build Fleet','',false);
    transienttabs.gettaburl('buildfleet'+id,
                            '/planets/'+id+'/buildfleet/');
    transienttabs.displaytab('buildfleet'+id);
  } else {
    transienttabs.removetab('buildfleet'+id);
  }
}

    
function handlemenuitemreq(event, url)
{
  prevdef(event);
  pumenu.waiting();
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
    pumenu.setlocation(gm.mousepos.x,gm.mousepos.y);
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
    pumenu.setlocation(gm.mousepos.x,gm.mousepos.y);
    handlemenuitemreq(evt, '/planets/'+planet+'/root/');
  } 
}

function makebutton(type,id)
{
  var buttonfunction = buttontypes[type][0].replace(/@counter/g,buttoncounter)
  buttonfunction = buttonfunction.replace(/@id/g, id);
  var button = makebuttonfn(buttontypes[type][3],buttontypes[type][2],
                            buttontypes[type][1],
                            buttonfunction);
  return button;
                      
}

function makebuttonfn(name,title,img,fn)
{
  var button  = "<img class='noborder' title='" + title + "'";
      button += "     id='" + name + buttoncounter + "'"
      button += "     src='/site_media/" + img + ".png'";
      button += '     onclick = "' + fn + '"';
      button += '/>';
  buttoncounter = (buttoncounter+1)%64768;
  return button;
}

function loadfleetlist(fleetlist,shiptypes)
{
  for (fleet_index in fleetlist){
    var fleet = fleetlist[fleet_index];
    if(!(fleet[gm.fd.id] in gm.fleets)){
      gm.fleets[fleet[gm.fd.id]] = fleet;
    }
  }
  permanenttabs.settabcontent('fleetslist', '<table id="fleetlisttable"></table>') 
 	$('#fleetlisttable').dataTable( {
    "bDeferRender": true,
    "sPaginationType": "full_numbers",
    "aaData": fleetlist,
    "aoColumns": [
			{ "sTitle": "" },
			{ "sTitle": "" },
			{ "sTitle": "ID" },
			{ "sTitle": "Name" },
			{ "sTitle": "Ships" },
			{ "sTitle": "Disposition" },
			{ "sTitle": "Att." },
			{ "sTitle": "Def." },
      { "sTitle": "Scrap" },
			{ "sTitle": "" },
			{ "sTitle": "" },
			{ "sTitle": "" }
    ],
		"aoColumnDefs": [ 
      { "mRender": function(data,type,row) {
          return makebutton('fleetinfo',row[gm.fd.id]);
        },
        "bSortable": false,
        "aTargets": [0]
      },
      { "mRender": function(data,type,row) {
          return makebuttonfn('centerfleet',
                              'Center on Fleet',
                              'center',
                              'gm.centermap('+row[gm.fd.x]+', '+row[gm.fd.y]+');');
        },
        "bSortable": false,
        "aTargets": [1]
      },
			{ "mData": gm.fd.id, "aTargets": [2] },
			{ "mData": gm.fd.name, "aTargets": [3] },
      { "mRender": function(data,type,row) {
          var count = 0;
          for (i in row[gm.fd.shiplist]){count += row[gm.fd.shiplist][i]}
          return count;
        },
        "aTargets":[4]
      },
			{ "mData": gm.fd.disposition, "aTargets": [5] },
      { "mRender": function(data,type,row) {
          var count = 0;
          for (var i in row[gm.fd.shiplist]){count += row[gm.fd.shiplist][i]*shiptypes[i][1]}
          return count;
        },
        "aTargets":[6]
      },
      { "mRender": function(data,type,row) {
          var count = 0;
          for (var i in row[gm.fd.shiplist]){count += row[gm.fd.shiplist][i]*shiptypes[i][2]}
          return count;
        },
        "aTargets":[7]
      },
      { "mRender": function(data,type,row) {
          if(row[gm.fd.flags]&gm.ff.inport){
            if (type === 'display'){
              return makebutton('fleetscrap',row[gm.fd.id]);
            } else {
              return 'a';
            }
          } else {
            if (type === 'display'){
              return ""
            } else {
              return 'b';
            }
          }
        },
        "aTargets": [8]
      },
      { "mRender": function(data,type,row) {
          if(row[gm.fd.homeport_id]){
            var home = getplanet(row[gm.fd.homeport_id]);
            if(home){
              return makebuttonfn('centerplanet',
                                'Center on Home Port',
                                'center',
                                'gm.centermap('+home[gm.pd.x]+', '+home[gm.pd.y]+');');
            }
          }
          return "";
        },
        "bSortable": false,
        "aTargets": [9]
      },
      { "mRender": function(data,type,row) {
          if(row[gm.fd.homeport_id]){
            var src = getplanet(row[gm.fd.source_id]);
            if(src){
              if (type === 'display'){
                return makebuttonfn('centerplanet',
                                  'Center on Source Port',
                                  'center',
                                  'gm.centermap('+src[gm.pd.x]+', '+src[gm.pd.y]+');');
              } else {
                return 'a';
              }
            } else {
              if (type === 'display'){
                return ""
              } else {
                return 'b';
              }
            }
          }
          return "";
        },
        "aTargets": [10]
      },
      { "mRender": function(data,type,row) {
          if((row[gm.fd.x] != row[gm.fd.dx])||(row[gm.fd.y] != row[gm.fd.dy])){
            if (type === 'display'){
              return makebuttonfn('centerplanet',
                                'Center on Destination',
                                'center',
                                'gm.centermap('+row[gm.fd.dx]+', '+row[gm.fd.dy]+');');
            } else {
              return 'a';
            }
          } else {
              if (type === 'display'){
                return "";
              } else {
                return 'b';
              }
            }
          return "";
        },
        "aTargets": [11]
      }
    ]
  } );
}
function changeresourcecolumn(obj)
{
  resource = obj.value;
  planetlistresource = gm.md[resource];
  var table = $('#planetlisttable').dataTable()
  var rows = table.fnSettings().aoData;      
  for(var i = 0; i < rows.length; i++){
    var newval = rows[i]._aData[gm.pd.resourcelist][gm.md[resource]];
    table.fnUpdate(newval, i, 6, false, false);
  }  
  $('#planetlisttable').dataTable().fnDraw();
}
function loadplanetlist(planetlist,commodities)
{
  for (planet_index in planetlist){
    var planet = planetlist[planet_index];
    if(!(planet[gm.pd.id] in gm.planets)){
      gm.planets[planet[gm.pd.id]] = planet;
    }
  }
  var resourcelist    = "<span><select onchange='changeresourcecolumn(this)'>"
  for (res in gm.md){
    resourcelist     += "<option value='"+res+"' ";
    if(res==='people'){
      resourcelist   += "selected='true' ";
    }
    resourcelist     += ">"+res+"</option>";
  }
  resourcelist       += "</select></span>";

  permanenttabs.settabcontent('planetslist', '<table id="planetlisttable"></table>') 
 	$('#planetlisttable').dataTable( {
    "bDeferRender": true,
    "sPaginationType": "full_numbers",
    "bAutoWidth": false,
    "aaData": planetlist,
    "aoColumns": [
			{ "sTitle": "", "sWidth": "10px" },
			{ "sTitle": "", "sWidth": "10px" },
			{ "sTitle": "", "sWidth": "10px" },
			{ "sTitle": "", "sWidth": "10px" },
			{ "sTitle": "Name", "sWidth": "200px" },
			{ "sTitle": "Society", "sWidth": "50px" },
			{ "sTitle": resourcelist, "sWidth": "200px" },
			{ "sTitle": "Tax", "sWidth": "30px" },
			{ "sTitle": "Tariff", "sWidth": "30px" },
			{ "sTitle": "", "sWidth": "10px" },
    ],
		"aoColumnDefs": [ 
			{
				"mRender": function (data, type, row) {
          return makebutton('planetinfo',row[gm.pd.id]);
				},
        "bSortable": false,
				"aTargets": [ 0 ]
			},
			{
				"mRender": function (data, type, row) {
          return makebutton('planetmanage',row[gm.pd.id]);
				},
        "bSortable": false,
				"aTargets": [ 1 ]
			},
			{
				"mRender": function (data, type, row) {
          return makebutton('planetupgrade', row[gm.pd.id]);
				},
        "bSortable": false,
				"aTargets": [ 2 ]
			},
			{
				"mRender": function (data, type, row) {
          if (row[11] === true){
            return makebutton('fleetbuild', row[gm.pd.id]);
          } else {
            return "";
          }
				},
        "bSortable": false,
				"aTargets": [ 3 ]
			},
			{ "mData": gm.pd.name, "aTargets": [4] },
			{ "mData": gm.pd.society, "aTargets": [5] },
			{ 
				"mRender": function (data, type, row) {
          return row[gm.pd.resourcelist][planetlistresource];
				},
        "aTargets": [6] 
      }, 
      { "mRender": function(data,type,row) {return row[gm.pd.inctaxrate]+"%";},
        "aTargets": [7] },
      { "mRender": function(data,type,row) {return row[gm.pd.tariffrate]+"%";},
        "aTargets": [8] },
      { "mRender": function(data,type,row) {
          return makebuttonfn('centerplanet',
                            'Center on Planet',
                            'center',
                            'gm.centermap('+row[gm.pd.x]+', '+row[gm.pd.y]+');');
        },
        "bSortable": false,
        "aTargets": [9]
      }
          
		]
	} ); 
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
  jq = new JobQueue();
  pumenu = new PopUpMenu();
  var cz = gm.getmagnification();
  protocolversion = protocol;

  transienttabs = new SliderContainer('transientcontainer', 'right', 50);
  permanenttabs = new SliderContainer('permanentcontainer', 'left', 50);
  routebuilder  = new RouteBuilder();

  permanenttabs.pushtab('neighborslist', 'Neighbors', '', true);
  permanenttabs.pushtab('planetslist', 'Planets', '', true);
  permanenttabs.pushtab('fleetslist', 'Fleets', '', true);
  
  var dosectors = gm.viewablesectors();
  gm.getsectors(dosectors,0,true);
  
  jq.addjob(permanenttabs.gettaburl,['neighborslist', '/politics/neighbors/']);
  jq.addjob(permanenttabs.gettabhsr,['planetslist', '/planets/list2/']);
  jq.addjob(permanenttabs.gettabhsr,['fleetslist', '/fleets/list2/']);
 
  var vb = [gm.curcenter.x-(curwidth/2.0),
            gm.curcenter.y-(curheight/2.0),
            curwidth, curheight];

  pumenu.setlocation(curwidth/8.0,curheight/4.0);
  

  
  jq.addjob(buildsectorrings,[]);
 
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
    //gm.setxy(evt);
    gm.dohover(evt);
    //setstatusmsg(gm.mousepos.mapx + "," + gm.mousepos.mapy);
    if(mousedown === true){
      mousecounter++;
      if(mousecounter%3 === 0){
        pumenu.hide();
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
      pumenu.hide();
    } else if ((!routebuilder.active())&&
               (!currouteid)&&(!curplanetid)&&(!curfleetid)&&(!curarrowid)&&
               (!transienttabs.isopen())&&
               (!permanenttabs.isopen())&&
               (pumenu.ishidden())&&
               (mousecounter < 3)){
      pumenu.waiting();
      pumenu.setlocation(gm.mousepos.x,gm.mousepos.y);
      handlemenuitemreq(evt, '/map/root/');
    } else if((!routebuilder.active())&&
               (!currouteid)&&(!curplanetid)&&(!curfleetid)&&(!curarrowid)&&
               (pumenu.ishidden())&&
               (mousecounter < 3)){
      permanenttabs.hidetabs();
      transienttabs.hidetabs();
    } else if(!pumenu.ishidden()) {
      pumenu.hide();
    } else if((curarrowid)&&(!curplanetid)&&(!currouteid)&&(!curfleetid)){
      gm.mouseorigin = getcurxy(evt);
      pumenu.setlocation(gm.mousepos.x,gm.mousepos.y);
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
        until: "+"+(600+Math.floor(Math.random()*300)), format: 'hms',
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




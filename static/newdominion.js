var svgns = "http://www.w3.org/2000/svg";

var map;
var curwidth;
var curheight;
var curxcenter;
var curycenter;
var maplayer0;
var maplayer1;
var maplayer2;
var svgmarkers;
var zoomlevel = 3;
var zoomlevels = [100.0,90.0,80.0,60.0,45.0,30.0,20.0]
var timeleft = "+500s"
var originalview = [];
var tips = [];
var mousedown = new Boolean(false);
var mouseorigin;
var server = new XMLHttpRequest();
var resizeTimer = null;
var curfleetid = 0;
var curplanetid = 0;
var curslider = "";
var rubberband;
var sectorlines;
var youarehere;
var curx, cury;
var mousecounter = 0;
var juststarted = 0;
var sectors = [];
var onscreensectors = [];


function Point(x,y)
{
  this.x = x;
  this.y = y;
}

function Sector(key,jsondata)
{
  this.json = jsondata
  this.planets = jsondata['planets'];
  this.fleets = jsondata['fleets'];
  this.key = key;
}

function resetmap()
{
  while(maplayer0.hasChildNodes()) maplayer0.removeChild(maplayer0.firstChild);
  while(maplayer1.hasChildNodes()) maplayer1.removeChild(maplayer1.firstChild);
  while(maplayer2.hasChildNodes()) maplayer2.removeChild(maplayer2.firstChild);
  for (key in onscreensectors){
    onscreensectors[key] = '-';
  }
  var viewable = viewablesectors(getviewbox(map));
  adjustview(viewable);
  getsectors(viewable,0);
}

function loadtab(tab,urlstring, container) 
{
  $('a.current').toggleClass('current');
  $(tab).toggleClass('current');
  if (urlstring.length > 0){ 
    //$("#preloader").show(); 
    $.ajax( 
    { 
      url: urlstring, 
      cache: false, 
      success: function(message) 
      { 
        $(container).empty().append(message); 
        //$("#preloader").hide(); 
      } 
    }); 
  } 
} 


function getsectors(newsectors,force)
{
  var submission = {};
  var doit = 0;
  // convert newsectors (which comes in as a straight array)
  // over to the loaded sectors array (which is associative...)
  // and see if we have already asked for that sector (or indeed
  // already have it in memory, doesn't really matter...)
  for (sector in newsectors){
    if((force==1)||(!(sector in sectors))){
      submission[sector]=1;
      doit = 1;
    }
  }
  if(doit==1){
    //submission = submission.join('&');
    sendrequest(loadnewsectors,"/sectors/",'POST',submission);
    setstatusmsg("Requesting Sectors");
  }
}


function buildsectorfleets(sector,newsectorl1,newsectorl2)
{
  var cz = zoomlevels[zoomlevel];
  for(fleetkey in sector['fleets']){
    var fleet = sector['fleets'][fleetkey]
    var playerowned;
    if ('ps' in fleet){
      playerowned=1;
    } else {
      playerowned=0;
    }
    var group = document.createElementNS(svgns, 'g');
    group.setAttribute('fill', fleet.c);
    group.setAttribute('id', 'gf'+fleet.i);
    group.setAttribute('stroke', fleet.c);
    group.setAttribute('stroke-width', '.01');
    group.setAttribute('onmouseover',
                        'fleethoveron(evt,"'+fleet.i+'")');
    group.setAttribute('onmouseout',
                        'fleethoveroff(evt,"'+fleet.i+'")');
    group.setAttribute('onclick',
                        'dofleetmousedown(evt,"'+fleet.i+'",'+playerowned+')');

    if ('s' in fleet){
      var sensegroup = document.getElementById("sg-"+fleet.o);
      if(!sensegroup){
        sensegroup = document.createElementNS(svgns,'g');
        sensegroup.setAttribute('fill',fleet.c);
        sensegroup.setAttribute('id','sg-'+fleet.o);
        sensegroup.setAttribute('opacity','.3');
        maplayer0.appendChild(sensegroup);
      }
      var sensecircle = document.createElementNS(svgns, 'circle');
      sensecircle.setAttribute('cx', fleet.x*cz);
      sensecircle.setAttribute('cy', fleet.y*cz);
      sensecircle.setAttribute('r', fleet.s*cz);
      sensegroup.appendChild(sensecircle);
    }

    if ('x2' in fleet){
      
      var marker = document.getElementById("marker-"+fleet.c);
      if(!marker){
        marker = document.createElementNS(svgns, 'marker');
        marker.setAttribute('id','marker-'+fleet.c.substring(1));
        marker.setAttribute('viewBox','0 0 10 10');
        marker.setAttribute('refX',1);
        marker.setAttribute('refY',5);
        marker.setAttribute('markerUnits','strokeWidth');
        marker.setAttribute('orient','auto');
        marker.setAttribute('markerWidth','5');
        marker.setAttribute('markerHeight','4');
        var pline = document.createElementNS(svgns, 'polyline');
        pline.setAttribute('points','0,0 10,5 0,10 1,5');
        pline.setAttribute('fill',fleet.c);
        pline.setAttribute('fill-opacity','1.0');
        marker.appendChild(pline);
        svgmarkers.appendChild(marker);
      }
      var line = document.createElementNS(svgns, 'line');

      line.setAttribute('marker-end', 'url(#marker-'+fleet.c.substring(1)+')');
      line.setAttribute('x1', fleet.x*cz);
      line.setAttribute('y1', fleet.y*cz);
      line.setAttribute('x2', fleet.x2*cz);
      line.setAttribute('y2', fleet.y2*cz);
      line.setAttribute('stroke',fleet.c);
      if(fleet.t == 's'){
        line.setAttribute('stroke-dasharray',(.09*cz)+","+(.09*cz));
        line.setAttribute('stroke-width', .02*cz+"");
      } else if(fleet.t == 'a') {
        line.setAttribute('stroke-dasharray',(.3*cz)+","+(.3*cz));
        line.setAttribute('stroke-width', .02*cz+"");
      } else if(fleet.t == 't') {
        line.setAttribute('stroke-dasharray',(.03*cz)+","+(.09*cz));
        line.setAttribute('stroke-width', .03*cz+"");
      } else if(fleet.t == 'm') {
        line.setAttribute('stroke-width', .03*cz+"");
      } else {
        line.setAttribute('stroke-width', .02*cz+"");
      }


      group.appendChild(line);
    }
    if('dmg' in fleet) {
      var circle = document.createElementNS(svgns, 'circle');
      circle.setAttribute('cx', fleet.x*cz);
      circle.setAttribute('cy', fleet.y*cz);
      circle.setAttribute('r', .2*cz);
      circle.setAttribute('style','fill:url(#damagedfleet);');
      newsectorl1.appendChild(circle);
    } else if('dst' in fleet) {
      var circle = document.createElementNS(svgns, 'circle');
      circle.setAttribute('cx', fleet.x*cz);
      circle.setAttribute('cy', fleet.y*cz);
      circle.setAttribute('r', .2*cz);
      circle.setAttribute('style','fill:url(#destroyedfleet);');
      newsectorl1.appendChild(circle);
    }
    var circle = document.createElementNS(svgns, 'circle');
    circle.setAttribute('fill', fleet.c);
    circle.setAttribute('cx', fleet.x*cz);
    circle.setAttribute('cy', fleet.y*cz);
    circle.setAttribute('r', .04*cz);
    circle.setAttribute('id', 'f'+fleet.i);
    circle.setAttribute('title', fleet.sl);
    group.appendChild(circle);
    newsectorl2.appendChild(group);
  } 
}


function buildsectorplanets(sector,newsectorl1, newsectorl2)
{
  var cz = zoomlevels[zoomlevel];
  for(planetkey in sector['planets']){
    var planet = sector['planets'][planetkey]
 
    // draw You Are Here and it's arrow if it's a new player
    if (((newplayer == 1) && ('pp' in planet))){
      youarehere.setAttribute('visibility','visible');
      youarehere.setAttribute('x',(planet.x-1.5)*cz);
      youarehere.setAttribute('y',(planet.y+1.3)*cz);
      var line = document.createElementNS(svgns, 'line');
      line.setAttribute('stroke-width', '1.2');
      line.setAttribute('stroke', '#aaaaaa');
      line.setAttribute('marker-end', 'url(#endArrow)');
      line.setAttribute('x2', (planet.x-.2)*cz);
      line.setAttribute('y2', (planet.y+.3)*cz);
      line.setAttribute('x1', (planet.x-.7)*cz);
      line.setAttribute('y1', (planet.y+1.0)*cz);
      newsectorl2.appendChild(line);
    }
  
    // does it have a sensor range circle?
    if (('s' in planet)&&('o' in planet)){
      var sensegroup = document.getElementById("sg-"+planet.o);
      if(!sensegroup){
        sensegroup = document.createElementNS(svgns,'g');
        sensegroup.setAttribute('id','sg-'+planet.o);
        sensegroup.setAttribute('fill',planet.h);
        sensegroup.setAttribute('opacity',.2);
        maplayer0.appendChild(sensegroup);
      }
      var circle = document.createElementNS(svgns, 'circle');
      circle.setAttribute('cx',  planet.x*cz);
      circle.setAttribute('cy',  planet.y*cz);
      circle.setAttribute('r',   planet.s*cz);
      sensegroup.appendChild(circle);
    }

    // military circle
    if ('mil' in planet){
      var highlight = document.createElementNS(svgns, 'circle');
      highlight.setAttribute('cx', planet.x*cz);
      highlight.setAttribute('cy', planet.y*cz);
      highlight.setAttribute('r', (planet.r+.17)*cz);
      highlight.setAttribute('stroke', planet.h);
      highlight.setAttribute('fill', 'none');
      highlight.setAttribute('stroke-width', .02*cz);
      if(planet.mil == 3){  
        highlight.setAttribute('stroke-dasharray',(.045*cz)+","+(.045*cz));
      } else if (planet.mil == 2) {
        highlight.setAttribute('stroke-dasharray',(.09*cz)+","+(.09*cz));
      } else {
        highlight.setAttribute('stroke-dasharray',(.045*cz)+","+(.045*cz));
      }

      //highlight.setAttribute('stroke-opacity', '.5');
      newsectorl1.appendChild(highlight);
    }
      

    // capital circle
    if ('cap' in planet){
      var highlight = document.createElementNS(svgns, 'circle');
      highlight.setAttribute('cx', planet.x*cz);
      highlight.setAttribute('cy', planet.y*cz);
      highlight.setAttribute('r', (planet.r+.12)*cz);
      highlight.setAttribute('stroke', planet.h);
      highlight.setAttribute('stroke-width', .02*cz);
      //highlight.setAttribute('stroke-opacity', '.5');
      newsectorl1.appendChild(highlight);
    }  
    if (planet.h != 0){
      var highlight = document.createElementNS(svgns, 'circle');
      highlight.setAttribute('cx', planet.x*cz);
      highlight.setAttribute('cy', planet.y*cz);
      highlight.setAttribute('r', (planet.r+.06)*cz);
      highlight.setAttribute('stroke', planet.h);
      highlight.setAttribute('stroke-width', .04*cz);
      newsectorl2.appendChild(highlight);
    }
    var circle = document.createElementNS(svgns, 'circle');
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
    circle.setAttribute('fill', planet.c);
    circle.setAttribute('title', planet.n);
    circle.setAttribute('onmouseover',
                        'planethoveron(evt,"'+planet.i+'")');
    circle.setAttribute('onmouseout',
                        'planethoveroff(evt,"'+planet.i+'")');
    circle.setAttribute('onclick',
                        'doplanetmousedown(evt,"'+planet.i+'",'+playerowned+')');
    newsectorl2.appendChild(circle);
  }
}

function loadnewsectors(newsectors)
{
  hidestatusmsg("loadnewsectors");
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
    
function adjustview(viewable)
{
  for (key in viewable){
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
  curx = evt.clientX;
  cury = evt.clientY;
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

function hidestatusmsg(msg)
{
  $('#statusmsg').hide("fast");
}

function rubberbandfromfleet(fleetid,initialx,initialy)
{
  var cz = zoomlevels[zoomlevel];
  var vb = getviewbox(map);
  curfleetid = fleetid;
  killmenu();
  $('#fleets').hide('fast'); 
  rubberband.setAttribute('visibility','visible');
  rubberband.setAttribute('x1',initialx*cz);
  rubberband.setAttribute('y1',initialy*cz);
  rubberband.setAttribute('x2',initialx*cz);
  rubberband.setAttribute('y2',initialy*cz);
}


function handleserverresponse(response)
{
  if ('menu' in response){
    $('#menu').html(response['menu'])
    $('#menu').show()
  }
  if ('window' in response){
    if(('x' in response)&&('y' in response)){
      $('#window').css({'top':response['y'],'left':response['x']});
    }
    $('#menu').hide();
    $('#windowcontent').html(response['window'])
    $('#window').show()
  }
  if ('killmenu' in response){
    $('#menu').hide()
  }
  if ('killwindow' in response){
    $('#window').hide()
  }
  if ('status' in response){
    setstatusmsg(response['status'])
  } else {
    hidestatusmsg("loadnewmenu");
  }
  if ('rubberband' in response){
    rubberbandfromfleet(response['rubberband'][0],
                        response['rubberband'][1],
                        response['rubberband'][2]);
  }
  if ('resetmap' in response){
    sectors = [];
    resetmap();
  }
  if ('slider' in response){
    $(curslider).html(response['slider']);
  }
}

function removetooltips()
{
  while(tips.length){
    var id = tips.pop()
    $(id).btOff()
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
function loadtooltip(id,url,tipwidth)  
{
  tips.push(id);
  $(id).bt({
    ajaxPath:url,
    fill:"#886600", width: tipwidth,
    trigger:["click","click"],
    strokeWidth: 2, strokeStyle: 'white',
    cornerRadius: 10, spikeGirth: 20});
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
    dataType: 'json'
  });
}
    
    

function handlemenuitemreq(event, type, requestedmenu, id)
{
  prevdef(event);
  var myurl = "/"+type+"/"+id+"/" + requestedmenu + "/";
  setmenuwaiting();
  sendrequest(handleserverresponse,myurl, "GET");
}

function sendform(subform,request)
{
  var submission = {};
  for(i in subform.getElementsByTagName('select')){
    var formfield = subform.getElementsByTagName('select')[i];
    if((formfield.name)&&(formfield.type == 'select-one')){
      submission[formfield.name] = formfield.options[formfield.selectedIndex].value;
    }
  }
  for(i in subform.getElementsByTagName('button')){
    var formbutton = subform.getElementsByTagName('button')[i];
    if(formbutton.id){
      submission[formbutton.id] = 1;
    }
  }
  for(i in subform.getElementsByTagName('textarea')){
    var textarea = subform.getElementsByTagName('textarea')[i];
    if((textarea.name)&&(textarea.value)){
      submission[textarea.name] = textarea.value;
    }
  }
  for(i in subform.getElementsByTagName('input')){
    var formfield = subform.getElementsByTagName('input')[i];
    if((formfield.name)&&(formfield.value)){
      if(formfield.type=="radio"){
        if(formfield.checked){
          submission[formfield.name] = formfield.value;
        }
      } else if(formfield.type=="checkbox"){
        if(formfield.checked){
          submission[formfield.name] = formfield.value;
        }
      } else {
        submission[formfield.name] = formfield.value;
      }
    }
  }
  sendrequest(handleserverresponse,request,'POST',submission);
  $('#window').hide();
  setmenuwaiting();
}

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
function zoomcircleid(factor,id)
{
  var circle = document.getElementById(id);
  if(circle){
    var radius = circle.getAttribute("r");
    radius *= factor;
    circle.setAttribute("r", radius);
    if(id[0]=='f'){
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
  zoomcircle(evt,.5);
  curplanetid = 0;
}

function fleethoveron(evt,fleet)
{
  if($('#menu').size()==0){
    setstatusmsg("Left Click to Manage Fleet");
  }
  document.body.style.cursor='pointer';
  setxy(evt);
  zoomcircle(evt,2.0);
}

function fleethoveroff(evt,fleet)
{
  hidestatusmsg("fleethoveroff");
  document.body.style.cursor='default';
  setxy(evt);
  zoomcircle(evt,.5);
}

function buildmenu()
{
  $('#menu').attr('style','position:absolute; top:'+(cury+10)+
                       'px; left:'+(curx+10)+ 'px;');
  $('#menu').show();
  return newmenu;
}

function buildwindow(x,y)
{
  $('#windowcontents').html('x');
  $('#window').css('left',x);
  $('#window').css('top',y);
  $('#window').show();
  return newmenu;
}

function dofleetmousedown(evt,fleet,playerowned)
{
  setxy(evt);
  if(curfleetid==fleet){
    curfleetid=0;
  } else if(!curfleetid){
    var newmenu = buildmenu();
    if(playerowned==1){
      handlemenuitemreq(evt, 'fleets', 'root', fleet);
    } else {
      handlemenuitemreq(evt, 'fleets', 'info', fleet);
    }
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
    var submission = {}
    submission['planet']=planet;

    sendrequest(loadnewsectors, request, 'POST', submission);
    curfleetid=0;
  } else {
    var newmenu = buildmenu();    
    if(playerowned==1){
      handlemenuitemreq(evt, 'planets', 'root', planet);
    } else {
      handlemenuitemreq(evt, 'planets', 'info', planet);
    }

  } 
}


function prevdef(event) {
  event.preventDefault();
}
function stopprop(event) {
  event.stopPropagation();
}


function viewablesectors(viewbox)
{
  var cz = zoomlevels[zoomlevel];
  var topx = parseInt((viewbox[0]/cz)/5.0);
  var topy = parseInt((viewbox[1]/cz)/5.0);
  var width = parseInt((viewbox[2]/cz)/5.0)+2;
  var height = parseInt((viewbox[3]/cz)/5.0)+2;
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


function init(timeleftinturn,cx,cy)
{
  juststarted = 1;
  map = document.getElementById('map');
  maplayer0 = document.getElementById('maplayer0');
  maplayer1 = document.getElementById('maplayer1');
  maplayer2 = document.getElementById('maplayer2');
  svgmarkers = document.getElementById('svgmarkers');
  rubberband = document.getElementById('rubberband');
  sectorlines = document.getElementById('sectorlines');
  youarehere = document.getElementById('youarehere');
  
  curxcenter = cx*zoomlevels[zoomlevel];
  curycenter = cy*zoomlevels[zoomlevel];
  curwidth = $(window).width()-6;
  // apparantly chrome sometimes misreports window height...
  ($(window).height()-8 > $(document).height()-8) ? 
    curheight = $(window).height()-8 : 
    curheight = $(document).height()-8; 

  var vb = [curxcenter-(curwidth/2.0),
            curycenter-(curheight/2.0),
            curwidth, curheight];
  setviewbox(vb);

  movemenu(curwidth/8.0,curheight/4.0);
  
  setTimeout(function(){
    if(juststarted == 1){
      killmenu();
      juststarted == 0;
    }
  }, 8000);

  originalview = getviewbox(map);
  map.setAttribute("viewBox", originalview.join(" "));
  
  var dosectors = viewablesectors(originalview);
  getsectors(dosectors,0);
  
  $('#mapdiv').mousedown(function(evt) { 
    setxy(evt);
    if(evt.preventDefault){
      evt.preventDefault();
    }
    if(juststarted==1){
      killmenu();
      juststarted = 0;
    }
    killmenu();
    removetooltips();
    $('div.slideoutcontents').hide('fast');
    $('div.slideoutcontentscontents').empty();
    document.body.style.cursor='move';
    mousedown = true;
    mouseorigin = getcurxy(evt);
  }); 

  $('#mapdiv').mousemove(function(evt) { 
    var viewbox = getviewbox(map);
    if(evt.preventDefault){
      evt.preventDefault();
    }             
    mousecounter++;

    if((mousedown == true)&&(mousecounter%3 == 0)){
      var neworigin = getcurxy(evt);
      var dx = (mouseorigin.x - neworigin.x);
      var dy = (mouseorigin.y - neworigin.y);
      var dosectors;
      viewbox[0] = viewbox[0] + dx;
      viewbox[1] = viewbox[1] + dy;
      setviewbox(viewbox);
      mouseorigin = neworigin;
    }
    if(curfleetid){
      var newcenter = getcurxy(evt);
      rubberband.setAttribute('x2',newcenter.x+viewbox[0]);
      rubberband.setAttribute('y2',newcenter.y+viewbox[1]);
    }
  });
  $('#mapdiv').mouseup(function(evt) { 
    setxy(evt);
    if(evt.preventDefault){
      evt.preventDefault();
    }
    if(evt.detail==2){
      var cxy = getcurxy(evt);
      zoom(evt,"-",cxy);
    }
    document.body.style.cursor='default';
    mousedown = false;
    rubberband.setAttribute('visibility','hidden');
    if((curfleetid)&&(!curplanetid)){
      var vb = getviewbox(map);
      var curloc = getcurxy(evt);
      var cz = zoomlevels[zoomlevel];
      curloc.x = curloc.x/cz + vb[0]/cz;
      curloc.y = curloc.y/cz + vb[1]/cz;

      movefleettoloc(evt,curfleetid,curloc)
      curfleetid=0;
    }

    var dosectors = viewablesectors(getviewbox(map));
    getsectors(dosectors,0);
    adjustview(dosectors);
  
  });

  $(window).bind('resize', function() {
    if (resizeTimer) clearTimeout(resizeTimer);
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

  vb[0] = x-(vb[2]/2.0)
  vb[1] = y-(vb[3]/2.0)
  setviewbox(vb);

  resetmap();
}

function resizewindow() { 
  var newwidth = $(window).width();
  var newheight = $(window).height();
  if(newwidth != 0){
    curwidth = newwidth-6;
  }
  if(newheight != 0){
    curheight = newheight-8;
  }
  var viewbox = getviewbox(map);
  viewbox[2]=curwidth;
  viewbox[3]=curheight;
  setviewbox(viewbox);
  //paper.setSize(curwidth,curheight);
}

function zoommiddle(evt, magnification)
{
  //var p = getcurxy(evt);
  //var viewbox = getviewbox(map);
  //var newcenter = map.createSVGPoint();
  //var x,y;
  //x = viewbox[0]+((viewbox[2]-viewbox[0])/2.0);
  //y = viewbox[1]+((viewbox[3]-viewbox[1])/2.0);
  var p = new Point(curwidth/2.0,curheight/2.0);
  zoom(evt,magnification,p);
}
function expandtoggle(id)
{
  if($(id).attr('src') == '/site_media/expandup.png'){
    $(id).attr('src', '/site_media/expanddown.png');
  } else {
    $(id).attr('src', '/site_media/expandup.png');
  }
}

function zoom(evt, magnification, screenloc)
{
  if(evt.preventDefault){
    evt.preventDefault();
  }
  var changezoom = 0;
  var oldzoom = zoomlevels[zoomlevel];
  if((magnification == "+")&&(zoomlevel<6)){
    changezoom = 1;
    zoomlevel++;
  } else if((magnification == "-")&&(zoomlevel>0)){
    changezoom = 1;
    zoomlevel--;
  }
  if(changezoom){
    // manipulate the zoom dots in the UI
    for(var i=1;i<=zoomlevel;i++){
      var zid = "#zoom"+i;
      $(zid).attr('src','/site_media/blackdot.png');
    }
    for(var i=zoomlevel+1;i<7;i++){
      var zid = "#zoom"+i;
      $(zid).attr('src','/site_media/whitedot.png');
    }


    var viewbox = getviewbox(map);
    var newzoom = zoomlevels[zoomlevel];
    var newviewbox = new Array();
    // screenloc is in screen coordinates
    // newcenter is in world coordinates
    var newcenter = new Point((viewbox[0]+screenloc.x)/oldzoom*newzoom,
                              (viewbox[1]+screenloc.y)/oldzoom*newzoom);
    
    newviewbox[0] = newcenter.x-(curwidth/2.0);
    newviewbox[1] = newcenter.y-(curheight/2.0);
    newviewbox[2] = curwidth;
    newviewbox[3] = curheight;
    map.setAttribute("viewBox",newviewbox.join(" "));
    resetmap();
  }
}

function setviewbox(viewbox)
{
  curxcenter = viewbox[0]+(viewbox[2]/2.0);
  curycenter = viewbox[1]+(viewbox[3]/2.0);
  curwidth = viewbox[2] 
  curheight = viewbox[3] 
  map.setAttribute("viewBox",viewbox.join(" "));
  map.setAttribute("width",curwidth);
  map.setAttribute("height",curheight);
  
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
  //var oldmenu = document.getElementById('menu');
  $('#menu').hide();
  $('#window').hide();
  //if(oldmenu){
  //  oldmenu.parentNode.removeChild(oldmenu);
  //}
}


function setmenuwaiting()
{
  setstatusmsg("Loading...");
  $('#menu').html('<div><img src="/site_media/ajax-loader.gif">loading...</img></div>');
  //$('#menu').show();
}



function getcurxy(evt)
{
  p = new Point(evt.pageX,evt.pageY);
  return p;
}

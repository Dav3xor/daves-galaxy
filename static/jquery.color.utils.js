/**
 * color-utils for jQuery
 * 
 * Copyright (c) 2008 Yoshiomi KURISU
 * Licensed under the MIT (MIT-LICENSE.txt)  licenses.
 * 
 */
(function($){
	
	$.isHexadecimalColor = function(color){
		if(color && color.match 
				&& ( color.match(/^#[0-9a-fA-F]{3}$/) || color.match(/^#[0-9a-fA-F]{6}$/)) ) return true;
		else return false;
	}
	
	$.isRGBColor = function(color){
		if(color && color.match && color.match(/^rgb\(([0-9]|[1-9][0-9]|[1][0-9]{2}|[2][0-4][0-9]|[2][5][0-5]),[ ]{0,1}([0-9]|[1-9][0-9]|[1][0-9]{2}|[2][0-4][0-9]|[2][5][0-5]),[ ]{0,1}([0-9]|[1-9][0-9]|[1][0-9]{2}|[2][0-4][0-9]|[2][5][0-5])\)$/) ) return true;
		else return false;
	}

	$.isColor = function(color){
		var $ = jQuery;
		if($.isHexadecimalColor(color) || $.isRGBColor(color)) return true;
		else 	return false;
	}
	
	$.RGB = function(color){
		var $ = jQuery;
		if(typeof color == 'string'){
			if($.isRGBColor($.fmtColor(color,'rgb'))){
				return [parseInt(RegExp.$1),parseInt(RegExp.$2),parseInt(RegExp.$3)];
			}
			return [];
		}else if(color instanceof Array && color.length == 3 
				&& isFinite(color[0]-0) && isFinite(color[1]-0) && isFinite(color[2]-0)
				&& ( 0 <= color[0]-0 && color[0] -0 <= 255)
				&& ( 0 <= color[1]-0 && color[1] -0 <= 255)
				&& ( 0 <= color[2]-0 && color[2] -0 <= 255)){
			return 'rgb('+color[0]+', '+color[1] + ', ' + color[2]+')';
		}
		return color;
	}
	
	$.colorVectorValue = function(color){
		var $ = jQuery;
		var c = $.RGB(color);
		if(c.length == 3){
			var r = c[0],g = c[1],b = c[2];
			return Math.sqrt( (r*r)+(g*g)+(b*b) ).toFixed(2);
		}
		return 0;
	}

	$.colorDecimalValue = function(color){
		var $ = jQuery;
		if($.isColor(color)){
			color = $.fmtColor(color,'hexadecimal');
			return parseInt(color.substr(1,6),16);
		}
		return 0;
	}


	$.fmtColor = function(color,fmt){
		var $ = jQuery;
		if($.isColor(color) == false) return color;
		var pad = function(str){
			if(str.length < 2){
				for(var i = 0,len = 2 - str.length ; i<len ; i++){
					str = '0'+str;
				}
			}
			return str;
		}
		if(color.match(/^#[0-9a-fA-F]{3}$/)){
			var r = color.substr(1,1);
			var g = color.substr(2,1);
			var b = color.substr(3,1);
			color = '#' + r + r + g + g + b + b;
		}
		
		fmt = (fmt)?fmt:(function(c){
			if($.isRGBColor(c)) return 'hexadecimal';
			else if($.isHexadecimalColor(c)) return 'rgb';
			else return '';
		})(color);
		if (fmt == 'rgb' && $.isHexadecimalColor(color)) {
			var r = parseInt(color.substr(1,2),16);
			var g = parseInt(color.substr(3,2),16);
			var b = parseInt(color.substr(5,2),16);
			color = $.RGB([r,g,b]);
		}else if (fmt == 'hexadecimal') {
			var c = $.RGB(color);
			if(c.length == 3){
				var r = pad(c[0].toString(16)),g = pad(c[1].toString(16)),b= pad(c[2].toString(16));
				color = '#' + r + g + b;
			}
		}
		return color;
	}
	
	$.modColor = function(color,type,value,rotate){
	  var gb = function(color,type,value,rotate){
	    if((type=='r'|| type=='g' || type=='b') && isFinite(value)) {
		    var $ = jQuery;
		    tmp = $.fmtColor(color,'rgb');
		    var gc = function(original_value,value,rotate){
		      var v = parseInt(original_value) + (value -0);
		      if(rotate){
			      v = (v > 255)?v-255:v;
			      v = (v < 0)?v+255:v;
		      }else{
			      v = (v > 255)?255:v;
			      v = (v < 0)?0:v;
		      }
		      return v;
		    }
		    if($.isRGBColor(tmp)){
					var r = parseInt(RegExp.$1);
					var g = parseInt(RegExp.$2);
					var b = parseInt(RegExp.$3);
			    if(type=='r'){
			      r = gc(RegExp.$1,value,rotate);
			    }else if(type=='g'){
			      g = gc(RegExp.$2,value,rotate);
			    }else if(type=='b'){
			      b = gc(RegExp.$3,value,rotate);
			    }
			    color = $.RGB([r,g,b]);
		    }
	    }
	    return color;
	  }
	  if(type instanceof Array && type.length == 3){
	  	type = {'r':type[0],'g':type[1],'b':type[2]};
	  }
	  if(type instanceof Object){
	  	rotate = value;
	    var params = ['r','g','b'];
	    for(var i = 0,len = params.length ; i<len ; i++){
	      var v = type[params[i]];
	      if( v && isFinite(v)){
	        color = gb(color,params[i],v,rotate);
	      }
	    }
	    return color;
	  }else if(typeof type == 'string' && isFinite(value)){
	    return gb(color,type,value,rotate);
	  }
	}
	
	$.averageColor = function(colors){
		var $ = jQuery;
		var color = [0,0,0];
		var cnt = 0;
		for(var i =0,len=colors.length;i<len;i++){
			var c = $.RGB(colors[i]);
			if(c.length == 3){
				color[0]  = color[0] + c[0];
				color[1]  = color[1] + c[1];
				color[2]  = color[2] + c[2];
				cnt ++;
			}
		}
		return $.RGB([Math.round(color[0] / cnt),Math.round(color[1] / cnt),Math.round(color[2] / cnt)]);
	}
	
	$.colorize = function(p){
		var $ = jQuery;
		if(typeof p == 'string'){
			var t = '#' + p.replace(/o/gi,'0').replace(/[li]/gi,'1').replace(/z/gi,'2').replace(/b/gi,'6').replace(/\?/gi,'7').replace(/q/gi,'9');
			if($.isColor(t)) return t;
		}else if(p instanceof Object){
			if(isFinite(p.min) && isFinite(p.max) && isFinite(p.value)){
				var total = p.max - p.min;
				var c = parseInt(p.value * 1677216 / total).toString(16);
		    for(var i = 0,len = 6-c.length;i < len;i++){
		        c = '0'+c;
		    }
		    return '#'+c;
			}
		}
		return '#000000';
	}
	
	$.fn.modColor = function(prop,type,value,rotate){
		var $ = jQuery;
	  var v = $(this).css(prop);
	  $(this).css(prop,$.modColor(v,type,value,rotate));
	  return this;
	}
	
	$.fn.averageColor = function(prop){
		prop = (prop)?prop:'backgroundColor';
		var $ = jQuery;
		var tmp = [];
		for(var i = 0,len = this.length;i<len;i++){
			var c = this.eq(i).css(prop);
			if($.isColor(c)){
				tmp.push(c);
			}
		}
		return $.averageColor(tmp);
	}
	
	$.fn.sortByColor = function(prop){
		var $ = jQuery;
		prop = (prop)?prop:'backgroundColor';

    var fn = function(a,b,prop){
    		var t = $.colorDecimalValue($(a).css(prop)) - $.colorDecimalValue($(b).css(prop));
    		if(t == 0) return $.colorVectorValue($(a).css(prop)) - $.colorVectorValue($(b).css(prop));
    		else return t;
    }
    function q(jq, h, t,prop) {
        var pivot = jq[parseInt( h +  (t - h)/2 )];
        var i = h - 1;
        var j = t + 1;
        while (1){
            while (fn(jq[++i], pivot,prop) < 0);
            while (fn(jq[--j], pivot,prop) > 0);
            if (i >= j) break;
            var tmp = jq[i];
            jq[i] = jq[j];
            jq[j] = tmp;
        }
        if (h < i - 1) q(jq, h, i - 1,prop);
        if (j + 1 < t) q(jq, j + 1, t,prop);
        return jq;
    }
    return q(this, 0, this.length - 1,prop);

	}


})(jQuery);

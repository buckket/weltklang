$(function() {
    var loaded = false;
	$('#locale-button').click(function(){
		if (loaded) {
			return true;
		}
		loaded = true;
		$('#locale-placeholder').html('<i class="icon-spinner icon-spin"></i>');
		$('#locale-placeholder').load('/api/site/timezoneselector', function() {
			$('#timezone-image').timezonePicker({target:'#timezone-select'});
			update_pin();
			$('#lang').click(update_pin)
		});
		
	});
	$('#locale-placeholder').click(function(e){
		e.stopPropagation();
	});
	
	function update_pin() {
		$.getJSON('/api/site/localeinfo/'+$('#lang').val(), function(data) {
			$('.timezone-picker .timezone-pin').attr('src', data.img);
			});
	}
	
});

function pad (str, max) {
    return str.length < max ? pad("0" + str, max) : str;
}

function update_np(force) {
	var banner = false;
	if ($("div.nowplaying-banner").length > 0) {
		banner = true;
	}
	$.getJSON('/api/site/nowplaying?full=full',function(data) {
		if (data.success) {
			if (banner) {
				bannerdiv = $("div.nowplaying-banner");
				if (data.data.show) {
					var cshow = bannerdiv.find('div.current-show');
					if (bannerdiv.hasClass('offline') || force) {
						bannerdiv.removeClass('offline');
						cshow.html('<h2 class="outline" id="np-show"></h2>' +
						           '<h6 class="outline" id="np-dj"></h6>' +
						   	       '<div class="progress">' +
						   		   '<div style="position:absolute;left:3px" class="outline" id="np-begin"></div>' +
						   		   '<div style="position:absolute;right:3px" class="outline" id="np-end"></div>' +
						   		   '<div class="bar" style="width: 0%;"></div>' +
						   		   '</div>');
					}
					var showtitle = '';
					if (data.data.series) {
						showtitle = data.data.series.name+' <small>'+data.data.show.name+'</small>';
					} else {
						showtitle = data.data.show.name;
					}
					cshow.find('#np-show').html(showtitle);
					cshow.find('#np-dj').html('by '+data.data.users.links);
					var begin = new Date(data.data.show.begin);
					cshow.find('#np-begin').html(pad(begin.getHours()+'', 2)+':'+pad(begin.getMinutes()+'', 2));
					if (data.data.show.type == 'PLANNED') {
						var end = new Date(data.data.show.end);
						var progress = ((data.data.show.now - data.data.show.begin)/(data.data.show.end - data.data.show.begin))*100;
						cshow.find('#np-end').html(pad(end.getHours()+'', 2)+':'+pad(end.getMinutes()+'', 2));
						cshow.find('div.bar').css('width', progress+'%');
					} else {
						cshow.find('#np-end').html('');
						cshow.find('div.bar').css('width', '100%');
					}
					if (data.data.show.logo) {
						cshow.css('background-image', "url('"+data.data.show.logo+"')");
					} else {
						cshow.css('background-image', "");
					}
					
					
					
				} else {
					if (!bannerdiv.hasClass('offline')) {
						bannerdiv.addClass('offline');
						var cshow = bannerdiv.find('div.current-show');
						cshow.html('<h1 class="outline">...silence...</h1><h4 class="outline">(more or less)</h4>');
						cshow.css('background-image', "url('http://i.imgur.com/HbEqICh.jpg')");
					}
				}
			}
		}
		setTimeout(update_np,5000);
	});
}

$(function() {
	update_np(true);
});

/**
 * Imgur Uploader
 * 
 * USAGE:
 * $('#imguruploader').imgurUploader({'clientid':'{{ imgur.client | safe }}',
 *                                  'target':'#image'})
 *                                  
 * 
 * 
 */

(function( $ ){

  $.fn.imgurUploader = function( options ) {  
    var settings = $.extend( {
      'clientid' : false,
      'target' : false,
    }, options);

    function open_file(context) {
    	context.data.find('input').click();
        return false;
    }
    
    function upload(context) {
        file = context.target.files[0];
        if (!file || !file.type.match(/image.*/)) return;

        var fd = new FormData();
        fd.append("image", file);
        fd.append("type", 'file');
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "https://api.imgur.com/3/image");
        xhr.setRequestHeader("Authorization", "Client-ID " + settings.clientid);
        xhr.onload = function() {
        	if (xhr.status == 200) {
        		var img_url = $.parseJSON(xhr.responseText).data.link;
        		context.data.find('.thumbnail').css("background-image", "url('"+img_url+"')");
        		context.data.find('.status').hide();
        		$(settings.target).val(img_url);        		
        	} else {
        		alert("Upload failed with: "+xhr.statusText);
        	}
        }
        context.data.find('.status').show();
        xhr.send(fd);
    }
    function empty(context) {
    	$(settings.target).val('');
    	context.data.find('.thumbnail').css("background-image", "");
    }
    
    return this.each(function() {
    	var $this = $(this);
        $this.find('a').first().click($this, open_file);
        $this.find('a').last().click($this, empty);
        $this.find('.thumbnail').css("background-image", "url('"+$(settings.target).val()+"')");
        $this.find('input').change($this, upload);
    });

  };
})( jQuery );
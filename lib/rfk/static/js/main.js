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

    function update_disco() {
        var current_show = $.nowPlaying.get_current_show();
        var disco = $("div.disco");
        var background = disco.find('div.background');
        if (current_show) {
            disco.find('.hp').show();
            dj = disco.find('.dj').show();
            dj.find('img').attr('src','/static/img/cb/'+current_show.user.countryball);
            if (current_show.logo) {
                background.css('background-image', "url('"+current_show.logo+"')");
            } else {
                background.css('background-image', "");
            }
            if (current_show.name) {
                disco.find('#ticker').html(current_show.name);
            }
            else {
                disco.find('#ticker').html('DJ did not enter a name へ‿(ツ)‿ㄏ');
            }
        } else {
            background.css('background-image', "url('http://i.imgur.com/HbEqICh.jpg')");
            disco.find('.hp').hide();
            disco.find('.dj').hide();
        }
    }

    function update_banner() {
        var current_show = $.nowPlaying.get_current_show();
        var next_show = $.nowPlaying.get_current_show();
        bannerdiv = $("div.nowplaying-banner");
        var cshow = bannerdiv.find('div.current-show');
        var showtitle = '';
        if (current_show) {
            if (bannerdiv.hasClass('offline')) {
                bannerdiv.removeClass('offline');
                cshow.html('<h2 class="outline" id="np-show"></h2>' +
                           '<h6 class="outline" id="np-dj"></h6>' +
                           '<div class="progress">' +
                           '<div style="position:absolute;left:3px" class="outline" id="np-begin"></div>' +
                           '<div style="position:absolute;right:3px" class="outline" id="np-end"></div>' +
                           '<div class="progress-bar" style="width: 0%;"></div>' +
                           '</div>');
            }
            if (current_show.series) {
                showtitle = current_show.series.name+' <small>'+current_show.name+'</small>';
            } else {
                showtitle = current_show.name;
            }
            if (showtitle == '' ) {
                showtitle = 'DJ did not enter a name へ‿(ツ)‿ㄏ';
            }
            cshow.find('#np-show').html(showtitle);
            cshow.find('#np-dj').html('by '+current_show.user.links);
            var begin = moment(current_show.begin).utc();
            cshow.find('#np-begin').html(pad(begin.hours()+'', 2)+':'+pad(begin.minutes()+'', 2));
            if (current_show.type == 'PLANNED') {
                var end = moment(current_show.end).utc();
                var progress = ((current_show.now - current_show.begin)/(current_show.end - current_show.begin))*100;
                cshow.find('#np-end').html(pad(end.hours()+'', 2)+':'+pad(end.minutes()+'', 2));
                cshow.find('div.progress-bar').css('width', progress+'%');
            } else {
                cshow.find('#np-end').html('');
                cshow.find('div.bar').css('width', '100%');
            }
            if (current_show.logo) {
                cshow.css('background-image', "url('"+current_show.logo+"')");
            } else {
                cshow.css('background-image', "");
            }
        } else {
            if (!bannerdiv.hasClass('offline')) {
                bannerdiv.addClass('offline');
                cshow.html('<h1 class="outline">...silence...</h1><h4 class="outline">(more or less)</h4>');
                cshow.css('background-image', "url('http://i.imgur.com/HbEqICh.jpg')");
            }
        }
        var nshow = bannerdiv.find('div.next-show');
        if (next_show) {
            showtitle = '';
            if (next_show.series) {
                showtitle = next_show.series.name+' <small>'+next_show.name+'</small>';
            } else {
                showtitle = next_show.name;
            }
            nshow.find('#ns-showtitle').html(showtitle);
            if (next_show.logo) {
                nshow.attr('style',"background-image: linear-gradient(left, rgba(243, 243, 243, 0.1) 10%, rgba(243, 243, 243, 1) 100%), url('"+next_show.logo+"');"+
                                   "background-image: -o-linear-gradient(left, rgba(243, 243, 243, 0.1) 10%, rgba(243, 243, 243, 1) 100%), url('"+next_show.logo+"');"+
                                   "background-image: -moz-linear-gradient(left, rgba(243, 243, 243, 0.1) 10%, rgba(243, 243, 243, 1) 100%), url('"+next_show.logo+"');"+
                                   "background-image: -webkit-linear-gradient(left, rgba(243, 243, 243, 0.1) 10%, rgba(243, 243, 243, 1) 100%), url('"+next_show.logo+"');"+
                                   "background-image: -ms-linear-gradient(left, rgba(243, 243, 243, 0.1) 10%, rgba(243, 243, 243, 1) 100%), url('"+next_show.logo+"');");
            } else {
                nshow.attr('style',"");
            }
        } else {
            nshow.find('#ns-showtitle').html('NOTHING ;_;');
            nshow.attr('style',"");
        }
    }
    if ($("div.nowplaying-banner").length > 0) {
        $(document).on('show_changed', update_banner);
        $(document).on('show_ended', update_banner);
        $(document).on('show_started', update_banner);
        $(document).on('nextshow_changed', update_banner);
    }
    $(document).on('show_changed', update_disco);
    $(document).on('show_ended', update_disco);
    $(document).on('show_started', update_disco);



    $.nowPlaying();
});

function pad (str, max) {
    return str.length < max ? pad("0" + str, max) : str;
}


var listeners = [];

function update_disco_listeners(new_listeners) {
    listeners.forEach(function(listener){
        if (new_listeners[listener]) {
            delete new_listeners[listener];
            //@todo lets not free some memory :3 
            //listeners.remove(listener);
        } else {
            $("div.listener").remove('#discolistener-'+listener);
        }
    });
    
    for (var listener in new_listeners) {
        var x = Math.floor(Math.random()*150);
        var y = Math.floor(Math.random()*50);
        $("div.disco").append('<div class="listener" id="discolistener-'+listener+'" style="left:'+x+'px;bottom:'+y+'px;z-index='+(100-y)+'">' +
                              '<img src="/static/img/cb/'+new_listeners[listener].countryball+'" /></div>');
        listeners.push(listener);
    }
}

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
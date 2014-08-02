// Avoid `console` errors in browsers that lack a console.
if (!(window.console && console.log)) {
    (function() {
        var noop = function() {};
        var methods = ['assert', 'clear', 'count', 'debug', 'dir', 'dirxml', 'error', 'exception', 'group', 'groupCollapsed', 'groupEnd', 'info', 'log', 'markTimeline', 'profile', 'profileEnd', 'markTimeline', 'table', 'time', 'timeEnd', 'timeStamp', 'trace', 'warn'];
        var length = methods.length;
        var console = window.console = {};
        while (length--) {
            console[methods[length]] = noop;
        }
    }());
}

// Place any jQuery/helper plugins in here.

(function ($) {
    var current_show = null;
    var next_show = null;
    var listeners = [];

    $.nowPlaying = $.nowPlaying || function () {

        function np() {
            $.getJSON('/api/site/nowplaying?full=true',function(data) {
                if (!data.success) {
                    return false;
                }
                update_disco_listeners(data.data.listener);
                if (data.data.show) {
                    if (current_show == null || current_show.id !== data.data.show.id) {
                        if (current_show == null) {
                            current_show = data.data.show;

                            $.event.trigger({
                                type: "show_started",
                                show: current_show
                            });
                        } else {
                            $.event.trigger({
                                type: "show_changed",
                                show: current_show
                            });
                        }
                    }
                } else if (current_show != null) {
                    current_show = null;
                    $.event.trigger({
                        type: "show_ended",
                        show: current_show
                    });
                }

                if (data.data.show && data.data.show.type === 'PLANNED') {
                    var progress = ((current_show.now - current_show.begin)/(current_show.end - current_show.begin))*100;
                    $.event.trigger({
                        type: "showprogess_update",
                        progress: progress
                    });
                }

                if (data.data.nextshow) {
                    if (next_show == null || next_show.id != data.data.nextshow.id) {
                        next_show = data.data.nextshow;
                        $.event.trigger({
                            type: "nextshow_changed",
                            show: next_show
                        });
                    }
                } else {
                    next_show = null;
                }
            });

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
            setTimeout(np, 5000);
        }
        np();
    };

    $.nowPlaying.get_current_show = function (){
        return current_show;
    };

    $.nowPlaying.get_next_show = function (){
        return next_show;
    };

})(jQuery);


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
      'target' : false
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
        };
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

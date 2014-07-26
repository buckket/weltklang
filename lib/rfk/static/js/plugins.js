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

    $.nowPlaying = $.nowPlaying || function () {

        function np() {
            $.getJSON('/api/site/nowplaying?full=true',function(data) {
                if (!data.success) {
                    return false;
                }
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
                    $.event.trigger({
                        type: "show_ended",
                        show: current_show
                    });
                    current_show = null;
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
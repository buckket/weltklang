$(function() {

    function request_permission() {
        // Try to get permission to show Notifications
        if (window.Notification && Notification.permission !== "granted") {
            Notification.requestPermission(function (status) {
                if (Notification.permission !== status) {
                    Notification.permission = status;
                }
            });
        }
    }

    $('#request_permission').click(function(){ request_permission(); return false; });

    function notify(input) {
        var icon_url = "/static/img/notification_medium.png";
        var title = input.show.user.names + " started streaming";
        if (input.show.name) {
            var body = "Show: " + input.show.name;
        }
        else {
            var body = "Show has no name ;_;";
        }

        if (window.Notification && Notification.permission === "granted") {
            var n = new Notification(title, {body: body, icon: icon_url, tag: 'show_start'});
        }
    }

    setTimeout(function() {
        $(document).on('show_started', notify);
        $(document).on('show_changed', notify);
    }, 5000);

});

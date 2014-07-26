
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

    request_permission();
    $('#request_permission').click(function(){ request_permission(); return false; });


    function notify(input) {
        var icon_url = "/static/img/notification_medium.png";
        var title = input.show.user.names + " started streaming";
        var body = "Show: " + input.show.name;

        if (window.Notification && Notification.permission === "granted") {
            var n = new Notification(title, {body: body, icon: icon_url, tag: 'show_start'});
        }

        // If the user hasn't told if he wants to be notified or not
        // Note: because of Chrome, we are not sure the permission property
        // is set, therefore it's unsafe to check for the "default" value.
        else if (window.Notification && Notification.permission !== "denied") {
            Notification.requestPermission(function (status) {
                if (Notification.permission !== status) {
                    Notification.permission = status;
                }

                // If the user said okay
                if (status === "granted") {
                    var n = new Notification(title, {body: body, icon: icon_url, tag: 'show_start'});
                }
            });
        }
    }

    $(document).on('show_started', notify);
    $(document).on('show_changed', notify);

});
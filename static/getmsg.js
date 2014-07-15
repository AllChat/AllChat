/**
 * Created by Derek on 2014/7/15.
 */

onmessage = function (event) {
    var user = event.data;
    var url = "/v1/messages/text/" + user + "/";
    while(true) {
        $.ajax({
            url: url,
            type: "GET",
            dataType: "json",
            timeout: 200000
        }).done(function (data, textStatus, jqXHR) {
        }).fail(function (jqXHR, textStatus, errorThrown) {
        });
    }
}
/**
 * Created by Derek on 2014/7/15.
 */

self.onmessage = function (event) {
    var user = event.data;
    var url = "/v1/messages/text/" + user + "/";
    var xmlhttp=new XMLHttpRequest();
    if(!xmlhttp) {
        throw new Error("Can't create object XMLHttpRequest");
    }
    xmlhttp.onreadystatechange = function(event) {
        if (xmlhttp.readyState==4)
        {
            if (xmlhttp.status==200)
            {
                postMessage(xmlhttp.response);
            }
            else {
                return false;
            }
        }
    };

    while(true) {
        xmlhttp.open("GET", url, false);
        xmlhttp.send(null);
    }
}
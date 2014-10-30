/**
 * Created by Derek on 2014/7/15.
 */

self.onmessage = function (event) {
    var user = event.data['user'];
    var token = event.data['token'];
    var url = "/v1/messages/text/" + user + "/";
    var xmlhttp=new XMLHttpRequest();
    if(!xmlhttp) {
        throw new Error("Can't create object XMLHttpRequest");
    }
    xmlhttp.onreadystatechange = function(event) {
        if(xmlhttp.readyState==4)
        {
            if (xmlhttp.status==200)
            {
                postMessage(xmlhttp.response);
            }
            else if((xmlhttp.status == 401) || (xmlhttp.status == 403) ) {
                postMessage("authorized");
                self.close();
            }
            else {
                return false;
            }
        }
    };

    while(true) {
        xmlhttp.open("GET", url, false);
        xmlhttp.setRequestHeader('token', token);
        xmlhttp.send(null);
    }
}
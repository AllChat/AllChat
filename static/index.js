/**
 * Created by Derek Fang on 2014/6/11.
 */

var Account = {
    createNew: function() {
        var account = {};
        var user = $.cookie('account');
        account.load_friend = function(friend) {
            $("#control-list-middle-accounts ul");
        };
        account.order_friends = function(list) {
            var online = new Array();
            var offline = new Array();
            for(var tmp = 0; tmp < list.length; tmp++) {
                if(list[tmp]['state'] === 'online') {
                    online.push(list[tmp]);
                }
                else {
                    offline.push(list[tmp]);
                }
            }
            var method = function(a, b) {
                if (a['account'] < b['account']) {
                    return -1;
                }
                else if(a['account'] == b['account']) {
                    return 0;
                }
                else{
                    return 1;
                }
            };
            online.sort(method);
            offline.sort(method);
            return online.concat(offline);
        };
        account.get_friends = function() {
            var url = "/v1/friends/" + user;
            $.ajax({
                url: url,
                contentType: "application/json; charset=UTF-8",
                type: "GET",
                dataType: "text"
            }).done(function (data, textStatus, jqXHR) {
                var list = $.evalJSON(data).friendlist;
                list = account.order_friends(list);
                for(var tmp = 0; tmp < list.length; tmp++) {
                    account.load_friend(list[tmp]);
                }
            }).fail(function (jqXHR, textStatus, errorThrown) {
                if(jqXHR.status == 404) {
                    alert("数据库故障,请重新登陆");
                }
                else if(jqXHR.status == 403) {
                    alert("用户名有误,请重新登陆");
                }
                $.removeCookie("account");
            });
        };
        return account;
    }
};

$(document).ready(function() {
    $('#chat-setting form img').on('click', function(e) {
        e.preventDefault();
        $(this).next().trigger("click");
    });
    if($.cookie('backup') && $.cookie('account')) {
        $.cookie('backup', $.cookie('account'));
    }
    else if($.cookie('backup')) {
        $.cookie('account', $.cookie('backup'));
    }
    else if($.cookie('account')) {
        $.cookie('backup', $.cookie('account'));
    }
    else {
        window.location.href = "login.html";
    }
});

$(window).unload(function(){
    $.removeCookie("account");
});



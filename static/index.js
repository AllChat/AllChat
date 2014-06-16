/**
 * Created by Derek Fang on 2014/6/11.
 */

var Account = {
    createNew: function() {
        var account = {};
        var user = $.cookie('account');
        account.load_friend = function(friend) {

        };
        account.order_friends = function(list) {

        }
        account.get_friends = function() {
            var url = "/v1/friends/" + user;
            $.ajax({
                url: url,
                contentType: "application/json; charset=UTF-8",
                type: "GET",
                dataType: "text"
            }).done(function (data, textStatus, jqXHR) {
                var list = $.evalJSON(data).friendlist;
                order_friends(list);
                for(var tmp = 0; tmp < list.length; tmp++) {
                    load_friend(tmp);
                }
            }).fail(function (jqXHR, textStatus, errorThrown) {
                if(jqXHR.status == 404) {
                    alert("数据库故障,请重新登陆");
                }
                else if(jqXHR.status == 403) {
                    alert("用户名有误，请重新登陆");
                }
                $.removeCookie("account");
            });
        };
    }
};

$(document).ready(function() {
    $('#chat-setting form img').on('click', function(e) {
        e.preventDefault();
        $(this).next().trigger("click");
    });
});

$(window).unload(function(){
    $.removeCookie("account");
});


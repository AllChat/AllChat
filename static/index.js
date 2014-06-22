/**
 * Created by Derek Fang on 2014/6/11.
 */

var Account = {
    createNew: function() {
        var account = {};
        var user;
        account.init = function() {
            account.controlListTopSetting();
            account.get_friends();
            account.openChat();
        };
        account.load_friend = function(friend) {
            var tmp = null;
            var $li = $("<li></li>").attr("id", 'user-' + friend['account']).addClass("friends");
            $li.on("mouseenter mouseleave", function(event) {
                if(event.type == "mouseenter") {
                    $(this).css("background", "rgb(203, 231, 252)");
                }
                else {
                    $(this).css("background", "none");
                }
            });
            var $img = $("<img/>").attr("src", "/static/images/user" + friend['icon'] +"-icon.jpg").addClass("icon");
            var $nickname = $("<p></p>").addClass("nickname").text(friend['nickname']);
            if (friend['state'] === "online") {
                tmp = "[在线]";
            }
            else{
                tmp = "[离线]";
            }
            var $state = $("<p></p>").addClass("state").text(tmp);
            $li.append($img).append($nickname).append($state).appendTo($("#control-list-middle-accounts ul"));
            account.bindChat($li);
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
            if(typeof(user) == "undefined") {
                user = $.cookie('account');
            }
            var url = "/v1/friends/" + user;
            $.ajax({
                url: url,
                contentType: "application/json; charset=UTF-8",
                type: "GET",
                dataType: "text"
            }).done(function (data, textStatus, jqXHR) {
                $("#control-list-middle-accounts ul").empty();
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
        account.get_groups = function() {
            var url = "/v1/groups/";
        };
        account.controlListTopSetting = function() {
            $("#control-list-top").on("click", "ul li", function(event) {
                var $select = $(this);
                if($select.hasClass("selected")) {
                    return;
                }
                var text = $select.text();
                var childrens = $("#control-list-middle-rest").children();
                for(var tmp = 0; tmp < childrens.length; tmp++) {
                    if(!$(childrens[tmp]).filter(":hidden").length) {
                        $(childrens[tmp]).css("display", "none");
                        break;
                    }
                }
                if(text == "会话记录") {
                    $("#control-list-middle-records").css("display", "block");
                }
                else if(text == "好友") {
                    $("#control-list-middle-accounts").css("display", "block");
                }
                else {
                    $("#control-list-middle-groups").css("display", "block");
                }
                $select.siblings().removeClass("selected");
                $select.addClass("selected");
            });
        };
        account.bindChat = function($li) {
            $li.on("dblclick", function(event) {
                $this = $(this)
                id = $this.attr("id");
                nickname = $this.children(".nickname").text();
                
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
    user = Account.createNew();
    user.init();
});

$(window).unload(function(){
    $.removeCookie("account");
});



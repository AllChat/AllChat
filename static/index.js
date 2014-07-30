/**
 * Created by Derek Fang on 2014/6/11.
 */

var Account = {
    createNew: function() {
        var account = {};
        var user;
        var nickname;
        var icon;
        account.init = function() {
            $.base64.utf8encode = true;
            $.base64.utf8decode = true;
            account.getSelf();
            account.controlListTopSetting();
            account.closeChat();
            account.get_friends();
            account.setFontAndSize();
            account.uploadImage();
            account.textareaSubmit();
            account.getMsg();
        };
        account.getSelf = function() {
            if(typeof(user) == "undefined") {
                user = $.cookie('account');
                nickname = $.base64.decode($.cookie("nickname"));
                icon = $.cookie('icon');
            }
            $("#icon-self").attr("src", "/static/images/user" + icon + "-icon.jpg");
            $("#account-self").html(user);
            $("#state-self").change(function(event) {
                var $this = $(this);
                var url = "/v1/accounts/" + user + "/";
                var data = {
                    "state": $this.val()
                };
                $.ajax({
                    url: url,
                    contentType: "application/json; charset=UTF-8",
                    type: "PUT",
                    data: $.toJSON(data),
                    dataType: "text"
                }).done(function (data, textStatus, jqXHR) {
                    sessionStorage.setItem("state", $this.val());
                }).fail(function (jqXHR, textStatus, errorThrown) {
                    alert("Failed to change user state");
                    $this.val(sessionStorage.getItem("state"));
                });
            }).val(sessionStorage.getItem("state"));
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
            var url = "/v1/friends/" + user;
            $.ajax({
                url: url,
                type: "GET",
                dataType: "json",
                async: false,
            }).done(function (data, textStatus, jqXHR) {
                $("#control-list-middle-accounts ul").empty();
                var list = data.friendlist;
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
                $this = $(this);
                var $chat = $("#chat");
                var id = $this.attr("id");
                var nickname = $this.children(".nickname").text();
                var chatUser = id.substr(5);
                if(id.split("-", 1)[0] != "user") {
                    return false;
                }
                $this.children("img").filter(function(index, event) {return $(event).attr("title") == "msg-reminder";}).remove();
                if($chat.css("visibility") == "hidden") {
                    $chat.stop().queue(function(next) {
                        $(this).css("visibility", "visible");
                        next();
                    });
                }
                var $ul = $("#chat-list ul");
                var create = true;
                $ul.children("li").each(function(index, element) {
                    var $element = $(element);
                    if($element.attr("id") == "list-user-" + chatUser) {
                        if($element.css("display") == "none") {
                            $element.stop().show().addClass("chat-focus");
                        }
                        else {
                            if(!$element.hasClass("chat-focus")) {
                                $element.addClass("chat-focus");
                            }
                        }
                        create = false;
                    }
                    else {
                        if($element.hasClass("chat-focus")) {
                            $element.removeClass("chat-focus");
                            var id = $element.attr("id");
                            if(id.substring(0,10) == "list-user-") {
                                account.closeChatWindow(id.substr(10));
                            }
                            else if(id.substring(0,11) == "list-group-") {
                                
                            }
                        }
                    }
                });
                if(create == true) {
                    var $li = $("<li></li>").attr("id", "list-user-" + chatUser).addClass("chat-friends chat-focus");
                    var $p = $("<p></p>").css("display", "none").text("×");
                    var $span = $("<span></span>").text(nickname);
                    $li.append($p).append($span).appendTo($ul);
                    account.closeCard($li);
                    account.addChatWindow(chatUser);
                }
                else {
                    account.openChatWindow(chatUser);
                }
            });
        };
        account.closeChat = function() {
            $("#chat-list > p").click(function(event) {
                var $chat = $("#chat");
                if($chat.css("visibility") == "visible") {
                    $chat.stop().queue(function(next) {
                        $(this).css("visibility", "hidden");
                        next();
                    });
                }
                $(this).next("ul").children("li").each(function() {
                    $(this).stop().hide();
                    var id = $(this).attr("id");
                    if(id.substring(0,10) == "list-user-") {
                        account.closeChatWindow(id.substr(10));
                    }
                    else if(id.substring(0,11) == "list-group-") {
                        
                    }
                });
            });
        };
        account.closeCard = function($li) {
            $li.on("mouseenter mouseleave", function(event) {
                if(event.type == "mouseenter") {
                    $(this).children("p").stop().show();
                }
                else {
                    $(this).children("p").stop().hide();
                }
            });
            $li.children("p").click(function(event) {
                var $tmp = $(this).closest("li");
                if($tmp.css("display") != "none") {
                    $tmp.stop().hide();
                    var id = $tmp.attr("id");
                    if(id.substring(0,10) == "list-user-") {
                        account.closeChatWindow(id.substr(10));
                    }
                    else if(id.substring(0,11) == "list-group-") {
                        
                    }
                }
                var $ul = $tmp.closest("ul");
                if($ul.children("li").length == $ul.children("li").filter(":hidden").length) {
                    if($tmp.hasClass("chat-focus")) {
                        $tmp.removeClass("chat-focus");
                    }
                    $("#chat-list > p").trigger("click");
                    return false;
                }
                if($tmp.hasClass("chat-focus")) {
                    $tmp.removeClass("chat-focus");
                    var id = $ul.children("li").not(":hidden").last().addClass("chat-focus").attr("id");
                    if(id.substring(0,10) == "list-user-") {
                        account.openChatWindow(id.substr(10));
                    }
                    else if(id.substring(0,11) == "list-group-") {
                        
                    }
                }
            });
            $li.children("span").click(function(event) {
                var $li = $(this).closest("li");
                $li.siblings("li").each(function(index, element) {
                    var $element = $(element);
                    if($element.hasClass("chat-focus")) {
                        var id = $element.removeClass("chat-focus").attr("id");
                        if(id.substring(0,10) == "list-user-") {
                            account.closeChatWindow(id.substr(10));
                        }
                        else if(id.substring(0,11) == "list-group-") {
                            
                        }
                    }
                });
                if(!$li.hasClass("chat-focus")) {
                    var id = $li.addClass("chat-focus").attr("id");
                    if(id.substring(0,10) == "list-user-") {
                        account.openChatWindow(id.substr(10));
                        $("#user-" + id.substr(10)).children("img").filter(function(index, event) {
                            return $(event).attr("title") == "msg-reminder";}).remove();
                    }
                    else if(id.substring(0,11) == "list-group-") {
                        
                    }
                }

            });
        };
        account.addChatWindow = function(id) {
            var $div = $("<div></div>").addClass("chat-records-setting").attr("id", "records-user-" + id).appendTo("#chat-records");
            $div.siblings().not(":hidden").css("display", "none");
        };
        account.closeChatWindow = function(id) {
            var $div = $("#records-user-" + id);
            if($div.not(":hidden")) {
                $div.css("display", "none");
            }
        };
        account.openChatWindow = function(id) {
            var $div = $("#records-user-" + id);
            if($div.is(":hidden")) {
                $div.css("display", "block");
            }
        };
        account.setFontAndSize = function() {
            $("#chat-input textarea").css("font-size", $("#font-size").val());
            $(".chatBox dd").css("font-size", $("#font-size").val());
            $("#font").change(function(event) {
                var value = $(this).val();
                $(".chatBox dd").css("font-family", value);
                $("#chat-input textarea").css("font-family", value);
                
            });
            $("#font-size").change(function(event) {
                var value = $(this).val();
                $(".chatBox dd").css("font-size", value + "px");
                $("#chat-input textarea").css("font-size", value + "px");
            });
        };
        account.uploadImage = function() {
            $("#image").change(function(event) {
                var reader = new FileReader();
                var file = this.files[0];
                if(file["type"].substring(0, 5) != "image") {
                    $(this).val("");
                    delete file;
                    return false;
                }
                reader.onload = function(e) {
                    var ret = e.target.result
                    var image_type;
                    var content;
                    if((ret.substring(0, 5) == "data:")) {
                        var i = 5;
                        while(ret[i++] != ";");
                        image_type = ret.substring(11, i-1);
                        content = ret.substr(i+7);
                    }
                    else {
                        $("#image").val("");
                        return false;
                    }
                    var img =  "<img src=\"" + ret + "\" />";
                    var $receiverId = $("#chat-list ul").children(".chat-focus").attr("id");
                    if($receiverId.substring(0,10) == "list-user-") {
                        var account_to = $receiverId.substr(10);
                        var url = "/v1/messages/individual";
                        var msg = new Array();
                        msg[0] = {
                            "content": content,
                            "type": image_type
                        };
                        var data = {
                            "msg": msg
                        };
                        account.addContent(account_to, nickname, img);
                        $.ajax({
                            url: url,
                            contentType: "application/json; charset=UTF-8",
                            type: "POST",
                            data: $.toJSON(data),
                            headers: {"message_sender": user, "message_receiver": account_to},
                            dataType: "text"
                        }).done(function (data, textStatus, jqXHR) {
                        }).fail(function (jqXHR, textStatus, errorThrown) {
                            $("#records-user-" + account_to).children("dl").last().children("dt").append($("<span>发送失败</span>")
                            .css({"color": "red", "padding": "0px 2px", "margin": "0px 0px 0px 10px", "background-color": "red"}));
                        });
                    }
                    else if($receiverId.substring(0,11) == "list-group-") {

                    }
                    $("#image").val("");
                }
                reader.readAsDataURL(file);
            });
        };
        account.textareaSubmit = function() {
            $("#chat-input").children("button").eq(1).on("click", function(event) {
                var content = $(this).siblings("textarea").val();
                if(content.length) {
                    var $receiver = $("#chat-list ul").children(".chat-focus");
                    if($receiver.length != 0) {
                        var id = $receiver.attr("id");
                        if(id.substring(0,10) == "list-user-") {
                            var account_to = id.substr(10);
                            var url = "/v1/messages/individual";
                            var msg = new Array();
                            msg[0] = {
                                "content": content,
                                "type": "text"
                            };
                            var data = {
                                "msg": msg
                            };
                            $(this).siblings("textarea").val("");
                            account.addContent(account_to, nickname, content);
                            $.ajax({
                                url: url,
                                contentType: "application/json; charset=UTF-8",
                                type: "POST",
                                data: $.toJSON(data),
                                headers: {"message_sender": user, "message_receiver": account_to},
                                dataType: "text"
                            }).done(function (data, textStatus, jqXHR) {
                            }).fail(function (jqXHR, textStatus, errorThrown) {
                                $("#records-user-" + account_to).children("dl").last().children("dt").append($("<span>发送失败</span>")
                                .css({"color": "red", "padding": "0px 2px", "margin": "0px 0px 0px 10px", "background-color": "red"}));
                            });
                        }
                        else if(id.substring(0,11) == "list-group-") {
                            var group_to = id.substr(11);
                            var url = "/v1/messages/group";
                        }
                    }
                }
            });
            $("#chat-input textarea").on("focus blur", function(event) {
                enter = function(event) {
                    if(event.keyCode == 13) {
                        var content = $("#chat-input textarea").val();
                        $("#chat-input textarea").val(content.substring(0, content.length - 1));
                        $(this).parent().children("button").eq(1).trigger("click");
                    }
                };
                if(event.type == "focus") {
                    if(!$._data(this, "events")["keyup"]) {
                        $(this).on("keyup.enter", enter);
                    }
                }
                else {
                    $(this).off(".enter");
                }
            });
        };
        account.addContent = function(id, name, content, timestr) {
            if(typeof(timestr) == "undefined") {
                var now = new Date();
                timestr = now.toLocaleDateString() + " " + now.getHours() + ":" + now.getMinutes() + ":" + now.getSeconds();
            }
            var $dl = $("<dl></dl>").addClass("chatBox");
            var $dt = $("<dt></dt>").addClass("chatBox-head").attr("title", name).text(name).append($("<span></span>").css("margin-left", "5px").text(timestr));
            var $dd = $("<dd></dd>").addClass("charBox-msg").html(content);
            $dl.append($dt).append($dd).appendTo($("#records-user-" + id));
            $("#records-user-" + id).get(0).scrollTop = $("#records-user-" + id).get(0).scrollHeight;
        };
        account.getMsg = function() {
            if(typeof(Worker)!=="undefined") {
                var worker =new Worker("/static/getmsg.js");
                worker.onmessage = function(event) {
                    var msg = $.evalJSON(event.data);
                    var method = msg["method"];
                    switch(method) {
                        case "send_group_message":
                            break;
                        case "send_individual_message":
                            var from = msg['args']['account'];
                            var time = msg['args']['time'];
                            var message = msg['args']['msg'];
                            account.get_individual_message(from, time, message);
                            break;
                        case "add_friend_resp":
                            break;
                        case "add_friend_req":
                            break;
                        default:
                            break;
                    }
                };
                worker.onerror = function(event) {
                    throw event.data;
                }
                worker.postMessage(user);
            }
        }
        account.get_individual_message = function(from, time, msg) {
            var exist = false;
            var $listUser = $("#list-user-" + from);
            if($("#user-" + from).length != 0) {
                if(!($listUser.length != 0 && $listUser.hasClass("chat-focus"))
                    &&($("#user-" + from).children("img").filter(function(index, event) {return $(event).attr("title") == "msg-reminder";}).length == 0)) {
                    $("<img src='/static/images/msg-reminder.png'/>").css({
                        "position": "absolute",
                        "padding": "0",
                        "margin": "0",
                        "width": "8px",
                        "height": "8px",
                        "left": "48px",
                        "top": "1px"
                    }).attr("title", "msg-reminder").prependTo($("#user-" + from));
                }
                exist = true;
            }
            if(!exist) {
                return false;
            }
            if($listUser.length == 0) {
                var $li = $("<li></li>").attr("id", "list-user-" + from)
                    .css("display", "none").addClass("chat-friends");
                var $p = $("<p></p>").css("display", "none").text("×");
                var $span = $("<span></span>").text(nickname);
                $li.append($p).append($span).appendTo($("#chat-list ul"));
                account.closeCard($li);
                $("<div></div>").addClass("chat-records-setting").css("display", "none")
                    .attr("id", "records-user-" + from).appendTo("#chat-records");
            }
            var timeTmp = new Date();
            timeTmp = new Date(Date.parse(time.replace(/[-]/g, "/")) - timeTmp.getTimezoneOffset()*60000);
            time = timeTmp.toLocaleDateString() + " " + timeTmp.getHours() + ":" + timeTmp.getMinutes() + ":" + timeTmp.getSeconds();
            var content = "";
            var img = new Array();
            for(var i=0; i<msg.length; i++) {
                if(msg[i]['type'] == "text") {
                    content += msg[i]['content'];
                }
                else if(['jpg', 'png', 'bmp', 'gif', 'psd', 'jpeg'].indexOf(msg[i]['type'])) {
                    content += "<img src='/static/images/loading.gif' id='" + msg[i]['content'].split(".", 2)[0] + "'/>";
                    img.push(msg[i]['content']);
                }
            }
            account.addContent(from, $("#user-" + from).find(".nickname").eq(0).text(), content, time);
            for(var i=0; i<img.length; i++) {
                var callback = function(name) {
                    var url = "/v1/messages/image/" + user + "/" + name;
                    $.ajax({
                        url: url,
                        type: "GET",
                        dataType: "json"
                    }).done(function (data, textStatus, jqXHR) {
                        var src = "data:image/" + data['type'] + ";base64," + data['content'];
                        $("#" + name.split(".", 2)[0]).attr("src", src);
                    }).fail(function (jqXHR, textStatus, errorThrown) {
                        $("#"+img[i]).attr("src", "/static/images/failed.jpg");
                    });
                };
                setTimeout(callback(img[i]), 0);
            }
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
    var user = Account.createNew();
    user.init();
});

$(window).unload(function(){
    var data = {
        "state":"offline"
    };
    $.ajax({
        url: "/v1/login/" + $.cookie('account'),
        contentType: "application/json; charset=UTF-8",
        type: "POST",
        async:false,
        timeout: 2000,
        data: $.toJSON(data),
        dataType: "text"
    }).always(function (jqXHR, textStatus, errorThrown) {
        $.removeCookie('account');
    });

});



/**
 * Created by Derek Fang on 2014/6/11.
 */

var Account = {
    createNew: function() {
        var account = {};
        var user;
        var nickname;
        account.init = function() {
            $.base64.utf8encode = true;
            $.base64.utf8decode = true;
            account.controlListTopSetting();
            account.closeChat();
            account.get_friends();
            account.setFontAndSize();
            account.uploadImage();
            account.textareaSubmit();
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
                nickname = $.base64.decode($.cookie("nickname"));
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
                $this = $(this);
                var $chat = $("#chat");
                var id = $this.attr("id");
                var nickname = $this.children(".nickname").text();
                var chatUser = id.substr(5);
                if(id.split("-", 1)[0] != "user") {
                    return false;
                }
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
                        image_type = ret.substring(10, i-1);
                        content = ret.substr(i+7);
                    }
                    else {
                        $("#image").val("");
                        delete file;
                        return false;
                    }
                    var img =  "<img src=\"" + ret + "\" />";
                    var $receiverId = $("#chat-list ul").children(".chat-focus").attr("id");
                    if($receiverId.substring(0,10) == "list-user-") {
                        var account_to = $receiverId.substr(10);
                        var url = "/messages/individual";
                        var msg = new Array();
                        msg[0] = {
                            "content": content,
                            "type": image_type
                        };
                        var data = {
                            "msg": msg
                        };
                        account.addContent(account_to, nickname, img);
                    }
                    else if($receiverId.substring(0,11) == "list-group-") {

                    }
                    $("#image").val("");
                    delete file;
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
                            var url = "/messages/individual";
                            var data = {};
                            $(this).siblings("textarea").val("");
                            account.addContent(account_to, nickname, content);
//                          $.ajax({
//                              url: url,
//                              contentType: "application/json; charset=UTF-8",
//                              type: "POST",
//                              data: $.toJSON(data),
//                              dataType: "text"
//                          }).done(function (data, textStatus, jqXHR) {
//                          }).fail(function (jqXHR, textStatus, errorThrown) {
//                          });
                        }
                        else if(id.substring(0,11) == "list-group-") {
                            var group_to = id.substr(11);
                            var url = "/messages/group";
                        }
                    }
                }
            });
        };
        account.addContent = function(id, name, content) {
            var now = new Date();
            var timestr = now.toLocaleDateString() + " " + now.getHours() + ":" + now.getMinutes() + ":" + now.getSeconds();
            var $dl = $("<dl></dl>").addClass("chatBox");
            var $dt = $("<dt></dt>").addClass("chatBox-head").attr("title", name).text(name).append($("<span></span>").css("margin-left", "5px").text(timestr));
            var $dd = $("<dd></dd>").addClass("charBox-msg").html(content);
            $dl.append($dt).append($dd).appendTo($("#records-user-" + id));
            $("#records-user-" + id).get(0).scrollTop = $("#records-user-" + id).get(0).scrollHeight;
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
    $.removeCookie("account");
});



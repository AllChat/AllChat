/**
 * Created by Derek Fang on 2014/6/11.
 */

function error401(xhr) {
    window.location.href = "login.html";
}

function error403(xhr) {
    window.location.href = "login.html";
}

var user;
var nickname;
var icon;
var token;
var state;

var Account = {
    createNew: function() {
        var account = {};
        account.init = function() {
            $.base64.utf8encode = true;
            $.base64.utf8decode = true;
            account.getSelf();
            account.controlListTopSetting();
            account.closeChat();
            account.get_friends();
            account.get_groups();
            account.setFontAndSize();
            account.uploadImage();
            account.textareaSubmit();
            account.init_setup_button();
            account.init_search_button();
            account.init_message_center();
            account.bind_get_history();
            account.getMsg();
        };
        account.getSelf = function() {
            if(typeof(user) == "undefined") {
                user = sessionStorage.getItem("account");
                sessionStorage.removeItem("account");
                nickname = $.base64.decode(sessionStorage.getItem("nickname"));
                sessionStorage.removeItem("nickname");
                icon = sessionStorage.getItem('icon');
                sessionStorage.removeItem("icon");
                state = sessionStorage.getItem('state');
                sessionStorage.removeItem("state");
                token = sessionStorage.getItem('token');
                sessionStorage.removeItem("token");
            }
            $.ajax({
                    url: "/v1/login/" + user + "/",
                    type: "GET",
                    headers: {"token":token},
                    dataType: "text",
                    async: false,
                    statusCode: {
                        401: error401,
                        403: error403
                    }
                }).always(function (data, textStatus, jqXHR) {
                });
            $("#icon-self").attr("src", "/static/images/head/" + icon + ".jpg");
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
                    headers: {"token":token},
                    dataType: "text",
                    statusCode: {
                        401: error401,
                        403: error403
                    }
                }).done(function (data, textStatus, jqXHR) {
                    state = $this.val();
                }).fail(function (jqXHR, textStatus, errorThrown) {
                    alert("Failed to change user state");
                });
            }).val(state);
        };
        account.add_action_button = function($li){
            $button = $("<div></div>").addClass("btn").addClass("delete").css("display","none").append("<p>刪除</p>");
            $button.on("click", function(event){
                event.stopPropagation();
                $.ajax({
                    url: "/v1/friends/" + user,
                    type: "DELETE",
                    contentType: "application/json; charset=UTF-8",
                    data: $.toJSON({"account":$(this).parent().attr("id").slice(5),"bidirectional":"true"}),
                    headers: {"token":token},
                    async: false,
                    statusCode: {
                        401: error401,
                        403: error403
                    }
                }).done(function (data, textStatus, jqXHR){
                    account.get_friends();
                    alert("成功刪除好友");
                }).fail(function (jqXHR, textStatus, errorThrown){
                    alert("删除好友失败，请重试");
                });
            });
            $li.append($button);
        }
        account.load_friend = function(friend) {
            var tmp = null;
            var $li = $("<li></li>").attr("id", 'user-' + friend['account']).addClass("friends");
            var $img = $("<img/>").attr("src", "/static/images/head/" + friend['icon'] +".jpg").addClass("icon");
            var $nickname = $("<p></p>").addClass("nickname").text(friend['nickname']);
            if (friend['state'] === "online") {
                tmp = "[在线]";
            }
            else{
                tmp = "[离线]";
            }
            var $state = $("<p></p>").addClass("state").text(tmp);
            account.add_action_button($li);
            $li.append($img).append($nickname).append($state).appendTo($("#control-list-middle-accounts ul"));
            account.bindChat($li);
            $li.on("click", "img" ,function(event){
                event.stopPropagation();
                $li.children("div.btn").toggle(600);
            });
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
                headers: {"token":token},
                async: false,
                statusCode: {
                    401: error401,
                    403: error403
                }
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
        account.load_group = function(group_id,group_name){
            var $li = $("<li></li>").attr('id','group-'+group_id).addClass('group');
            var $img = $("<img />").attr('src','/static/images/group.jpg').addClass('icon');
            var $groupname = $("<p></p>").addClass('groupname').text(group_name);
            $li.append($img).append($groupname).appendTo($("#control-list-middle-groups ul"));
            account.bindChat($li);
        };
        account.get_groups = function() {
            var url = "/v1/groups/";
            $.ajax({
                type: 'GET',
                url: url,
                dataType: 'json',
                headers: {'group_id':0,'account':user,"token":token},
                async: false,
                statusCode: {
                    401: error401,
                    403: error403
                }
            }).done(function (data,textStatus,jqXHR){
                $("#control-list-middle-groups ul").empty();
                $.each(data,function (key,value){
                    account.load_group(key,value["name"]);
                });
            }).fail(function (jqXHR){
                if(jqXHR.status == 503){
                    alert("数据库故障,请重新登陆");
                }else if(jqXHR.status == 404){
                    alert("用户名有误,请重新登陆");
                }
            });
        };
        account.get_group_member = function(groupID,div){
            var url = "/v1/groups/";
            $.ajax({
                type: "GET",
                url: url,
                dataType: "json",
                headers: {"group_id":groupID,"account":user, "token":token},
                statusCode: {
                    401: error401,
                    403: error403
                }
            }).done(function (data){
                $switcher = $("<div></div>").addClass("group-members-switcher");
                $switcher.append($("<div></div>").addClass("triangle-left"));
                $member_list = $("<ul></ul>");
                $.each(data,function (key,value){
                    if(value["state"]=="online"){value["state"]="[在线]"}else{value["state"]="[离线]"}
                    $("<li></li>").attr("title",key)
                    .append($("<img/>").attr("src","/static/images/head/" + value['icon'] +".jpg"))
                    .append($("<p></p>").text(value["nickname"])).append($("<p></p>").text(value["state"]))
                    .appendTo($member_list);
                });
                div.append($switcher).append($member_list);
                $switcher.on("click",function(event){
                    event.stopPropagation();
                    if($(this).parent().css("right")=="-150px"){
                        $(this).parent().animate({right:"0px"},500);
                        $(this).children(0).attr("class","triangle-right");
                    }else{
                        $(this).parent().animate({right:"-150px"},500);
                        $(this).children(0).attr("class","triangle-left");
                    }
                });
            }).fail(function (jqXHR){
                alert(jqXHR.responseText);
            });
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
                var chatTo = id.split("-")[1];
                var name = "";
                var chatList = "";
                var chatRecord = "";
                if(id.split("-", 1)[0] == "user") {
                    name = $this.children(".nickname").text();
                    chatList = "list-user-";
                    chatRecord = "records-user-";
                }else if(id.split("-", 1)[0] == "group"){
                    name = $this.children(".groupname").text();
                    chatList = "list-group-";
                    chatRecord = "records-group-";
                }else{
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
                    if($element.attr("id") == chatList + chatTo) {
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
                            var chatRecordId = $element.attr("id").replace("list","records");
                            account.closeChatWindow(chatRecordId);
                        }
                    }
                });
                if(create == true) {
                    var $li = $("<li></li>").attr("id", chatList + chatTo).addClass("chat-friends chat-focus");
                    var $p = $("<p></p>").css("display", "none").text("×");
                    var $span = $("<span></span>").text(name);
                    $li.append($p).append($span).appendTo($ul);
                    account.closeCard($li);
                    account.addChatWindow(chatRecord + chatTo);
                }
                else {
                    account.openChatWindow(chatRecord + chatTo);
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
                    var id = $(this).attr("id").replace("list","records");
                    account.closeChatWindow(id);
                    if($(this).hasClass("chat-focus")) {
                        $(this).removeClass("chat-focus")
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
                    var id = $tmp.attr("id").replace("list","records");
                    account.closeChatWindow(id);
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
                    var id = $ul.children("li").not(":hidden").last().addClass("chat-focus").attr("id").replace("list","records");
                    account.openChatWindow(id);
                }
            });
            $li.on("click", function(event){
                event.stopPropagation();
                if(!$(this).is("p")){
                    var $li = $(this).closest("li");
                    $li.siblings("li").each(function(index, element) {
                        var $element = $(element);
                        if($element.hasClass("chat-focus")) {
                            var id = $element.removeClass("chat-focus").attr("id").replace("list","records");
                            account.closeChatWindow(id);
                        }
                    });
                    if(!$li.hasClass("chat-focus")) {
                        var id = $li.addClass("chat-focus").attr("id").replace("list","records");
                        account.openChatWindow(id);
                        $(id.replace("list-","#")).children("img").filter(function(index, event) {
                                return $(event).attr("title") == "msg-reminder";}).remove();
                    }
                }
            });
        };
        account.addChatWindow = function(id) {
            var $div = $("<div></div>").addClass("chat-records-setting").attr("id", id);
            if(id.split('-')[1]=='group'){
                $content = $("<div></div>").attr("id",id.replace("records","content")).addClass(
                    "chat-records-content");
                $members = $("<div></div>").addClass("group-members");
                account.get_group_member(id.split('-')[2],$members);
                $div.append($content).append($members);
            }
            $div.appendTo("#chat-records");
            $div.siblings().not(":hidden").css("display", "none");
        };
        account.closeChatWindow = function(id) {
            var $div = $("#" + id);
            if($div.not(":hidden")) {
                $div.css("display", "none");
            }
        };
        account.openChatWindow = function(id) {
            var $div = $("#" + id);
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
            $("#image-select-icon").on("click", function(event){
                $("#image").click();
            });
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
                        account.addContent('records-user-'+account_to, nickname, img);
                        $.ajax({
                            url: url,
                            contentType: "application/json; charset=UTF-8",
                            type: "POST",
                            data: $.toJSON(data),
                            headers: {"message_sender": user, "message_receiver": account_to, "token":token},
                            dataType: "text",
                            statusCode: {
                                401: error401,
                                403: error403
                            }
                        }).done(function (data, textStatus, jqXHR) {
                        }).fail(function (jqXHR, textStatus, errorThrown) {
                            $("#records-user-" + account_to).children("dl").last().children("dt").append($("<span>发送失败</span>")
                            .css({"color": "red", "padding": "0px 2px", "margin": "0px 0px 0px 10px", "background-color": "red"}));
                        });
                    }
                    else if($receiverId.substring(0,11) == "list-group-") {
                        var groupid = $receiverId.split("-")[2];
                        var url = "/v1/messages/group";
                        var msg = new Array();
                        msg[0] = {
                            "content": content,
                            "type": image_type
                        };
                        var data = {
                            "msg": msg
                        };
                        account.addContent($receiverId.replace("list","content"), nickname, img);
                        $.ajax({
                            url: url,
                            contentType: "application/json; charset=UTF-8",
                            type: "POST",
                            data: $.toJSON(data),
                            headers: {"message_sender": user, "group_id": groupid, "token":token},
                            dataType: "text",
                            statusCode: {
                                401: error401,
                                403: error403
                            }
                        }).done(function (data, textStatus, jqXHR) {
                        }).fail(function (jqXHR, textStatus, errorThrown) {
                            $("#" + $receiverId.replace("list","records")).children("dl").last().children("dt").append($("<span>发送失败</span>")
                            .css({"color": "red", "padding": "0px 2px", "margin": "0px 0px 0px 10px", "background-color": "red"}));
                        });
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
                            account.addContent('records-user-'+account_to, nickname, content);
                            $.ajax({
                                url: url,
                                contentType: "application/json; charset=UTF-8",
                                type: "POST",
                                data: $.toJSON(data),
                                headers: {"message_sender": user, "message_receiver": account_to, "token":token},
                                dataType: "text",
                                statusCode: {
                                    401: error401,
                                    403: error403
                                }
                            }).done(function (data, textStatus, jqXHR) {
                            }).fail(function (jqXHR, textStatus, errorThrown) {
                                $("#records-user-" + account_to).children("dl").last().children("dt").append($("<span>发送失败</span>")
                                .css({"color": "red", "padding": "0px 2px", "margin": "0px 0px 0px 10px", "background-color": "red"}));
                            });
                        }
                        else if(id.substring(0,11) == "list-group-") {
                            var groupid = id.split("-")[2];
                            var url = "/v1/messages/group";
                            var msg = new Array();
                            msg[0] = {
                                "content": content,
                                "type": "text"
                            };
                            var data = {
                                "msg": msg
                            };
                            $(this).siblings("textarea").val("");
                            account.addContent(id.replace("list","content"), nickname, content);
                            $.ajax({
                                url: url,
                                contentType: "application/json; charset=UTF-8",
                                type: "POST",
                                data: $.toJSON(data),
                                headers: {"message_sender": user, "group_id": groupid, "token":token},
                                dataType: "text",
                                statusCode: {
                                    401: error401,
                                    403: error403
                                }
                            }).done(function (data, textStatus, jqXHR) {
                            }).fail(function (jqXHR, textStatus, errorThrown) {
                                $("#" + id.replace("list","records")).children("dl").last().children("dt").append($("<span>发送失败</span>")
                                .css({"color": "red", "padding": "0px 2px", "margin": "0px 0px 0px 10px", "background-color": "red"}));
                            });
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
                timestr = now.toLocaleDateString() + " " + now.toTimeString().split(" ")[0];
            }
            var $dl = $("<dl></dl>").addClass("chatBox");
            var $dt = $("<dt></dt>").addClass("chatBox-head").attr("title", name).text(name).append($("<span></span>").css("margin-left", "5px").text(timestr));
            var $dd = $("<dd></dd>").addClass("charBox-msg").html(content);
            $dl.append($dt).append($dd).appendTo($("#" + id));
            $("#" + id).get(0).scrollTop = $("#" + id).get(0).scrollHeight;
        };
        account.init_setup_button = function(){
            $("body").on("click", "div", function(event){
                event.stopPropagation();
                if($(this).attr("id")=="setup-icon"){
                    if($('div.search-add-bar').css('display')=='block'){$('div.search-add-bar').toggle();};
                    $('div.setup-list').toggle(600);
                }else if($(this).attr("id")=="personal-info"){
                    account.setupPersonalInfo();
                }else if($(this).attr("id")=="change-password"){
                    account.changePassword();
                }else if($(this).attr("id")=="about-us"){
                    account.showAbout();
                }
            });
        };
        account.setupPersonalInfo = function(){
            $('.setup-list').toggle();
            account.createDialog('personal-info','个人信息');
            account.constructInfoDialog();
            $('div.personal-info-head img').attr('src',$('#icon-self').attr('src'));
        }
        account.createDialog = function(dialogID,title){
            if($('.info-dialog').length>0){ $('.info-dialog').remove(); }
            var $dialog = $('<div></div>').attr('id',dialogID+'-dialog').addClass('info-dialog');
            var $title = $('<div></div>').addClass('dialog-title').append($('<p></p>').text(title));
            var $closeTab = $('<div></div>').addClass('dialog-close').append($('<img/>').attr('src','../static/images/icon/close.png'));
            var $list = $('<div></div>').attr('id',dialogID+'-list').addClass('dialog-content');
            $dialog.append($title).append($closeTab).append($list).appendTo($('#layer'));
            account.bindClose($closeTab);
        }
        account.bindClose = function($div){
            $div.on('click',function(event){
                event.stopPropagation();
                $div.parent().remove();
            });
        }
        account.constructInfoDialog = function(){
            $head = $('<div></div>').addClass('personal-info-head');
            $head.append($('<p></p>').text('头像')).append('<img/>').append($('<button></button>').text('更换'));
            $nickname = $('<div></div>').addClass('personal-info-nickname');
            $nickname.append($('<p></p>').text('昵称')).append('<input/>');
            $email = $('<div></div>').addClass('personal-info-email');
            $email.append($('<p></p>').text('邮箱')).append('<input/>');
            $submit = $('<button></button>').attr('id','personal-info-submit').text('确认');
            $('#personal-info-list').append($head).append($nickname).append($email).append($submit);
            $submit.on('click',function(event){
                event.stopPropagation();
                var icon_up = $('div.personal-info-head img').attr('src').split('head/')[1].split('.')[0];
                var nickname_up = $('div.personal-info-nickname input').val();
                var email = $('div.personal-info-email input').val();
                var modifiedInfo = {'icon':icon_up};
                if(nickname.length>0){modifiedInfo['nickname']=nickname_up};
                if(email.length>0){modifiedInfo['email']=email};
                $.ajax({
                    type: 'PUT',
                    url: '/v1/accounts/'+user+'/',
                    contentType: 'application/json; charset:utf-8',
                    headers: {"token":token},
                    data: $.toJSON(modifiedInfo),
                    dataType: 'text',
                    statusCode: {
                        401: error401,
                        403: error403
                    }
                }).done(function (data){
                    icon = icon_up;
                    $('#icon-self').attr('src',"/static/images/head/" + icon + ".jpg");
                    alert('个人信息修改成功');
                }).fail(function (jqXHR){
                    alert(jqXHR.responseText);
                });
            });
            $head.on("click", "button" , function(event){
                event.stopPropagation();
                $displayIcons = $('<div></div>').attr('id','head-options').css({"width":"290px","height":"155px","position":"absolute",
                "top":"20px","left":"40px","border":"2px","padding":"2px","background-color":"#fff","overflow-y":"auto"});
                for (var i=0;i<6;i++){
                    $displayIcons.append($('<img/>').attr('src',"/static/images/head/" + i + ".jpg").css({
                        "width":"60px","height":"60px","padding":"0px","margin-left":"10px","margin-top":"10px"
                    }));
                }
                $displayIcons.appendTo($('div.dialog-content'));
                $('#head-options img').on('click',function(event){
                    event.stopPropagation();
                    $('div.personal-info-head img').attr('src',$(this).attr('src'));
                    $('#head-options').remove();
                    $('#head-options img').off('click');
                });
            });
        }
        account.changePassword = function(){
            $('.setup-list').toggle();
            account.createDialog('change-password','修改密码');
            account.constructPasswordDialog();
        }
        account.constructPasswordDialog = function(){
            $oldpassword = $('<div></div>').attr('id','password-head').addClass('password-input');
            $oldpassword.append($('<p></p>').text('原密码')).append('<input id="oldpassword" type="password"/>');
            $newpassword = $('<div></div>').addClass('password-input');
            $newpassword.append($('<p></p>').text('新密码')).append('<input id="newpassword" type="password"/>');
            $newconfirm = $('<div></div>').addClass('password-input');
            $newconfirm.append($('<p></p>').text('确认')).append('<input id="newconfirm" type="password"/>');
            $submit = $('<button></button>').attr('id','change-password-submit').text('确认');
            $('#change-password-list').append($oldpassword).append($newpassword).append($newconfirm).append($submit);
            $submit.on('click',function(event){
                event.stopPropagation();
                var oldpassword = $('#oldpassword').val();
                var newpassword = $('#newpassword').val();
                var newconfirm = $('#newconfirm').val();
                if(newpassword!=newconfirm){
                    alert('两次输入的新密码不一致');
                }else if(oldpassword.length==0 || newpassword.length==0 || newconfirm.length==0){
                    alert('请确认所有输入框不为空');
                }else{
                    $.ajax({
                        type: 'PUT',
                        url: '/v1/accounts/'+user+'/',
                        contentType: 'application/json; charset:utf-8',
                        headers: {"token":token},
                        data: $.toJSON({'new_password':newpassword,'old_password':oldpassword}),
                        dataType: 'text',
                        statusCode: {
                            401: error401,
                            403: error403
                        }
                    }).done(function (data){
                        alert('密码修改成功！');
                    }).fail(function (jqXHR){
                        alert(jqXHR.responseText);
                    });
                }
            });
        }
        account.showAbout = function(){
            $('.setup-list').toggle();
            account.createDialog('about-allchat','关于allchat');
            $('#about-allchat-list').append($('<p></p>').text('Allchat 1.0').css({"margin-top":"30px","margin-left":"20px"})).append(
                $('<p></p>').text('Author: Derake, Alex').css("margin-left","20px")).append(
                $('<p></p>').text('Copyright© 2014-2020. All rights reserved.').css("margin-left","20px"));
        }
        account.init_search_button = function(){
            $("body").on("click","#search-icon",function(event){
                event.stopPropagation();
                if($("div.setup-list").css("display")=="block"){$("div.setup-list").toggle();};
                $("div.search-add-bar").toggle(600);
            });
            $("div.add-bar").on("click", "img" ,function(event){
                event.stopPropagation();
                if($(this).attr("id")=="fast-add-button"){
                    var username = $("#add-username").val();
                    account.addFriendRequest(username);
                }else if($(this).attr("id")=="search-user-button"){
                    account.searchUser();
                }else if($(this).attr("id")=="create-group-button"){
                    account.createGroup();
                }else if($(this).attr("id")=="search-group-button"){
                    account.searchGroup();
                }
            });
        }
        account.addFriendRequest = function(username){
            if(username.length==0){
                alert('请输入用户名后再提交！');
            }else{
                var pattern = /^[\w!@#$%^&*_.]+$/;
                if (!pattern.test(username)){alert('亲，您的关键字包含我们不支持的字符哦，换掉试试吧~');}
                else{
                    $.ajax({
                        type: 'POST',
                        url: '/v1/friends/'+user+'/',
                        contentType: "application/json; charset=UTF-8",
                        headers: {"token":token},
                        data: $.toJSON({'account':username,'message':'this is '+user}),
                        dataType: 'text',
                        statusCode: {
                            401: error401,
                            403: error403
                        }
                    }).done(function (data){
                        alert(data);
                    }).fail(function (jqXHR){
                        alert(jqXHR.responseText);
                    });
                }
            }
        }
        account.searchUser = function(){
            var keyword = $('#search-username').val();
            if(keyword.length==0){
                alert('搜索关键字不能为空');
            }else{
                var pattern = /^[\w!@#$%^&*_.]+$/;
                if (!pattern.test(keyword)){alert('亲，您的关键字包含我们不支持的字符哦，换掉试试吧~');}
                else{
                    $.ajax({
                        type: 'GET',
                        url: '/v1/accounts/'+keyword+'/?mysql_like=1',
                        headers: {"token":token},
                        dataType: 'json',
                        statusCode: {
                            401: error401,
                            403: error403
                        }
                    }).done(function (data){
                        if(data.accounts.length==0){
                            alert('很遗憾，没有找到匹配的结果，换个关键字试试吧～');
                        }else{
                            var type = 'user';
                            account.showSearchResult(data,type);
                        }
                    }).fail(function (jqXHR){
                        alert(jqXHR.responseText);
                    });
                }
            }
        }
        account.showSearchResult = function(data,type){
            account.createDialog("search-result","搜索结果");
            if(type=="user"){
                values=data.accounts;
            }else if(type=="group"){
                values=data.groups;
            }
            $result_list = $("<ul></ul>");
            $.each(values,function(index,value){
                $item = account.createListItem(value,type);
                $result_list.append($item);
            });
            $result_list.on("click","button.search-result-addbutton",function(event){
                event.stopPropagation();
                var username = $(this).siblings(".search-result-username").text();
                account.addFriendRequest(username);
            });
            $result_list.on("click","button.search-result-joinbutton",function(event){
                event.stopPropagation();
                var groupid = $(this).siblings(".search-result-groupid").text();
                var groupowner = $(this).siblings(".search-result-groupowner").text();
                account.joinGroupRequest(groupid,groupowner);
            });
            $("#search-result-list").append($result_list);
        }
        account.createListItem = function(value,type){
            var $li = $('<li></li>');
            if(type=='user'){
                $username = $('<p></p>').addClass('search-result-username').text(value['account']);
                $nickname = $('<p></p>').addClass('search-result-nickname').text(value['nickname']);
                $state = $('<p></p>').addClass('search-result-state').text(value['state']);
                $icon = $('<img/>').addClass('search-result-icon').attr('src',"/static/images/head/"+value['icon']+".jpg");
                $li.append($username).append($nickname).append($state).append($icon);
                $li.append('<button class="search-result-addbutton">加为好友</button>');
            }else if(type=='group'){
                $groupname = $('<p></p>').addClass('search-result-groupname').text(value['group_name']);
                $groupid = $('<p></p>').addClass('search-result-groupid').text(value['group_id']);
                $groupowner = $('<p></p>').addClass('search-result-groupowner').text(value['group_owner']);
                $groupsize = $('<p></p>').addClass('search-result-groupsize').text(value['group_size']);
                $li.append($groupname).append($groupid).append($groupowner).append($groupsize);
                $li.append('<button class="search-result-joinbutton">申请加入</button>');
            }
            return $li;
        }
        account.joinGroupRequest = function(groupid,groupowner){
            if(user==groupowner){
                alert('您已经是群主了，别闹~');
            }else{
                $.ajax({
                    type: 'PUT',
                    url: '/v1/groups/'+groupid+'/',
                    contentType: 'application/json; charset=utf-8',
                    headers: {"token":token},
                    data: $.toJSON({'account':user,'operation':'join'}),
                    dataType:'text',
                    statusCode: {
                        401: error401,
                        403: error403
                    }
                }).done(function (data){
                    alert('申请成功啦，等着好消息吧~');
                }).fail(function (jqXHR){
                    alert(jqXHR.responseText);
                });
            }
        }
        account.createGroup = function(){
            var groupname = $('#create-group-name').val();
            if(groupname.length==0){
                alert('群名称还没填呢，再想想吧~');
            }else{
                $.ajax({
                    type: 'POST',
                    url: '/v1/groups/',
                    contentType: 'application/json; charset=UTF-8',
                    headers: {"token":token},
                    data: $.toJSON({'account':user,'group_name':groupname}),
                    dataType: 'text',
                    statusCode: {
                        401: error401,
                        403: error403
                    }
                }).done(function (data){
                    alert('您的群创建成功了，快去拉几个小弟进来吧~');
                }).fail(function (jqXHR){
                    alert(jqXHR.responseText);
                });
            }
        }
        account.searchGroup = function(){
            var keyword = $('#search-group-name').val();
            if(keyword.length==0){
                alert('搜索关键字不能为空');
            }else{
                $.ajax({
                    type: 'POST',
                    url: '/v1/groups/search/',
                    contentType: 'application/json; charset=utf-8',
                    headers: {"token":token},
                    data: $.toJSON({'keyword':keyword,'account':user,'type':'uncertain','offset':0}),
                    dataType: 'json',
                    statusCode: {
                        401: error401,
                        403: error403
                    }
                }).done(function (data){
                    if(data.result_size==0){
                        alert('很遗憾，没有找到匹配的结果，换个关键字试试吧～');
                    }else{
                        var type = 'group';
                        account.showSearchResult(data,type);
                    }
                }).fail(function (jqXHR){
                    alert('服务器开小差了，sorry!');
                });
            }
        }
        account.init_message_center = function(){
            $('body').on('click','#message-center',function(event){
                event.stopPropagation();
                account.openMessageCenter();
            });
        }
        account.openMessageCenter = function(){
            account.createDialog('message-center','消息中心');
            account.constructMessageCenter();
            if($("#message-center img[title=msg-reminder]").length>0){
                $("#message-center img[title=msg-reminder]").remove();
            }
        }
        account.constructMessageCenter = function(){
            $messageList = $('<ul></ul>');
            data = $("#message-center").data("messages");
            if(data != undefined){
                $.each(data, function(index, message){
                    var content = $.parseJSON(message);
                    if(content["type"]=="add_friend_req"){
                        $li = $("<li></li>").attr("from",content["from"]);
                        $messageBody = $("<p></p>").addClass("message-center-content").text(content["from"]+"请求加你为好友");
                        $accept = $("<button>同意</button>").addClass("add-friends-button").attr("action","accept");
                        $reject = $("<button>拒绝</button>").addClass("add-friends-button").attr("action","reject");
                        $li.append($messageBody).append($accept).append($reject).appendTo($messageList);
                    }else if(content["type"]=="add_friend_resp"){
                        $li = $("<li></li>");
                        var result;
                        if(content["message"]=="accept"){
                            result = "同意了您的好友请求";
                        }else{
                            result = "拒绝了您的好友请求";
                        }
                        $messageBody = $("<p></p>").addClass("message-center-content").text(content["from"]+result);
                        $li.append($messageBody).appendTo($messageList);
                    }else if(content["type"]=="join_group_apply"){
                        $li = $("<li></li>").attr("from",content["from"]).attr("group_id",content["group_id"]);
                        var group_id = content["group_id"];
                        var group_name = $("li.group[id=group-"+group_id+"]").children("p").text();
                        $messageBody = $("<p></p>").addClass("message-center-content").text(content["from"]+"申请加入群"+group_name);
                        $accept = $("<button>同意</button>").addClass("join-group-button").attr("action","add");
                        $reject = $("<button>拒绝</button>").addClass("join-group-button").attr("action","del");
                        $li.append($messageBody).append($accept).append($reject).appendTo($messageList);
                    }else if(content["type"]=="join_group_confirm"){
                        $li = $("<li></li>");
                        var result;
                        if(content["message"]=="success"){
                            result = "群主同意了您的加群申请";
                        }else{
                            result = "群主拒绝了您的加群申请";
                        }
                        $messageBody = $("<p></p>").addClass("message-center-content").text(content["group_id"]+result);
                        $li.append($messageBody).appendTo($messageList);
                    }
                });
            }
            $('#message-center-list').append($messageList);
            account.bindClick($messageList);
        }
        account.bindClick = function($div){
            $div.on("click", "button.add-friends-button", function(event){
                event.stopPropagation();
                action = $(this).attr("action");
                from_user = $(this).parent().attr("from");
                $.ajax({
                    type: 'PUT',
                    url: '/v1/friends/'+user+'/',
                    contentType: "application/json; charset=UTF-8",
                    headers: {"token":token},
                    data: $.toJSON({'account':from_user,'result':action}),
                    dataType: 'text',
                    statusCode: {
                        401: error401,
                        403: error403
                    }
                }).done(function (data){
                    if(action == "accept"){
                        account.get_friends();
                    }
                    alert(data);
                }).fail(function (jqXHR){
                    alert(jqXHR.responseText);
                });
            });
            $div.on("click", "button.join-group-button", function(event){
                event.stopPropagation();
                group_id = $(this).parent().attr("group_id");
                from_user = $(this).parent().attr("from");
                action = $(this).attr("action");
                $.ajax({
                    type: 'PUT',
                    url: '/v1/groups/'+group_id+'/',
                    contentType: "application/json; charset=UTF-8",
                    headers: {"token":token},
                    data: $.toJSON({'account':from_user,'operation':action}),
                    dataType: 'text',
                    statusCode: {
                        401: error401,
                        403: error403
                    }
                }).done(function (data){
                    alert(data);
                }).fail(function (jqXHR){
                    alert(jqXHR.responseText);
                });
            });
        }
        account.get_dates = function(chat_type,chat_identity){
            $.ajax({
                url: "/v1/records/dates/",
                type: "GET",
                dataType: "json",
                headers: {"token":token, "type":chat_type, "identity":chat_identity},
                statusCode: {
                    401: error401,
                    403: error403
                }
            }).done(function (data, textStatus, jqXHR) {
                $list = $("#history-"+chat_type+"-"+chat_identity).children("div.chat-history-selector");
                $ul = $("<ul></ul>");
                $.each(data, function(index, val) {
                    $("<li></li>").text(val).appendTo($ul);
                });
                $ul.appendTo($list);
            }).fail(function (jqXHR, textStatus, errorThrown) {
                alert(jqXHR.responseText);
            });
        }
        account.build_history_window = function(chat_type,chat_identity){
            if($("#history-"+chat_type+"-"+chat_identity).length==0){
                $history = $("<div></div>").attr("id","history-"+chat_type+"-"+chat_identity).addClass('chat-history-div');
                $history.append($("<p>x</p>"));
                $history.append($("<div></div>").addClass("chat-history-header"));
                $history.append($("<div></div>").addClass("chat-history-selector"));
                $history.on("click", "p" ,function(event) {
                    event.stopPropagation();
                    $(this).parent().css("display", "none");
                });
                $("#layer").append($history);
                account.get_dates(chat_type,chat_identity);
                
            }else{
                $("#history-"+chat_type+"-"+chat_identity).css('display', 'block');
            }
        }
        account.bind_get_history = function(){
            $("#chat-history").on("click", function(event) {
                event.stopPropagation();
                active_user = $(".chat-focus").attr("id").split("-");
                account.build_history_window(active_user[1],active_user[2]);
            });
        }
        account.getMsg = function() {
            if(typeof(Worker)!=="undefined") {
                var worker =new Worker("/static/getmsg.js");
                worker.onmessage = function(event) {
                    var msg = $.evalJSON(event.data);
                    var method = msg["method"];
                    switch(method) {
                        case "send_group_message":
                            var from = msg['args']['account'];
                            var time = msg['args']['time'];
                            var groupid = msg['args']['group_id'];
                            var message = msg['args']['msg'];
                            account.get_group_message(from,time,groupid,message);
                            break;
                        case "send_individual_message":
                            var from = msg['args']['account'];
                            var time = msg['args']['time'];
                            var message = msg['args']['msg'];
                            account.get_individual_message(from, time, message);
                            break;
                        case "add_friend_resp":
                            var from = msg['args']['account'];
                            var time = msg['args']['time'];
                            var message = msg['args']['msg'];
                            account.add_message(from, time, message, method, 0);
                            break;
                        case "add_friend_req":
                            var from = msg['args']['account'];
                            var time = msg['args']['time'];
                            var message = msg['args']['msg'];
                            account.add_message(from, time, message, method, 0);
                            break;
                        case "join_group_apply":
                            var from = msg['args']['account'];
                            var time = msg['args']['time'];
                            var groupid = msg['args']['group_id'];
                            var message = msg['args']['msg'];
                            account.add_message(from, time, message, method, groupid);
                            break;
                        case "join_group_confirm":
                            var time = msg['args']['time'];
                            var groupid = msg['args']['group_id'];
                            var result = msg['args']['result'];
                            account.add_message("", time, result, method, groupid);
                            break;
                        case "authorized":
                            window.location.href = "login.html";
                            break;
                        default:
                            break;
                    }
                };
                worker.onerror = function(event) {
                    throw event.data;
                };
                worker.postMessage({'user':user, 'token':token});
            }
        }
        account.add_msg_reminder = function($div, left_pos, top_pos){
            $("<img src='/static/images/msg-reminder.png'/>").css({
                "position": "absolute",
                "padding": "0",
                "margin": "0",
                "width": "8px",
                "height": "8px",
                "left": left_pos,
                "top": top_pos,
            }).attr("title", "msg-reminder").prependTo($div);
        }
        account.get_individual_message = function(from, time, msg) {
            var exist = false;
            var $listUser = $("#list-user-" + from);
            if($("#user-" + from).length != 0) {
                if(!($listUser.length != 0 && $listUser.hasClass("chat-focus"))
                    &&($("#user-" + from).children("img").filter(function(index, event) {return $(event).attr("title") == "msg-reminder";}).length == 0)) {
                    account.add_msg_reminder($("#user-" + from),"48px","1px");
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
            time = timeTmp.toLocaleDateString() + " " + timeTmp.toTimeString().split(" ")[0];
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
            account.addContent('records-user-'+from, $("#user-" + from).find(".nickname").eq(0).text(), content, time);
            for(var i=0; i<img.length; i++) {
                var callback = function(name) {
                    var url = "/v1/messages/image/" + user + "/" + name;
                    $.ajax({
                        url: url,
                        type: "GET",
                        dataType: "json",
                        headers: {"token":token},
                        statusCode: {
                            401: error401,
                            403: error403
                        }
                    }).done(function (data, textStatus, jqXHR) {
                        var src = "data:image/" + data['type'] + ";base64," + data['content'];
                        $("#" + name.split(".", 2)[0]).attr("src", src).css("max-width","480px");
                    }).fail(function (jqXHR, textStatus, errorThrown) {
                        $("#"+img[i]).attr("src", "/static/images/failed.jpg");
                    });
                };
                setTimeout(callback(img[i]), 0);
            }
        };
        account.get_group_message = function(from,time,groupid,message){
            var $groupList = $("#list-group-"+groupid);
            if(!($groupList.length != 0 && $groupList.hasClass("chat-focus"))
                &&($("#group-" + groupid).children("img").filter(function(index, event) {return $(event).attr("title") == "msg-reminder";}).length == 0)) {
                account.add_msg_reminder($("#group-" + groupid),"48px","1px");
            }
            if($groupList.length==0){
                var $li = $("<li></li>").attr("id", "list-group-" + groupid)
                    .css("display", "none").addClass("chat-friends");
                var $p = $("<p></p>").css("display", "none").text("×");
                var $span = $("<span></span>").text($("#group-"+groupid).children(".groupname").text());
                $li.append($p).append($span).appendTo($("#chat-list ul"));
                account.closeCard($li);
                account.addChatWindow("records-group-" + groupid);
                $("#records-group-"+groupid).css("display","none");
            }
            var timeTmp = new Date();
            timeTmp = new Date(Date.parse(time.replace(/[-]/g, "/")) - timeTmp.getTimezoneOffset()*60000);
            time = timeTmp.toLocaleDateString() + " " + timeTmp.toTimeString().split(" ")[0];
            var content = "";
            var img = new Array();
            for(var i=0; i<message.length; i++) {
                if(message[i]["type"] == "text") {
                    content += message[i]['content'];
                }
                else if(['jpg', 'png', 'bmp', 'gif', 'psd', 'jpeg'].indexOf(message[i]['type'])) {
                    content += "<img src='/static/images/loading.gif' id='" + message[i]['content'].split(".", 2)[0] + "'/>";
                    img.push(message[i]['content']);
                }
            }
            account.addContent('content-group-'+groupid, from, content, time);
            for(var i=0; i<img.length; i++) {
                var callback = function(name) {
                    var url = "/v1/messages/image/" + user + "/" + name;
                    $.ajax({
                        url: url,
                        type: "GET",
                        dataType: "json",
                        headers: {"token":token},
                        statusCode: {
                            401: error401,
                            403: error403
                        }
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
        account.add_message = function(from, time, message, msg_type, group_id){
            if($("#message-center img[title=msg-reminder]").length == 0){
                account.add_msg_reminder($("#message-center"),"28px","1px");
            }
            var data = {
                "from":from,
                "time":time,
                "message":message,
                "type":msg_type,
                "group_id":group_id,
            }
            if($("#message-center").data("messages") == undefined){
                $("#message-center").data("messages",[]);
            }
            $("#message-center").data("messages").push($.toJSON(data));
        };
        return account;
    }
};

$(document).ready(function() {
    var user = Account.createNew();
    user.init();
});

$(window).unload(function(){
    var data = {
        "state":"offline"
    };
    $.ajax({
        url: "/v1/login/" + user + "/",
        contentType: "application/json; charset=UTF-8",
        type: "POST",
        async:false,
        timeout: 2000,
        headers: {"token":token},
        data: $.toJSON(data),
        dataType: "text"
    }).always(function (jqXHR, textStatus, errorThrown) {
        $.removeCookie('account');
    });

});



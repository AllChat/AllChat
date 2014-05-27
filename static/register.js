/**
 * Created by Derek on 14-5-25.
 */
var globalCode;
var canBeSubmit = new Array(0,0,0,0,0,0);
var passTmp = "";

var generateCode = function() {
    var code = "";
    var codeLength = 4;//验证码的长度
    var selectChar = new Array(0,1,2,3,4,5,6,7,8,9,'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z');

    for(var i=0;i<codeLength;i++) {
       var charIndex = Math.floor(Math.random()*61);
      code +=selectChar[charIndex];
    }
    globalCode = code;
    return code;
};

var validate = function(value) {
    var inputCode = value.toUpperCase();
    var codeToUp = globalCode.toUpperCase();
    if(inputCode != codeToUp) {
      var content = "<p>验证码输入错误</p>";
      return {"result":false, "msg":content};
    }
    else {
      return {"result":true};
    }
};



function inputValidate() {
    $("#middle-form input").each(function(index, element) {
        var name = $(element).attr("name");
        if(name == "account" || name == "password") {
            $(element).on("keyup blur",function(event) {
                var pattern = /^[\w!@#$%^&*_.]+$/;
                var value = $(this).val();
                var $place = $(this).parent().next();
                if(event.type == "keyup") {
                    if (!pattern.test(value)) {
                        var content = "<p>请使用数字,字母或!@#$%^&*_.</p>";
                        $(content).appendTo($place.empty()).css({
                            "color": "red",
                            "font-size": parseFloat($place.css("font-size")) * 0.8 + "px"
                        });
                        if (name == "account"){
                            canBeSubmit[0] = 0;
                        }
                        else {
                            canBeSubmit[2] = 0;
                        }
                    }
                    else if(value.length > 256){
                        var content = "<p>用户名长度超过256</p>";
                        if (name == "password") {
                            content = "<p>密码长度超过256</p>";
                            canBeSubmit[2] = 0;
                        }
                        else {
                            canBeSubmit[0] = 0;
                        }
                        $(content).appendTo($place.empty()).css({
                            "color": "red",
                            "font-size": parseFloat($place.css("font-size")) * 0.8 + "px"
                        });
                    }
                    else{
                        var content = "<p>名字很棒</p>";
                        if (name == "password") {
                            content = "<p>密码很棒</p>";
                            passTmp = value;
                            canBeSubmit[2] = 1;
                        }
                        else {
                            canBeSubmit[0] = 1;
                        }
                        $(content).appendTo($place.empty()).css({
                            "color": "green",
                            "font-size": parseFloat($place.css("font-size")) * 0.8 + "px"
                        });
                    }
                }
                else{
                    if (value == ""){
                        var content = "<p>请输入用户名</p>";
                        if (name == "password") {
                            content = "<p>请输入密码</p>";
                        }
                        $(content).appendTo($place.empty()).css({
                            "color": "red",
                            "font-size": parseFloat($place.css("font-size")) * 0.8 + "px"
                        });
                        if (name == "account"){
                            canBeSubmit[0] = 0;
                        }
                        else {
                            canBeSubmit[2] = 0;
                        }
                    }
                }

            });
        }
        else if(name == "nickname") {
            $(element).on("keyup blur", function (event) {
                var value = $(this).val();
                var $place = $(this).parent().next();
                if(event.type == "keyup") {
                    if(value.length > 256){
                        var content = "<p>昵称长度超过256</p>";
                        $(content).appendTo($place.empty()).css({
                            "color": "red",
                            "font-size": parseFloat($place.css("font-size")) * 0.8 + "px"
                        });
                        canBeSubmit[1] = 0;
                    }
                    else{
                        var content = "<p>昵称很棒</p>";
                        $(content).appendTo($place.empty()).css({
                            "color": "green",
                            "font-size": parseFloat($place.css("font-size")) * 0.8 + "px"
                        });
                        canBeSubmit[1] = 1;
                    }
                }
                else{
                    if (value == ""){
                        var content = "<p>请输入昵称</p>";
                        $(content).appendTo($place.empty()).css({
                            "color": "red",
                            "font-size": parseFloat($place.css("font-size")) * 0.8 + "px"
                        });
                        canBeSubmit[1] = 0;
                    }
                }
            });
        }
        else if(name == "password-confirm"){
            $(element).on("keyup blur", function (event) {
                var value = $(this).val();
                var $place = $(this).parent().next();
                if(passTmp != value) {
                    var content = "<p>两次密码不相同</p>";
                        $(content).appendTo($place.empty()).css({
                            "color": "red",
                            "font-size": parseFloat($place.css("font-size")) * 0.8 + "px"
                        });
                    canBeSubmit[3] = 0;
                }
                else {
                    $place.empty();
                    canBeSubmit[3] = 1;
                }
            });
        }
        else if(name == "email") {
            $(element).on("keyup blur",function(event) {
                var pattern = /^[^@\s]+@[^@\s]+$/;
                var value = $(this).val();
                var $place = $(this).parent().next();
                if(event.type == "keyup") {
                    if (!pattern.test(value)) {
                        var content = "<p>邮箱名不可用</p>";
                        $(content).appendTo($place.empty()).css({
                            "color": "red",
                            "font-size": parseFloat($place.css("font-size")) * 0.8 + "px"
                        });
                        canBeSubmit[4] = 0;
                    }
                    else if(value.length > 256){
                        var content = "<p>邮箱名长度超过256</p>";
                        $(content).appendTo($place.empty()).css({
                            "color": "red",
                            "font-size": parseFloat($place.css("font-size")) * 0.8 + "px"
                        });
                        canBeSubmit[4] = 0;
                    }
                    else{
                        var content = "<p>邮箱名可用</p>";
                        $(content).appendTo($place.empty()).css({
                            "color": "green",
                            "font-size": parseFloat($place.css("font-size")) * 0.8 + "px"
                        });
                        canBeSubmit[4] = 1;
                    }
                }
                else{
                    if (value == ""){
                        var content = "<p>请输入邮箱名</p>";
                        $(content).appendTo($place.empty()).css({
                            "color": "red",
                            "font-size": parseFloat($place.css("font-size")) * 0.8 + "px"
                        });
                        canBeSubmit[4] = 0;
                    }
                }
            });
        }
        else if(name == "verify") {
            $(element).on("keyup blur", function (event) {
                var value = $(this).val();
                var $place = $(this).parent();
                if (event.type == "keyup") {
                    if (value.length >= 4) {
                        var ret = validate(value);
                        if(!ret["result"]) {
                            var content = ret['msg'];
                            $(content).appendTo($place.children("p").remove().end()).css({
                                "color": "red",
                                "font-size": parseFloat($place.css("font-size")) * 0.8 + "px",
                                "display": "inline",
                                "padding": "0px 4px 0px 4px"
                            });
                            canBeSubmit[5] = 0;
                        }
                        else{
                            var content = "<p>验证码正确</p>";
                            $(content).appendTo($place.children("p").remove().end()).css({
                                "color": "green",
                                "font-size": parseFloat($place.css("font-size")) * 0.8 + "px",
                                "display": "inline",
                                "padding": "0px 4px 0px 4px"
                            });
                            canBeSubmit[5] = 1;
                        }
                    }
                }
                else{
                    if (value == "") {
                        var content = "<p>请输入验证码</p>";
                        $(content).appendTo($place.children("p").remove().end()).css({
                            "color": "red",
                            "font-size": parseFloat($place.css("font-size")) * 0.8 + "px",
                            "display": "inline",
                            "padding": "0px 4px 0px 4px"
                        });
                        canBeSubmit[5] = 0;
                    }
                }
            });
        }
    });
}


$(document).ready(function(){

    $("#createcode").click(function(event) {
        event.preventDefault();
        $(this).children("input").val(generateCode());
    });

    $("#checkcode").val(generateCode());

    inputValidate();

    $("#middle-form").on("click", "#submit-button",function(event){
        event.preventDefault();
        if(canBeSubmit.join("") == "111111"){
            var data = {
                account: $("#account").val(),
                nickname:$("#nickname").val(),
                password:$("#password").val(),
                email:$("#email").val()
            };
            $.ajax({
                url: $("#middle-form").attr("action"),
                contentType: "application/json; charset=UTF-8",
                type: "POST",
                data: $.toJSON(data),
                dataType: "text"
            }).done(function (data, textStatus, jqXHR) {
                alert("succeed");
            }).fail(function (jqXHR, textStatus, errorThrown) {
                alert("failed");
            });
        }
    });
});
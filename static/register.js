/**
 * Created by Derek on 14-5-25.
 */
$(document).ready(function(){
    var globalCode;
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
    $("#createcode").click(function(event) {
        event.preventDefault();
        $(this).children("input").val(generateCode());
    });
    $("#checkcode").val(generateCode());
    $("#middle-form").on("click", "#submit-button",function(event){
        event.preventDefault();
        var pass_tmp = undefined;
        $("#middle-form").find("input").each(function(index, element){
            name = $(element).attr("name");
            value = $(element).val();
            if(name == "account") {
                var pattern = /^[\w!@#$%^&*_.]+$/;
                if (!pattern.test(value)) {
                    var $place = $(element).parent().next();
                    content = "<p>用户名中包含非法字符,请使用数字,字母或者!@#$%^&*_.</p>";
                    $place.html(content).css({
                        "color": "red",
                        "font-size": parseFloat($place.css("font-size")) * 0.8 + "px"
                    });
                    return false;
                }
                else if(value.length > 256){
                    var $place = $(element).parent().next();
                    content = "<p>用户名长度超过256</p>";
                    $place.html(content).css({
                        "color": "red",
                        "font-size": parseFloat($place.css("font-size")) * 0.8 + "px"
                    });
                    return false;
                }
            }
            else if(name == "nickname") {
                if(value.length > 256){
                    var $place = $(element).parent().next();
                    content = "<p>昵称长度超过256</p>";
                    $place.html(content).css({
                        "color": "red",
                        "font-size": parseFloat($place.css("font-size")) * 0.8 + "px"
                    });
                    return false;
                }
            }
            else if(name == "password") {
                var pattern = /^[\w!@#$%^&*_.]+$/;
                if (!pattern.test(value)) {
                    var $place = $(element).parent().next();
                    content = "<p>密码中包含非法字符,请使用数字,字母或者!@#$%^&*_.</p>";
                    $place.html(content).css({
                        "color": "red",
                        "font-size": parseFloat($place.css("font-size")) * 0.8 + "px"
                    });
                    return false;
                }
                else if(value.length > 256){
                    var $place = $(element).parent().next();
                    content = "<p>密码长度超过256</p>";
                    $place.html(content).css({
                        "color": "red",
                        "font-size": parseFloat($place.css("font-size")) * 0.8 + "px"
                    });
                    return false;
                }
                pass_tmp = value;
            }
            else if(name == "password-confirm") {
                if(pass_tmp != value) {
                    var $place = $(element).parent().next();
                    content = "<p>两次输入的密码不相同</p>";
                    $place.html(content).css({
                        "color": "red",
                        "font-size": parseFloat($place.css("font-size")) * 0.8 + "px"
                    });
                    return false;
                }
            }
            else if(name == "email") {
                var pattern = /^[^@\s]+@[^@\s]+$/;
                if (!pattern.test(value)) {
                    var $place = $(element).parent().next();
                    content = "<p>email名有误</p>";
                    $place.html(content).css({
                        "color": "red",
                        "font-size": parseFloat($place.css("font-size")) * 0.8 + "px"
                    });
                    return false;
                }
            }
            else if(name == "verify") {
                var ret = validate(value);
                if(!ret["result"]){
                    var content = ret['msg'];
                    var $place = $(element).parent();
                    $(content).appendTo($place).css({
                        "color": "red",
                        "font-size": parseFloat($place.css("font-size")) * 0.8 + "px",
                        "display": "inline",
                        "padding": "0px 4px 0px 4px"
                    });
                    return false;
                }
            }
        });
    });
});
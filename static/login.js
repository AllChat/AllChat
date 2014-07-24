/**
 * Created by Derek on 2014/6/3.
 */

function timer() {
    var $select = $(".middle-left-button .span-background");
    var num = $(".middle-left-button span").length;
    var tmp = parseInt($select.text());
    var index = tmp + 1;
    index = index % num;
    if (!index) {
        index = num;
    }
    $select.removeClass("span-background");
    $(".middle-left-button span").eq(index - 1).addClass("span-background");
    $(".middle-left-image-li").eq(tmp - 1).stop().fadeOut("slow").end().eq(index - 1).stop().fadeIn("slow");
}

$(document).ready(function(){
    if(typeof window.sessionStorage == 'undefined'){
        alert("浏览暂不支持localStorage, 请使用Chrome或者Firefox");
        return false;
    }
    $(".middle-left-image-li").eq(1).hide().end().eq(2).hide().end().eq(3).hide();
    $(".middle-left-button span").eq(0).addClass("span-background");
    var tmpTimer = setInterval("timer()", 3000);

    $(".middle-left-button").on("mouseenter mouseleave", "span", function(event) {
        if(event.type == "mouseenter"){
            clearInterval(tmpTimer);
            tmpTimer = null;
            var $select = $(".middle-left-button .span-background");
            var preIndex = parseInt($select.text());
            var index = parseInt($(this).text());
            $select.removeClass("span-background");
            $(this).addClass("span-background");
            $(".middle-left-image-li").eq(preIndex - 1).stop().fadeOut("slow").end().eq(index - 1).stop().fadeIn("slow");
        }
        else{
            tmpTimer = setInterval("timer()", 3000);
        }
    });

    $(".middle-right-form").on("submit", function(event) {
        event.preventDefault();
        var account = $("#account").val();
        data = {
            password: $("#password").val(),
            state: $("#state").val()
        };
        $.ajax({
            url: $(".middle-right-form").attr("action") + account,
            contentType: "application/json; charset=UTF-8",
            type: "POST",
            data: $.toJSON(data),
            dataType: "text"
        }).done(function (data, textStatus, jqXHR) {
            sessionStorage.setItem("state", $("#state").val());
            window.location.href = "index.html";
        }).fail(function (jqXHR, textStatus, errorThrown) {
            alert("账户名或密码有误，请重新输入");
        });
    });
});
/**
 * Created by Derek on 14-5-25.
 */
$(document).ready(function(){
    $("#middle-form").submit(function(event){
        event.preventDefault();
        $(this).find("input").each(function(index, element){
            name = $(element).attr("name");
            value = $(element).val();
            if(name == "account") {
                var pattern = /^[\w!@#$%^&*_.]+$/;
                if (!pattern.test(value)) {
                    var $place = $(element).parent().next();
                    content = "<p>用户名中包含非法字符</p>";
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
                    alert(name);
                }
            }
            else if(name == "password") {

            }
            else if(name == "password-confirm") {

            }
            else if(name == "email") {

            }
            else if(name == "verify") {

            }
        });
    });
});
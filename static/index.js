/**
 * Created by Derek Fang on 2014/6/11.
 */

$(document).ready(function() {
    $('#chat-setting form img').on('click', function(e) {
        e.preventDefault();
        $(this).next().trigger("click");
    });
});
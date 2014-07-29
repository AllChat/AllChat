$(document).ready(function (){
    $('body').on('click','#add-bar-swither',function(event){event.stopPropagation();
    	if($('#control-list-middle-accounts-add').css("bottom")=="-80px"){
    		$('#control-list-middle-accounts-add').animate({"bottom":"0px"},600);
    	}else{
    		$('#control-list-middle-accounts-add').animate({"bottom":"-80px"},600);
    	}
    });
    $('body').on('click','#fast-add-button',function(event){
    	event.stopPropagation();
    	addFriendRequest();
    });
});

function addFriendRequest(){
	var username = $('#add-username').val();
	var user = $.cookie('account');
	if(username.length==0){
		alert('请输入用户名后再提交！');
	}else{
		$.ajax({
			type: 'POST',
			url: '/v1/friends/'+user+'/',
			contentType: "application/json; charset=UTF-8",
			data: {'account':username},
			dataType: 'text',
		}).done(function (data, textStatus){
			alert(data);
		}).fail(function (data, textStatus){
			alert(textStatus);
		});
	}
}
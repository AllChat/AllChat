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
    	var username = $('#add-username').val();
    	addFriendRequest(username);
    });
    $('body').on('click','#search-user-button',function(event){
    	event.stopPropagation();
    	searchUser();
    });
});

function addFriendRequest(username){
	var user = $.cookie('account');
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
				data: $.toJSON({'account':username,'message':'this is '+user}),
				dataType: 'text',
			}).done(function (data){
				alert(data);
			}).fail(function (jqXHR){
				alert(jqXHR.responseText);
			});
		}
	}
}
function searchUser(){
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
				dataType: 'json',
			}).done(function (data){
				if(data.accounts.length==0){
					alert('很遗憾，没有找到匹配的结果，换个关键字试试吧～');
				}else{
					var type = 'user';
					showSearchResultDialog(data,type);
				}
			}).fail(function (jqXHR){
				alert(jqXHR.responseText);
			});
		}
	}
}

function showSearchResultDialog(data,type){
	if($('#search-result-dialog').length>0){
		$('#result-list-box ul').empty();
	}else{
		$('#layer').append('<div id="search-result-dialog"></div>');
		$('#search-result-dialog').append('<div id="result-list-box"></div>');
		$('#result-list-box').append('<ul></ul>');
	}
	$.each(data.accounts,function(index,value){
		addUserToDialog(value['account'],value['nickname'],value['state'],value['icon']);
	});
	$('body').off('click','button.search-result-addbutton');
	$('body').on('click','button.search-result-addbutton',function(event){
		event.stopPropagation();
		var username = $(this).siblings('.search-result-username').text();
		addFriendRequest(username);
	});
}
function addUserToDialog(account,nickname,state,icon){
	var userInfo = $('<li></li>');
	userInfo.append('<p class="search-result-username">'+account+'</p>');
	userInfo.append('<p class="search-result-nickname">'+nickname+'</p>');
	userInfo.append('<p class="search-result-state">'+state+'</p>');
	userInfo.append('<p class="search-result-icon">'+icon+'</p>');
	userInfo.append('<button class="search-result-addbutton">加为好友</button>');
	$('#result-list-box ul').append(userInfo);
}
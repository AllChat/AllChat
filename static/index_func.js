$(document).ready(function (){
    $('body').on('click','#search-icon',function(event){
    	event.stopPropagation();
    	toggleDisplay($('#control-list-middle-accounts-add'));
    	toggleDisplay($('#control-list-middle-groups-add'));
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
    $('body').on('click','#create-group-button',function(event){
    	event.stopPropagation();
    	createGroup();
    });
    $('body').on('click','#search-group-button',function(event){
    	event.stopPropagation();
    	searchGroup();
    });});

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
					showSearchResult(data,type);
				}
			}).fail(function (jqXHR){
				alert(jqXHR.responseText);
			});
		}
	}
}
function createResultDialog(){
	if($('#search-result-dialog').length>0){
		$('#result-list-box ul').empty();
	}else{
		var $dialog = $('<div></div>').attr('id','search-result-dialog');
		var $title = $('<div></div>').attr('id','dialog-title').append($('<p></p>').text('搜索结果'));
		var $closeTab = $('<div></div>').attr('id','result-dialog-close').append($('<img/>').attr('src','../static/images/icon/close.png'));
		var $list = $('<div></div>').attr('id','result-list-box').append('<ul></ul>');
		$dialog.append($title).append($closeTab).append($list).appendTo($('#layer'));
	}
}
function showSearchResult(data,type){
	createResultDialog();
	if(type=='user'){
		values=data.accounts;
	}else if(type=='group'){
		values=data.groups;
	}
	$.each(values,function(index,value){
		addItemToDialog(value,type);
	});
	$('body').off('click','#result-dialog-close');
	$('body').on('click','#result-dialog-close',function(event){
		event.stopPropagation();
		$('#search-result-dialog').remove();
	});
	$('body').off('click','button.search-result-addbutton');
	$('body').on('click','button.search-result-addbutton',function(event){
		event.stopPropagation();
		var username = $(this).siblings('.search-result-username').text();
		addFriendRequest(username);
	});
	$('body').off('click','button.search-result-joinbutton');
	$('body').on('click','button.search-result-joinbutton',function(event){
		event.stopPropagation();
		var groupid = $(this).siblings('.search-result-groupid').text();
		var groupowner = $(this).siblings('.search-result-groupowner').text();
		joinGroupRequest(groupid,groupowner);
	});
}
function addItemToDialog(value,type){
	var $li = $('<li></li>');
	if(type=='user'){
		$username = $('<p></p>').attr('class','search-result-username').text(value['account']);
		$nickname = $('<p></p>').attr('class','search-result-nickname').text(value['nickname']);
		$state = $('<p></p>').attr('class','search-result-state').text(value['state']);
		$icon = $('<p></p>').attr('class','search-result-icon').text(value['icon']);
		$li.append($username).append($nickname).append($state).append($icon);
		$li.append('<button class="search-result-addbutton">加为好友</button>');
	}else if(type=='group'){
		$groupname = $('<p></p>').attr('class','search-result-groupname').text(value['group_name']);
		$groupid = $('<p></p>').attr('class','search-result-groupid').text(value['group_id']);
		$groupowner = $('<p></p>').attr('class','search-result-groupowner').text(value['group_owner']);
		$groupsize = $('<p></p>').attr('class','search-result-groupsize').text(value['group_size']);
		$li.append($groupname).append($groupid).append($groupowner).append($groupsize);
		$li.append('<button class="search-result-joinbutton">申请加入</button>');
	}
	$('#result-list-box ul').append($li);
}
function toggleDisplay(div){
	if(div.css("bottom")=="-80px"){
		div.animate({"bottom":"0px"},600);
	}else{
		div.animate({"bottom":"-80px"},600);
	}
}
function searchGroup(){
	var keyword = $('#search-group-name').val();
	if(keyword.length==0){
		alert('搜索关键字不能为空');
	}else{
		var user = $.cookie('account');
		$.ajax({
			type: 'POST',
			url: '/v1/groups/search/',
			contentType: 'application/json; charset=utf-8',
			data: $.toJSON({'keyword':keyword,'account':user,'type':'uncertain','offset':0}),
			dataType: 'json',
		}).done(function (data){
			if(data.result_size==0){
				alert('很遗憾，没有找到匹配的结果，换个关键字试试吧～');
			}else{
				var type = 'group';
				showSearchResult(data,type);
			}
		}).fail(function (jqXHR){
			alert('服务器开小差了，sorry!');
		});
	}
}
function createGroup(){
	var groupname = $('#create-group-name').val();
	if(groupname.length==0){
		alert('群名称还没填呢，再想想吧~');
	}else{
		var user = $.cookie('account');
		$.ajax({
			type: 'POST',
			url: '/v1/groups/',
			contentType: 'application/json; charset=UTF-8',
			data: $.toJSON({'account':user,'group_name':groupname}),
			dataType: 'text',
		}).done(function (data){
			alert('您的群创建成功了，快去拉几个小弟进来吧~');
		}).fail(function (jqXHR){
			alert(jqXHR.responseText);
		});
	}
}
function joinGroupRequest(groupid,groupowner){
	var user = $.cookie('account');
	if(user==groupowner){
		alert('您已经是群主了，别闹~');
	}else{
		$.ajax({
			type: 'PUT',
			url: '/v1/groups/'+groupid+'/',
			contentType: 'application/json; charset=utf-8',
			data: $.toJSON({'account':user,'operation':'join'}),
			dataType:'text',
		}).done(function (data){
			alert('申请成功啦，等着好消息吧~');
		}).fail(function (jqXHR){
			alert(jqXHR.responseText);
		});
	}
}
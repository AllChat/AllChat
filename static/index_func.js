$(document).ready(function (){
    $('body').on('click','#search-icon',function(event){
        event.stopPropagation();
        if($('div.setup-list').css('display')=='block'){$('div.setup-list').toggle();};
        $('div.search-add-bar').toggle(600);
    });
    $('body').on('click','#setup-icon',function(event){
        event.stopPropagation();
        if($('div.search-add-bar').css('display')=='block'){$('div.search-add-bar').toggle();};
        $('div.setup-list').toggle(600);
    })
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
    });
    $('body').on('click','#personal-info',function(event){
        event.stopPropagation();
        setupPersonalInfo();
    });
    $('body').on('click','#change-password',function(event){
        event.stopPropagation();
        changePassword();
    });
    $('body').on('click','#about-us',function(event){
        event.stopPropagation();
        showAbout();
    });
    $('body').on('click','#group-manage',function(event){
        event.stopPropagation();
        manageGroups();
    });
});

function addFriendRequest(username){
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
                    showSearchResult(data,type);
                }
            }).fail(function (jqXHR){
                alert(jqXHR.responseText);
            });
        }
    }
}
function createDialog(dialogID,title){
    if($('.info-dialog').length>0){
        $('.info-dialog').remove();
    }
    var $dialog = $('<div></div>').attr('id',dialogID+'-dialog').addClass('info-dialog');
    var $title = $('<div></div>').addClass('dialog-title').append($('<p></p>').text(title));
    var $closeTab = $('<div></div>').addClass('dialog-close').append($('<img/>').attr('src','../static/images/icon/close.png'));
    var $list = $('<div></div>').attr('id',dialogID+'-list').addClass('dialog-content');
    $dialog.append($title).append($closeTab).append($list).appendTo($('#layer'));
    bindClose($closeTab);
}
function bindClose($div){
    $div.on('click',function(event){
        event.stopPropagation();
        $div.parent().remove();
    });
}
function showSearchResult(data,type){
    createDialog('search-result','搜索结果');
    if(type=='user'){
        values=data.accounts;
    }else if(type=='group'){
        values=data.groups;
    }
    $('#search-result-list').append('<ul></ul>');
    $.each(values,function(index,value){
        addItemToDialog(value,type);
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
    $('#search-result-list ul').append($li);
}
function searchGroup(){
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
function joinGroupRequest(groupid,groupowner){
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
function setupPersonalInfo(){
    $('.setup-list').toggle();
    createDialog('personal-info','个人信息');
    constructInfoDialog();
    $('div.personal-info-head img').attr('src',$('#icon-self').attr('src'));
    $('#personal-info-submit').off('click');
    $('#personal-info-submit').on('click',function(event){
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
    $('div.personal-info-head button').off('click');
    $('div.personal-info-head button').on('click',function(event){
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
function constructInfoDialog(){
    $head = $('<div></div>').addClass('personal-info-head');
    $head.append($('<p></p>').text('头像')).append('<img/>').append($('<button></button>').text('更换'));
    $nickname = $('<div></div>').addClass('personal-info-nickname');
    $nickname.append($('<p></p>').text('昵称')).append('<input/>');
    $email = $('<div></div>').addClass('personal-info-email');
    $email.append($('<p></p>').text('邮箱')).append('<input/>');
    $submit = $('<button></button>').attr('id','personal-info-submit').text('确认');
    $('#personal-info-list').append($head).append($nickname).append($email).append($submit);
}
function changePassword(){
    $('.setup-list').toggle();
    createDialog('change-password','修改密码');
    constructPasswordDialog();
    $('#change-password-submit').off('click');
    $('#change-password-submit').on('click',function(event){
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
function constructPasswordDialog(){
    $oldpassword = $('<div></div>').attr('id','password-head').addClass('password-input');
    $oldpassword.append($('<p></p>').text('原密码')).append('<input id="oldpassword" type="password"/>');
    $newpassword = $('<div></div>').addClass('password-input');
    $newpassword.append($('<p></p>').text('新密码')).append('<input id="newpassword" type="password"/>');
    $newconfirm = $('<div></div>').addClass('password-input');
    $newconfirm.append($('<p></p>').text('确认')).append('<input id="newconfirm" type="password"/>');
    $submit = $('<button></button>').attr('id','change-password-submit').text('确认');
    $('#change-password-list').append($oldpassword).append($newpassword).append($newconfirm).append($submit);
}
function showAbout(){
    $('.setup-list').toggle();
    createDialog('about-allchat','关于allchat');
    $('#about-allchat-list').append($('<p></p>').text('Allchat 1.0').css({"margin-top":"30px","margin-left":"20px"})).append(
        $('<p></p>').text('Author: Derake, Alex').css("margin-left","20px")).append(
        $('<p></p>').text('Copyright© 2014-2020. All rights reserved.').css("margin-left","20px"));
}
function manageGroups(){
    createDialog('manage-group','我加入的群');
    constructGroupDialog();
}
function constructGroupDialog(){
    var url = "/v1/groups/";
    $.ajax({
        type: 'GET',
        url: url,
        dataType: 'json',
        headers: {'group_id':0,'account':user, 'token':token},
        async: false,
        statusCode: {
            401: error401,
            403: error403
        }
    }).done(function (data,textStatus,jqXHR){
        $groupList = $('<ul></ul>');
        $.each(data,function (key,value){
            $li = $('<li></li>');
            $groupname = $('<p></p>').addClass('search-result-groupname').text(value['name']);
            $groupid = $('<p></p>').addClass('search-result-groupid').text(key);
            if(value['role']=='owner'){
                $button = $('<button>管理该群</button>').addClass('manage-group-button');
            }else{
                $button = $('<button>退出该群</button>').addClass('quit-group-button');
            }
            $li.append($groupname).append($groupid).append($button).appendTo($groupList);
        });
        $('#manage-group-list').append($groupList);
    }).fail(function (jqXHR){
        if(jqXHR.status == 503){
            alert("数据库故障,请重新登陆");
        }else if(jqXHR.status == 404){
            alert("用户名有误,请重新登陆");
        }
    });
}
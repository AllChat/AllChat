$(document).ready(function (){
                
});

// function constructGroupDialog(){
//     var url = "/v1/groups/";
//     $.ajax({
//         type: 'GET',
//         url: url,
//         dataType: 'json',
//         headers: {'group_id':0,'account':user, 'token':token},
//         async: false,
//         statusCode: {
//             401: error401,
//             403: error403
//         }
//     }).done(function (data,textStatus,jqXHR){
//         $groupList = $('<ul></ul>');
//         $.each(data,function (key,value){
//             $li = $('<li></li>');
//             $groupname = $('<p></p>').addClass('search-result-groupname').text(value['name']);
//             $groupid = $('<p></p>').addClass('search-result-groupid').text(key);
//             if(value['role']=='owner'){
//                 $button = $('<button>管理该群</button>').addClass('manage-group-button');
//             }else{
//                 $button = $('<button>退出该群</button>').addClass('quit-group-button');
//             }
//             $li.append($groupname).append($groupid).append($button).appendTo($groupList);
//         });
//         $('#manage-group-list').append($groupList);
//     }).fail(function (jqXHR){
//         if(jqXHR.status == 503){
//             alert("数据库故障,请重新登陆");
//         }else if(jqXHR.status == 404){
//             alert("用户名有误,请重新登陆");
//         }
//     });
// }
$(document).ready(function (){
    $('body').on('click','li',function(event){var username=this.children[1].innerHTML;if($('#chatWindow[name='+username+']').length==0){var userhead=$(this.children[0]).attr("src");createChatWindow(username,userhead)};$('#chatWindow[name='+username+']').click();event.stopPropagation();});
    $('body').on('click','.draggable',function(){maxIndex=getMaxIndex();if(Number($(this).css( "z-index"))<maxIndex){$(this).css( "z-index", maxIndex+1);}});
    $('body').on('dragstart','.draggable',function(){maxIndex=getMaxIndex();if(Number($(this).css( "z-index"))<maxIndex){$(this).css( "z-index", maxIndex+1);}});
	$('body').on('click','#close',function () {$(this).parent().parent().remove();});
	$.each($('.draggable'),function(i,window){$(window).css('z-index',1);});
});
function createChatWindow(username,userhead){
    var chatWindow = $('<div id=chatWindow class=draggable name='+username+'><div id=pic><img id=chathead src='+userhead+'><img id="min" src="../static/images/icon/min.png"><img id="max" src="../static/images/icon/max.png"><img id="close" src="../static/images/icon/close.png"></div><div id=msgWindow ></div><div id=optionArea></div><div id=inputArea><div id=inputBox ><textarea id=inputText ></textarea></div><input type=button value=发送></div></div>').appendTo($('#desktop'));
    chatWindow.draggable({ containment: "parent" });
	chatWindow.css('z-index',0);
}
function getMaxIndex(){
	var maxIndex = 0;
	$.each($('.draggable'),function(i,window){if(Number($(window).css('z-index'))>maxIndex){maxIndex=Number($(window).css('z-index'))}});
	return maxIndex;
}
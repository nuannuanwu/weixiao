$(document).ready(Date.prototype.Format = function(fmt){ 
  		var o = {   
    	"M+" : this.getMonth()+1,                 //月份   
    	"d+" : this.getDate(),                    //日   
    	"h+" : this.getHours(),                   //小时   
    	"m+" : this.getMinutes(),                 //分   
    	"s+" : this.getSeconds(),                 //秒   
    	"q+" : Math.floor((this.getMonth()+3)/3), //季度   
    	"S"  : this.getMilliseconds()             //毫秒   
  	};   
  	if(/(y+)/.test(fmt))   
    	fmt=fmt.replace(RegExp.$1, (this.getFullYear()+"").substr(4 - RegExp.$1.length));   
  	for(var k in o)   
    	if(new RegExp("("+ k +")").test(fmt))   
  	fmt = fmt.replace(RegExp.$1, (RegExp.$1.length==1) ? (o[k]) : (("00"+ o[k]).substr((""+ o[k]).length)));   
  	return fmt;   
});

function dialog_pub(msgid){
	if(checkInputLength('#id_body_'+msgid,200,msgid)==false){return false;}
		msg_con = $('#id_body_'+msgid);
		msg_val = msg_con.val();
        data = { parent_id: msg_con.data('parent'),waiter_id:msg_con.data('waiter'),body:msg_val };
		url = waiter_save_message;
		user_name=$('#msg_user_'+msgid).attr('title');
		user_head=$('#msg_head_'+msgid).attr('src');
		msg_time=new Date().Format("yyyy-MM-dd hh:mm");
		$.post(url, data, function(result){
            var type = result.type;
			if (type == 'ok') {
				msg_sended= '<div class="kDialog clearfix" style="display:none;"><a title="'+user_name+'" class="kmsgHead pull-right" href=""><img src="'+user_head+'"></a>'+
				    		'<div class="thumbnail kChat_right pull-right"><p>'+msg_val+'</p><br>'+
				      		'<small rel="tooltip" class="date">'+msg_time+'</small><span class="ktrian_out"></span><span class="ktrian_in"></span></div></div>';
                $("#dialog-area-"+msgid).before(msg_sended);
                $("#dialog-area-"+msgid).prev().fadeIn("slow");
                $("#msg-reply-"+msgid).show();
                msg_con.val("");
			}
			else {
				Balert(result.message);
			}
		},"json");
		return false;
	}
	

function word_num(msgid){  
	var Interval; 
	clearInterval(Interval);	
	Interval=setInterval(function(){checkInputLength('#id_body_'+msgid,200,msgid);},300);
    }

    //检测输入字符数
    function checkInputLength(obj,num,msgid){
    	if($(obj).val().replace(/<(?!img|input|object)[^>]*>|\s+/ig, "") == ""){
        		textareaStatus('off',msgid);
        		return false;
        	}else{
            	textareaStatus('on',msgid);
            	return true;
            }
		/*
        var len = $(obj).val().length;
        var wordNumObj = $('#wordNum_'+msgid);
        if(len==0){
            textareaStatus('off',msgid);
            wordNumObj.css('color','').html((num-len));
            return false;
        }else if( len > num ){
            wordNumObj.css('color','red').html((len-num));
            textareaStatus('off',msgid);
            return false;
        }else if( len <= num){
        	if($(obj).val().replace(/<(?!img|input|object)[^>]*>|\s+/ig, "") == ""){
        		wordNumObj.css('color','').html((num-len));
        		textareaStatus('off',msgid);
        		return false;
        	}else{
            	wordNumObj.css('color','').html((num-len));
            	textareaStatus('on',msgid);
            	return true;
           }
        }*/
    }

    //发布窗口、按钮状态
    function textareaStatus(type,msgid){
        var obj = $('#send_button_'+msgid);
        if(type=='on'){
            obj.removeAttr('disabled').attr('class','btn btn-info pull-right');
            //}else if( type=='sending'){
            //	obj.attr('disabled','true').attr('class','btn_big_disable hand');
        }else{
            obj.attr('disabled','true').attr('class','btn btn-info pull-right disabled');
        }
    }
	
	
	function dialog(msgid,type){
		var msgbar = $("#msg-area-"+msgid);
			msgbar.slideToggle();
			$("#msg-dialog-"+msgid).slideToggle();
			if(document.location.href.indexOf("track")>0){
				if(type==1){
					if(document.getElementById('track_add_'+msgid)){
						msgbar.remove();
						$("#msg-dialog-"+msgid).remove();
					}
				}
			}
	}  
(function(){
	var unreads = $('._updateUnread');
	unreads.live("click", function(){ 
		var url = waiter_update_unread_message;
		var unread = $(this);
		var userid = unread.attr('data-userid');			
		var recipientid = unread.attr('data-recipientid')

		var unreadnum = unread.attr('data-unreadnum');
		if (unreadnum > 0){
			unread.attr('data-unreadnum',0);
			$.get(url,{ userid:userid, recipientid:recipientid});
		}
	});
})();
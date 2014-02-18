var CHOSEN;
var GROUP = $('h1').data('groupid'), SCHOOL = $('h1').data('school');
//初始化并显示食谱
function cookbook(obj,y,m,d){
		if(obj != CHOSEN){
		var o = $(obj), c = $("#cookbook"), a = $("#arrow"), as = $("#arrowS");
		var ol = o.offset().left, ot = o.offset().top, pt = o.position().top, pl = o.position().left, wh = $(window).height(), cw = c.width(), ch = c.height();
		$('#breakfast').val();
		$('#light_breakfast').val();
		$('#lunch').val();
		$('#light_lunch').val();
		$('#dinner').val();
		$('#light_dinner').val();
		cookbookGet(y,m,d);
		if((2*cw) > ol){
			if(a.hasClass("kArrowR")){
				a.removeClass("kArrowR");
				as.removeClass("kArrowSR");
			};
			a.addClass("kArrowL");
			as.addClass("kArrowSL");
			if((wh-ot) > ch || (ot-100) < ch){
				c.css({"left":pl+100,"top":pt-20});
				a.css({"top":60});
				as.css({"top":60});
			}else{
				c.css({"left":pl+100,"top":pt-ch+80});
				a.css({"top":ch-60});
				as.css({"top":ch-60});
			}
			c.show();
		}else{
			if(a.hasClass("kArrowL")){
				a.removeClass("kArrowL");
				as.removeClass("kArrowSL");
			};
			a.addClass("kArrowR");
			as.addClass("kArrowSR");
			if((wh-ot) > ch || (ot-100) < ch){
				c.css({"left":pl-cw-20,"top":pt-20});
				a.css({"top":60});
				as.css({"top":60});
			}else{
				c.css({"left":pl-cw-20,"top":pt-ch+80});
				a.css({"top":ch-60});
				as.css({"top":ch-60});
			}			
			c.show();
		}
		$(CHOSEN).removeClass("bgRed");
		o.addClass("bgRed");
		CHOSEN = obj;
	}
	return false;
}
//AJAX获取食谱内容
function cookbookGet(y,m,d){
	var date = y+'-'+m+'-'+d;
	data = { date:date,school:SCHOOL,group:GROUP };
	url='get_cookbook_date/';	
	$.get(url, data, function(result){
		var con = result.con.con;
		if (result.type == 'ok') {
			$('#cookbook_save').unbind("click");
			$('#cookbook_save').click(function(){cookbookSave(y,m,d);});
			$('#cookbook_date').html(result.con.month+'/'+result.con.day);
			fontOrange(con.breakfast.comefrom,'breakfast');
			fontOrange(con.light_breakfast.comefrom,'light_breakfast');
			fontOrange(con.lunch.comefrom,'lunch');
			fontOrange(con.light_lunch.comefrom,'light_lunch');
			fontOrange(con.dinner.comefrom,'dinner');
			fontOrange(con.light_dinner.comefrom,'light_dinner');
			$('#breakfast').val(con.breakfast.con);
			$('#light_breakfast').val(con.light_breakfast.con);
			$('#lunch').val(con.lunch.con);
			$('#light_lunch').val(con.light_lunch.con);
			$('#dinner').val(con.dinner.con);
			$('#light_dinner').val(con.light_dinner.con);
		}
	},"json");
	return false;
}
//标记自定义食谱
function fontOrange(con,type){
	if(con == 'group'){
		$('#'+type+'_t').addClass("fontOrange");
	}
	else if($('#'+type+'_t').hasClass("fontOrange")){
		$('#'+type+'_t').removeClass("fontOrange");
	}
}
//保存食谱
function cookbookSave(y,m,d){
	var date = y+'-'+m+'-'+d;
	var breakfast = $('#breakfast').val(),
		light_breakfast = $('#light_breakfast').val(),
		lunch =	$('#lunch').val(),
		light_lunch = $('#light_lunch').val(),
		dinner = $('#dinner').val(),
		light_dinner = $('#light_dinner').val(),
		sid = $("#school_id").val();
	cookbookPost('save',date,breakfast,light_breakfast,lunch,light_lunch,dinner,light_dinner,sid);	
}
//关闭食谱
function cookbookClose(){
	$(CHOSEN).removeClass("bgRed");
	$("#cookbook").hide();
	CHOSEN = undefined;
	return false;
}
//清空食谱
function cookbookClear(event,y,m,d){
	stopBubble(event);
	var date = y+'-'+m+'-'+d;
	var breakfast = "",
			light_breakfast = "",
			lunch =	"",
			light_lunch = "",
			dinner = "",
			light_dinner = "";			
	var object = { message:'确认要清空该食谱吗？',handler:function() {
		cookbookPost('clear',date,breakfast,light_breakfast,lunch,light_lunch,dinner,light_dinner);
	}};
	Bconfirm(object);
}
//AJAX递交食谱至后端
function cookbookPost(type,date,breakfast,light_breakfast,lunch,light_lunch,dinner,light_dinner,sid){
	data = { date:date,school:SCHOOL,group:GROUP,breakfast:breakfast,light_breakfast:light_breakfast,lunch:lunch,light_lunch:light_lunch,dinner:dinner,light_dinner:light_dinner,ty:type ,sid:sid};
	url='save_cookbook/';	
	$.post(url, data, function(result){
		if (result.type) {
			if(type == 'save'){
				Notice.success("食谱保存"+result.message);
			}else{
				Notice.success("食谱清空"+result.message);
			}
			cookbookClose();
			
			var con = result.con;
			var items = "";
			if(con.breakfast)items += "早餐 ";
			if(con.light_breakfast)items += "早点 ";
			if(con.lunch)items += "午餐 ";
			if(con.light_lunch)items += "午点 ";
			if(con.dinner)items += "晚餐 ";
			if(con.light_dinner)items += "晚点 ";
			$("#bg-"+date).html(items);
		}else{
			Notice.error(result.message);
		}
	},"json");
	return false;
}



//食谱设置显示
$(function(){

	var isInBox = false;
	$('#kGroupSelect').hover(
	  function () {	  
	  	isInBox = true
	  	$('#kGroupSelect-con').show();	    
	  }, 
	  function () {
	  	isInBox = false
	  	setTimeout(function(){
	  		if (!isInBox) {
	  			$('#kGroupSelect-con').hide();	
	  			clearTimeout()
	  		}	  	 	
	  	 }, 500)	   
	  }
	);

	$('#kGroupSelect-con').hover(
	  function () {
	    isInBox = true;
	    $(this).show()
	  }, 
	  function () {
	    isInBox = false;
	    $(this).hide()
	  }
	);

})
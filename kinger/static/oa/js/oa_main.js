// JavaScript Document
/*
*=========================================================
* @author: het
* @date:2013-04-20
* @description: 幼儿园教育系统/js
*=========================================================
*/
// oa公用效果js操作文件

/*$(".cni > .stretch-btn").live('click',function(){
	var openList = $(this).parent(".cni").siblings(".p-list");
	if(openList.is(":visible")){
		openList.slideUp();
		$(this).text("展开");
	}else{
		openList.slideDown();
		$(this).text("折叠");
	} 
})*/
// 展开手风琴功能
$(document).on('click', ".stretch-btn", function(){
	var openList = $(this).parent(".cni").siblings('.p-list');
	if(openList.is(":visible")){
		openList.slideUp();
                //openList.show();
		$(this).text("展开");
	}else{
		openList.slideDown();
                 //openList.show();
		$(this).text("折叠");
	} 
});
  
$(document).ready(function(){
	//列表样式
	//$(".list tr:even").addClass("bg_color");
	$(".list tr").hover(
	   function(){
			$(this).toggleClass("atr"); 
	   },
	   function(){ 
			$(this).toggleClass("atr");
                                
	});
	//日期选择
	$(".selectdata").datepicker({
            dateFormat: 'yy-mm-dd',
            changeYear: true,
            changeMonth: false, 
            fixFocusIE: true,  
            onSelect:function(date){   
                $(this).blur().change();
            },onClose: function (date) {  
             }
        });

//多文件上传 
//$("#my-uploadfiles")
var number_flag = 0;
$(document).on('click','#my-uploadfiles',function(){ 
	number_flag = number_flag+1; 
    var inputHtml ='<div class="addinput" style="display: none;"><span class="filesname"></span><input type="file" class="hide" name="files" id="inpitid_'+number_flag+'"/><a class="delectfile">删除</a></div>';
    $('#quoteRequest').append(inputHtml);
    $('.addinput > [name=files]:last').click();
        //$('#inpitid_'+number_flag).click();
        //$('.addinput > [name=files]:last').change();
}); 
// file的change事件
$(document).on('change' , '.addinput > [name=files]:last',function(){ 
	  	var fileTarget = $("#inpitid_"+number_flag)[0];
	  	 console.log(fileTarget);
	  	if(fileTarget.files[0].size>8*1024*1024){
	  		$("#inpitid_"+number_flag).parent(".addinput").empty();
	  		alert("您选择的文件太大!");
	  	}else{ 
	        var url = fileTarget.value; 
	        url = url.split("\\");
	        var fileName = url[url.length-1];
	        $(this).siblings("span").html(fileName);
	        if(url){
	            $(this).parent(".addinput").show();
	            //alert(111)
	            $(this).siblings("span").html(fileName);
	        }else{
	            $(this).parent(".addinput").empty(); 
	        }
    }
});

$(document).on('click', ".delectfile" , function(){
    $(this).parent(".addinput").remove();
});

//隐藏信息输入框
$("#id_send_msg").click( function(){
        if($(this).attr('checked')){
                $("#note_text").show();
                $("#send_remind").show();
        }else{
                $("#note_text").hide();
                $("#send_remind").hide();
                } 
});	
/*	//表单提交提示隐藏
        $("#post_form input,#post_form select,#post_form textarea").blur(function() {
                objInput = $(this)
                formId=$("#post_form")
                chaozuo(objInput,formId); 
        });*/
	 
  function chaozuo(obj,formObj){
	  if(!obj.parent().find(".erro-tips").text()){
		   return false;
		}else{
			fname = obj.attr("name")
			$.ajax({ // create an AJAX call...
				data: $(formObj).serialize(), // get the form data
				type: $(formObj).attr('method'), // GET or POST
				url: $(formObj).attr('action'), // the file to call
				success: function(response) { // on success.. 
					error = response[fname]
					if(!error){
						obj.parent().find(".erro-tips").empty()
					}
				}
			});
			return false;
		 }
	 }
	 //列表页删除提醒
	 function remindDel(){
		var gnl=confirm("你真的确定要删除吗?"); 
		if (gnl==true){ 
			return true; 
		}else{ 
			return false; 
		} 
	}
	 
});
 
//日期插件中文样式
jQuery(function($){
	$.datepicker.regional['zh-CN'] = {
		closeText: '关闭',
		prevText: '<上月',
		nextText: '下月>',
		currentText: '今天',
		monthNames: ['一月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月'],
		monthNamesShort: ['一','二','三','四','五','六','七','八','九','十','十一','十二'],
		dayNames: ['星期日','星期一','星期二','星期三','星期四','星期五','星期六'],
		dayNamesShort: ['周日','周一','周二','周三','周四','周五','周六'],
		dayNamesMin: ['日','一','二','三','四','五','六'],
		weekHeader: '周',
		dateFormat: 'yy-mm-dd',
		firstDay: 1,
		isRTL: false,
		showMonthAfterYear: true, 
		yearSuffix: '年'};
	$.datepicker.setDefaults($.datepicker.regional['zh-CN']);
});
//textarea长度验证
function checktext(text) {
    allValid = true;
    for (i = 0; i < text.length; i++) {
        if (text.charAt(i) != " ") {
            allValid = false;
            break;
        }
    }
    return allValid;
}
 
//输入框字数提示
function gbcount(messages, totals, useds, remains) {
    var max;
    max = totals.value;
    if (messages.value.length > max) {
        messages.value = messages.value.substring(0, max);
        useds.value = max;
        remains.value = 0;
        $("#remains_text").text(remains.value);
        alert('抱歉，你输入的内容已超过'+max+'个字!');
    } else {
	useds.value = messages.value.length;
        remains.value = max - useds.value;
        $("#remains_text").text(remains.value);
    }
} 

$(function(){ 
	//公文高级搜
   $("#adv-search-btn").toggle(function(){
		//$(this).addClass("smlip");
		//$("#slimp-seatch").hide();
		$(this).text("普通搜索");
		$("#adv-search").show();
		$(this).addClass("hide");
		$(this).removeClass("show");
		
	},function(){
		//$(this).removeClass("smlip");
		$(this).text("高级搜索");
		$("#adv-search").hide();
		$("#slimp-seatch").show();
		$(this).addClass("show");
		$(this).removeClass("hide");
	});
	$(".shijainduan").datepicker({dateFormat: 'yy-mm-dd'});
	$("#from").datepicker({ 
		buttonText: 'Choose',
		defaultDate: "+1w",
		changeMonth: true,
		numberOfMonths: 1,
		minDate: '+1m +1w', 
		onClose: function(selectedDate) {
		 $("#to").datepicker("option", {dateFormat: 'yy-mm-dd'}, "minDate", selectedDate);
		}
	}); 
	$("#to").datepicker({
	   // minDate: 2012-05-09,
		buttonText: 'Choose',
		defaultDate: "+1w",
		changeMonth: true,
		numberOfMonths: 1,
		onClose: function(selectedDate) {
		  $("#from").datepicker("option", {dateFormat: 'yy-mm-dd'}, "maxDate", selectedDate);
		}
	});
})

  function previewImage(file,imgId){  
           if (file.files && file.files[0]){  
               var img = document.getElementById(imgId);  
               var reader = new FileReader();  
               reader.onload = function(evt){img.src = evt.target.result;}  
               reader.readAsDataURL(file.files[0]);  
           }else{  
               file.select();  
               var src = document.selection.createRange().text;  
               $("#"+imgId).attr("src",src);
           }  
  }
     

$(function(){ 
	$(".toggle_button").click(function(){ //右侧栏 事件
		if($(this).data("toggle")=="toggle"){
			$(".sidebar_right").hide();
			$(this).find("span").removeClass("nav_ioc_r");
			$(this).find("span").addClass("nav_ioc_l");
			$(this).data("toggle","onToggle"); 
			$(this).css({ right:"0px",top:"10px"});
		} else{
			$(this).data("toggle","toggle");
			$(".sidebar_right").show();
			$(this).find("span").removeClass("nav_ioc_l");
			$(this).find("span").addClass("nav_ioc_r");  
			$(this).css({ right:"206px",top:"10px"});
		}
		
	});

	$(".drop_down").hover(function(){ //更多
		$(this).find(".more").addClass("on");
		$(this).find(" .more span").addClass("onupbg");
		$(this).find(".more span").removeClass("ondowbg");
		$(".drop_down_list").show();	
	},function(){
		$(this).find(".more").removeClass("on");
		$(this).find(" .more span").addClass("ondowbg");
		$(this).find(".more span").removeClass("onupbg");
		$(".drop_down_list").hide();
	}); 
});
function piece_operate(){//图片旋转,拖放,缩放操作函数
	$('.img_block').resizable(//图片块
	{ 
		//handles: "n,e,s, w,ne, nw, se, sw",
		handles: "n,e,s, w,se, sw",  
		maxWidth: 300, 
		maxHeight:300,
		minWidth: 100,
		minHeight: 100,
		aspectRatio:true,
		refreshPositions: false,
		delay: 200,
		autoHide: true,
		accept: ".img_block",
		scope: "tasks",
	}
	).draggable({delay: 200,containment: $('.container'),cursor: 'pointer'}).rotatable();
	$( ".img_block" ).droppable({//图片块接受图片
			greedy: true,
			drop: function( event, ui ) {
				var test = ui.draggable[0].className.indexOf("test_img"); 
				if(test!=-1){
					$(this).find('img').attr("src",ui.draggable[0].src); 
				}
			}
		});

	    $( "#box_canvas" ).droppable({ //画布接收图片
	      	drop: function( event, ui ) { 
	      		 var test = ui.draggable[0].className.indexOf("test_img"); 
	      		if(test!=-1){
	      		   if($(this).is("#box_canvas")) {  
		      			dropPiece.infoBox = '<div class="target img_block" style="left: 199px; top: 280px;"><div class="close_btn"></div><img  src='+ ui.draggable[0].src +' class=""></div>';
						$("#box_canvas").append(dropPiece.infoBox); 
				    	piece_operate();
			    	}
	      		}  
				 
		    } 
	    });
}
function piece_operate_font(){//文子块旋转,拖放,缩放操作函数
	$('.font_block').resizable(
		{ 
			//handles: "n,e,s, w,ne, nw, se, sw",
			handles: "n,e,s,w",  
			maxWidth: 300, 
			maxHeight:300,
			minWidth: 100,
			minHeight: 100,
			aspectRatio:true,
			refreshPositions: false,
			delay: 20000,
			autoHide: true
		}
	).draggable({delay: 200,containment: $('.container'),cursor: 'pointer'}).rotatable();
	$(".set_fontColor").bigColorpicker(function(el,color){ //设置字体颜色
		$(el).parent().parent('.font_style_box').show();
    	$(el).css("backgroundColor",color);
    	$(el).parent().parent().siblings(".input_text").css("color",color); 
    });
} 
var dropPiece = { //主操作类
	infoBox :"",
	init: function(){
		piece_operate();
		dropPiece.dropClick();
		piece_operate_font();
		//<input class="input_text" type="text" vaule="" placeholder="双击添加文字"/> <div class="input_text" contenteditable="true" placeholder="双击添加文字"></div>
	},
	dropClick: function(){
		$("#piece_imgbox").click(function(){ //添加图片块
			var hhh =$("#hhh").val(); 
			var imgBox = '<div class="target img_block ui-resizable ui-draggable" style="-webkit-transform: rotate(0rad);"><div class="close_btn"> </div><img  src="'+hhh+'oa/images/growth/init_img.jpg" class=""></div>';
			$("#box_canvas").append(imgBox);
			piece_operate();	
		});
		$("#piece_infobox").click(function(){ //添加文子快  
			var infoBox = '<div class="target font_block ui-resizable ui-draggable" style="-webkit-transform: rotate(336.1418455386954deg); left: 70px; top: 182px;">'
						+'<div class="close_btn_1 "></div>'
						+'<div class="input_text" contenteditable="true" placeholder="双击编辑文字">双击编辑文字</div>'
						+'<div class="font_style_box"><select class="set_fontStyle_select">'
						+'<option vaule="微软雅黑">微软雅黑</option><option vaule="微软雅黑雅黑雅黑">微软雅黑雅黑雅黑</option></select>'
						+'<select class="set_fontSize_select"><option vaule="8px">8px</option><option vaule="10px">10px</option><option vaule="12px">12px</option> <option selected="selected" vaule="14px">14px</option>'
						+'<option vaule="16px">16px</option><option vaule="18px">18px</option><option vaule="20px">20px</option><option vaule="21px">21px</option><option vaule="22px">22px</option>'
						+'<option vaule="24px">24px</option><option vaule="26px">26px</option><option vaule="28px">28px</option><option vaule="30px">30px</option><option vaule="32px">32px</option>'
						+'<option vaule="34px">34px</option><option vaule="36px">36px</option></select>'
						+'<div class="block-select"><a href="javascript:void(0)" class="a-picker-block set_fontColor" ></a></div>'
						+'<div class="down_fontzip"><a href="javascript:void(0)" class="">下载字体包</a></div></div></div>';
			$("#box_canvas").append(infoBox);
			piece_operate_font();
			// $(".input_text").focus();	
		}); 
		$("#server_canvas").click(function(){//保存
			var canvas = $("#box_canvas").html();
		});
		
		$( ".test_img" ).draggable({
			appendTo: $("#box_canvas"),
			helper: "clone" 
		});
		
	    //删除图片
	    $(document).on('click','.close_btn','.close_btn_1',function(){ 
	    	$(this).parent('.target').remove(); 
	    });
	    //删除图片
	    $(document).on('click','.close_btn_1',function(){ 
	    	$(this).parent('.target').remove(); 
	    });
        //拖动列表顺序     
	    $("#cart ol" ).sortable({ 
	    	containment:$('#cart ol'),
	      	sort: function() {}
    	});
    	$( "#cart ol" ).disableSelection();
    	//删除列表元素
		$(document).on('click','.close_btn_i',function(){ 
	    	$(this).parent('li').remove();

	    });
	   
	    //鼠标编辑图片事件
	    $(document).on("mouseover",".target",function(){
	    	if($(this).is(".img_block")){ 
	    		$(this).find(".close_btn").addClass("close_ico_bg");  
	    	}else if($(this).is(".font_block")){
	    		$(this).find(".close_btn_1").addClass("close_ico_bg_1");
		    	//$(this).find("img").addClass("border-ico");
		    	//$(this).find(".ui-rotatable-handle").addClass("ui-draggable-ico-bg");
	    	}
	    	$(this).find(".ui-rotatable-handle").addClass("ui-draggable-ico-bg");
            //$(this).find("img").addClass("border-ico");
	    	// $(this).find(".ui-resizable-handle").addClass("ui-resizable-ico-bg");
	    }).on("mouseout",".target", function(){
	        //$(this).find("img").removeClass("border-ico");
	        if($(this).is(".img_block")){
	        	$(this).find(".close_btn").removeClass("close_ico_bg"); 
	        }else if($(this).is(".font_block")){ 
	        	$(this).find(".close_btn_1").removeClass("close_ico_bg_1");
	        } 
	        $(this).find(".ui-rotatable-handle").removeClass("ui-draggable-ico-bg");
	    	// $(this).find(".ui-resizable-handle").removeClass("ui-resizable-ico-bg");
	    });
	    $(document).on("dblclick",".target", function(){ 
	    	$(this).find(".input_text").focus();
	    	$(this).find(".font_style_box").show();
	    });
	    $(document).on('blur','.input_text',function(){ 
	    	 //$(this).siblings(".font_style_box").hide();
	    });
	    $(document).on('change',".set_fontSize_select",function(){//设置文字大小
	    	var size = $(this).find('option:selected').val(); 
	    	$(this).parent().siblings(".input_text").css({fontSize:size,textAlign:"left",lineHeight:size});

	    });
	    $(document).on('change',".set_fontStyle_select",function(){//设置字体
	    	var fontFamily = $(this).find('option:selected').val(); 
	    	$(this).parent().siblings(".input_text").css('font-family',fontFamily);

	    });
	    $(document).on('click',"#box_canvas",function(e){//设置字体
	    	if ( $(e.target).eq(0).is( $(".font_block ,.input_text ,.set_fontStyle_select,.set_fontSize_select,.down_fontzip,#bigpicker ,#bigSections") ) ){ 
	    	}else{ 
	    		$(".font_style_box").hide();
	    	}
	    });
	    $( "#slider-range-min" ).slider({// 控制画布大小
		      range: "min",
		      value: 100,
		      min: 100,
		      max: 300,
		      slide: function( event, ui ) {
		        $( "#amount" ).text(ui.value +'%');
		        $( "#box_canvas" ).css('zoom',ui.value+"%");
		      }
	    });
    	$( "#amount" ).text($( "#slider-range-min" ).slider( "value" )+"%");
		//$(".test_img").draggable({ 
		// 	opacity: 0.7,
		// 	helper: "clone",
		// 	hoverClass:"ui-state-active",
		// 	drop: function( event, ui ) {
		// 		console.log(event);
  		//  	alert(11111);
		//     	 //$(this).data(); 
		//     } 
		//}); 
	}

}


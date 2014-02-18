	//确认操作
	$('.a_confirm_link').on('click', function(){
		var self = $(this);
        url = self.attr('href');
		message = self.data('title');
        if(typeof message == 'undefined'){
            message = '确认执行此操作吗？'
			};

		Bconfirm({
			message: message,
			handler: function(button){
                window.location.href=url;
			}
		});
		AutoFoot();
		return false;
	});

	//确认操作
	$('.a_ajax_link').on('click', function(){
		var self = $(this);
		title = self.attr('title');
		url = self.attr('href');
		
		Bajax({
			url: url,
			title: title,
			handler: function(button){
                window.location.href=url;
			}
		});
		return false;
	});
	
	//确认后执行函数  action-type 为函数名  action-data 为函数参数
	$('.a_confirm_action').on('click', function(){
		var self = $(this);
        url = self.attr('href');
		message = self.data('title');

        action = self.attr('action-type');
        data = self.attr('action-data');
        handler = eval(action);

        if(typeof message == 'undefined'){
            message = '确认执行此操作吗？';
		};

		Bconfirm({
			message: message,
			handler: function(button){
                handler(self,data);
			}
		});
		return false;
	});

	$('.a_alert_link').on('click', function(){
		var self = $(this);
		message = self.data('title');
		url = self.attr('href');
		$.get(url, '', function(result){
			if (result == 1) {
				Alert(message + '成功', '标题', function(){
					reload();
				});
			}
			else {
				Alert(message + '失败');
			}
			
		});
		return false;
	});

function reload(){
	window.location.reload();
}

function redirect(url){
	window.location.href=url;
}


/*
 * 弹出框
 */
function Balert(message, title, callback){
	//$("#dialog").dialog("destroy");
	
	if ($("#dialog-message").length == 0) {
		$("body").append('<div id="dialog-message"></div>');
	}
	
	var content_text = message;
	var btn_ok_text = '确定';
	var btn_cancel_text = '取消';
	var title_text = '消息框';

	var div_html = '<div class="hide modal in" id="modal" style="display: block; "><div class="modal-header">    <a class="close" data-dismiss="modal">×</a>    <h3>'+title_text+'</h3></div><div class="modal-body">    <p>'+content_text+'</p></div><div class="modal-footer">    <a class="btn btn-primary btn-danger" data-dismiss="modal" href="#">'+btn_ok_text+'</a></div></div>'
	$("#dialog-message").html(div_html);
	$('#dialog-message').modal('toggle');
}
/*
 * 确认框
 *
 * object {message:'确认执行此操作吗',hander:function()}
 * @params message:显示消息的内容； hander:单击确认后处理的函数
 *
 */
 
function Bconfirm(object){
	var message = object.message;
	var callback = object.handler;
	
	$("#dialog-confirm").remove();
	if ($("#dialog-confirm").length == 0) {
		$("body").append('<p id="dialog-confirm"> 加载中,请稍等...</p>');
	}
	var content_text = message;
	var btn_ok_text = '确定';
	var btn_cancel_text = '取消';
	var title_text = '消息框';

	var div_html = '<div class="hide modal in" id="modal" style="display: block; "><div class="modal-header">    <a class="close" data-dismiss="modal">×</a>    <h3>'+title_text+'</h3></div><div class="modal-body">    <p>'+content_text+'</p></div><div class="modal-footer">    <a class="btn btn-primary" data-dismiss="modal" href="#">'+btn_ok_text+'</a>    <a class="btn" data-dismiss="modal" href="#">'+btn_cancel_text+'</a></div></div>'
	$("#dialog-confirm").html(div_html);
	if (typeof(callback) == "function") {
		$("#modal .btn-primary").bind( 'click', function(event) {
			$('#dialog-confirm').modal('hide');
			callback.call();
			return false;
		} );
	};
	$('#dialog-confirm').modal('toggle');
	return false;
}

function Bajax(object){
	var message = object.message;
	var callback = object.handler;
	var title = object.title;
	var url = object.url;
	
	$("#dialog-confirm").remove();
	if ($("#dialog-confirm").length == 0) {
		$("body").append('<p id="dialog-confirm"> 加载中,请稍等...</p>');
	}

	//读取数据
	$.get(url, function(data) {
		message = data;
		//$("#dialog-confirm").load(url);
		var content_text = message;
		var btn_ok_text = '确定';
		var btn_cancel_text = '取消';
		var title_text = '消息框';

		var div_html = '<div class="hide modal in" id="modal" style="display: block; "><div class="modal-header">  </div></div>'
		$("#dialog-confirm").html(div_html);
		$('#dialog-confirm').modal('toggle');
	});
}

// 解决 django 启用csrf，ajax错误问题
$(document).ajaxSend(function(event, xhr, settings) {  
    function getCookie(name) {  
        var cookieValue = null;  
        if (document.cookie && document.cookie != '') {  
            var cookies = document.cookie.split(';');  
            for (var i = 0; i < cookies.length; i++) {  
                var cookie = jQuery.trim(cookies[i]);  
                // Does this cookie string begin with the name we want?  
                if (cookie.substring(0, name.length + 1) == (name + '=')) {  
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));  
                    break;  
                }  
            }  
        }  
        return cookieValue;  
    }  
    function sameOrigin(url) {  
        // url could be relative or scheme relative or absolute  
        var host = document.location.host; // host + port  
        var protocol = document.location.protocol;  
        var sr_origin = '//' + host;  
        var origin = protocol + sr_origin;  
        // Allow absolute or scheme relative URLs to same origin  
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||  
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||  
            // or any other URL that isn't scheme relative or absolute i.e relative.  
            !(/^(\/\/|http:|https:).*/.test(url));  
    }  
    function safeMethod(method) {  
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));  
    }  
 
    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {  
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));  
    }  
});

//悬浮提醒框
Notice = {
	success:function(message) {
        jSuccess(message,{
					VerticalPosition : 'center',
					HorizontalPosition : 'center'
		});
    }
    ,warning:function(message) {
        jNotify(message,{
					VerticalPosition : 'center',
					HorizontalPosition : 'center'
		});
    }
    ,error:function(message) {
        jError(message,{
					VerticalPosition : 'center',
					HorizontalPosition : 'center'
		});
    }
    ,info:function(message) {
        jNotify(message,{
					VerticalPosition : 'center',
					HorizontalPosition : 'center'
		});
    }
    ,loading:function(message) {
        jNotify(message,{
					VerticalPosition : 'center',
					HorizontalPosition : 'center'
		});
    }
}
//脚部自动定位
window.NOAUTOFOOT = 0;
function AutoFoot(){
		if(NOAUTOFOOT==1) {
			return false;
		}
    	if(($('#container').offset().top + $('#container').height() + 30) < $(window).height()){
    		$('#footer').css({position: 'fixed', left: 0,bottom: 0});
    	} else {
    		$('#footer').css({position: 'static', marginTop: 30});
    	}
}
//阻止冒泡及跳链
function stopBubble(event){
	if (event && event.stopPropagation){
		event.stopPropagation()
	}else{
		window.event.cancelBubble=true
	}
	if ( event && event.preventDefault ){
        event.preventDefault()
    }else{ 
        window.event.returnValue = false
    }
    return false
}

/* 滚到头部
  * =============================== */
var scrolltotop={
	setting: {startline:100, scrollto: 0, scrollduration:250, fadeduration:[500, 100]},
	controlHTML: '<a href="#top" class="top_stick">&nbsp;</a>',
	controlattrs: {offsetx:12, offsety:50},
	anchorkeyword: '#top',

	state: {isvisible:false, shouldvisible:false},

	scrollup:function(){
		if (!this.cssfixedsupport) {
			this.$control.css({opacity:0,display:'none'})
		};//点击后隐藏#topcontrol这个div
		var dest=isNaN(this.setting.scrollto)? this.setting.scrollto : parseInt(this.setting.scrollto);
		if (typeof dest=="string" && jQuery('#'+dest).length==1) { //检查若scrollto的值是一个id标记的话
			dest=jQuery('#'+dest).offset().top;
		} else { //检查若scrollto的值是一个整数
			dest=this.setting.scrollto;
		};
		this.$body.animate({scrollTop: dest}, this.setting.scrollduration);
	},

	keepfixed:function(){
		//获得浏览器的窗口对象
		var $window=jQuery(window);
		//获得#topcontrol这个div的x轴坐标
		var controlx=$window.scrollLeft() + $window.width() - this.$control.width() - this.controlattrs.offsetx;
		//获得#topcontrol这个div的y轴坐标
		var controly=$window.scrollTop() + $window.height() - this.$control.height() - this.controlattrs.offsety;
		//随着滑动块的滑动#topcontrol这个div跟随着滑动
		this.$control.css({left:controlx+'px', top:controly+'px'});
	},

	togglecontrol:function(){
		//当前窗口的滑动块的高度
		var scrolltop=jQuery(window).scrollTop();
		if (!this.cssfixedsupport) {
			this.keepfixed();
		};
		//若设置了startline这个参数，则shouldvisible为true
		this.state.shouldvisible=(scrolltop>=this.setting.startline)? true : false;
		//若shouldvisible为true，且!isvisible为true
		if (this.state.shouldvisible && !this.state.isvisible){
			this.$control.show();
			this.$control.stop().animate({opacity:1}, this.setting.fadeduration[0]);
			this.state.isvisible=true;
		} //若shouldvisible为false，且isvisible为false
		else if (this.state.shouldvisible==false && this.state.isvisible){
			this.$control.hide();
			this.$control.stop().animate({opacity:0}, this.setting.fadeduration[1]);
			this.state.isvisible=false;
		}
	},

	init:function(){
		jQuery(document).ready(function($){
			var mainobj=scrolltotop;
			var iebrws=document.all;
			mainobj.cssfixedsupport=!iebrws || iebrws && document.compatMode=="CSS1Compat" && window.XMLHttpRequest; //not IE or IE7+ browsers in standards mode
			mainobj.$body=(window.opera)? (document.compatMode=="CSS1Compat"? $('html') : $('body')) : $('html,body');

			//包含#topcontrol这个div
			mainobj.$control=$('<div id="topcontrol">'+mainobj.controlHTML+'</div>')
				.css({position:mainobj.cssfixedsupport? 'fixed' : 'absolute', bottom:mainobj.controlattrs.offsety, right:mainobj.controlattrs.offsetx, opacity:0,display:'none', cursor:'pointer'})
				.attr({title:'返回顶部'})
				.click(function(){mainobj.scrollup(); return false;})
				.appendTo('body');

			if (document.all && !window.XMLHttpRequest && mainobj.$control.text()!='') {//loose check for IE6 and below, plus whether control contains any text
				mainobj.$control.css({width:mainobj.$control.width()}); //IE6- seems to require an explicit width on a DIV containing text
			};

			mainobj.togglecontrol();

			//点击控制
			$('a[href="' + mainobj.anchorkeyword +'"]').click(function(){
				mainobj.scrollup();
				return false;
			});

			$(window).bind('scroll resize', function(e){
				mainobj.togglecontrol();
			});
		});
	}
};

scrolltotop.init();

/* 悬浮名片
  * =============================== */
!function ($) {

  var Namecard = function (element, options) {
  	this.init('namecard', element, options)
  }
  //名片公用方法
  Namecard.prototype = {
  	//标记本对象上一个读取用户
  	lastUid: 0
  	//初始化
  	,  init: function (type, element, options) {
  	  this.type = type
      this.$element = $(element)
      this.options = this.getOptions(options)
      this.uid = this.$element.data('uid')

      var eventIn
        , eventOut
        , $card = this.card()

      if (this.options.trigger == 'click') {
        this.$element.on('click.' + this.type, this.show)
      } else if (this.options.trigger == 'hover') {
        eventIn = this.options.trigger == 'hover' ? 'mouseenter' : 'focus'
        eventOut = this.options.trigger == 'hover' ? 'mouseleave' : 'blur'
        this.$element.on(eventIn + '.' + this.type, $.proxy(this.enter, this))
        this.$element.on(eventOut + '.' + this.type, $.proxy(this.leave, this))
      }
    }
  //获取配置参数
  , getOptions: function (options) {
      options = $.extend({}, $.fn[this.type].defaults, options)

      if (options.delay && typeof options.delay == 'number') {
        options.delay = {
          show: options.delay
        , hide: 500//options.delay
        }
      }

      return options
    }
  //鼠标移入时执行函数
  , enter: function (e) {
      var self = $(e.currentTarget)[this.type](this._options).data(this.type)

      if (!self.options.delay || !self.options.delay.show) return self.show()

      clearTimeout(this.timeout)
      self.hoverState = 'in'
      this.timeout = setTimeout(function() {
        if (self.hoverState == 'in') self.show()
      }, self.options.delay.show)
    }
  //鼠标移出时执行函数
  , leave: function (e) {
      var self = $(e.currentTarget)[this.type](this._options).data(this.type)

      if (this.timeout) clearTimeout(this.timeout)
      if (!self.options.delay || !self.options.delay.hide) return self.hide(e)

      self.hoverState = 'out'
      this.timeout = setTimeout(function() {
        if (self.hoverState == 'out') self.hide(e)
      }, self.options.delay.hide)
    }
  //显示名片
  , show: function () {
  		var pos
		  , $card = this.card()

		pos = this.getPosition()
		if ( pos.pos == 'right' ){
			$card.find('#card-arrow-in').addClass('card-arrow-in-right')
			$card.find('#card-arrow-out').addClass('card-arrow-out-right')
		} else {
			$card.find('#card-arrow-in').addClass('card-arrow-in-left')
			$card.find('#card-arrow-out').addClass('card-arrow-out-left')
		}
		$card
			.remove()
			.css({ top: pos.top, left: pos.left })
		$card.appendTo(document.body)
		$card.on('mouseleave', $.proxy(this.hide, this))
		if (this.lastUid != this.uid){
			this.setContent()
			this.lastUid = this.uid
		}		
  	}
  //移除名片
  , hide: function (e) {
		var $card = this.card()
		  , relTarg = e.toElement || e.relatedTarget
		var r = relTarg.id

	  	if( r != 'namecard' && r != 'card-in' && r != 'card-arrow-in' && r != 'card-arrow-out' && r != 'card-img' && r != 'card-span' && r != 'card-p' ){
      		if ( $card.find('#card-arrow-in').hasClass('card-arrow-in-right') ){
      			$card.find('#card-arrow-in').removeClass('card-arrow-in-right')
      			$card.find('#card-arrow-out').removeClass('card-arrow-out-right')
      		} else if  ( $card.find('#card-arrow-in').hasClass('card-arrow-in-left') ){
      			$card.find('#card-arrow-in').removeClass('card-arrow-in-left')
      			$card.find('#card-arrow-out').removeClass('card-arrow-out-left')
      		}
      		$card.unbind('mouseleave')
      		$card.remove()
      	}

      	return this
    }
  //获取名片JQ对象
  , card: function () {
      return this.$card = this.$card || $(this.options.template)
    }
  //获取名片显示位置
  , getPosition: function () {
		var ol = this.$element.offset().left
		  , ot = this.$element.offset().top
		  , ow = this.$element.width()
		  , cl = $('#container').offset().left
		  , cw = $('#container').width()
		if ((cl + cw - ol) < 400){
			return { pos: 'right', left: ol - 312, top: ot - 10 }
			
		} else {
			return { pos: 'left', left: ol + ow + 8, top: ot - 10 }
		}
  	}
  //AJAX获取用户信息
  , setContent: function () {
  		var uid = this.uid
  		  , $e = $('#card-in')
  		$e.html(this.options.loadingText)
  		maxWord = this.options.maxWord
  		url = '/vcar/?uid='+uid
  		data = uid
  		$.get(url, data, function(result){
		var con = result.con;
		if (result.type == 'ok') {
			
			$e.html(con);
		}
	},"json");
  	}
  }

 /* 名片调用方法
  * ======================== */

  $.fn.namecard = function (option) {
    return this.each(function () {
      var $this = $(this)
        , data = $this.data('namecard')
        , options = typeof option == 'object' && option
      if (!data) $this.data('namecard', (data = new Namecard(this, options)))
      if (typeof option == 'string') data[option]()
    })
  }

  $.fn.namecard.defaults = {
    loadingText: '加载中...'
  , delay: 500
  , trigger: 'hover'
  , maxWord: 40
  , template: '<div id="namecard" style="z-index:10000000;"><div id="card-arrow-out"></div><div id="card-arrow-in"></div><div id="card-in"></div></div>'
  }

  $.fn.namecard.Constructor = Namecard

}(window.jQuery);



/************************************************************************
*************************************************************************
@Name :       	jNotify - jQuery Plugin
@Revison :    	2.0
@Date : 		01/2011
@Author:     		Surrel Mickael (www.myjqueryplugins.com - www.msconcept.fr)  -  Croissance Net (www.croissance-net.com)
@Support:    	FF, IE7, IE8, MAC Firefox, MAC Safari
@License :		Open Source - MIT License : http://www.opensource.org/licenses/mit-license.php

**************************************************************************
*************************************************************************/
(function($){

	$.jNotify = {
		defaults: {
			/** VARS - OPTIONS **/
			autoHide : true,				// Notify box auto-close after 'TimeShown' ms ?
			clickOverlay : false,			// if 'clickOverlay' = false, close the notice box on the overlay click ?
			MinWidth : 100,					// min-width CSS property
			TimeShown : 3000, 				// Box shown during 'TimeShown' ms
			ShowTimeEffect : 200, 			// duration of the Show Effect
			HideTimeEffect : 200, 			// duration of the Hide effect
			LongTrip : 15,					// in pixel, length of the move effect when show and hide
			HorizontalPosition : 'right', 	// left, center, right
			VerticalPosition : 'bottom',	 // top, center, bottom
			ShowOverlay : false,				// show overlay behind the notice ?
			ColorOverlay : '#000',			// color of the overlay
			OpacityOverlay : 0.3,			// opacity of the overlay
			
			/** METHODS - OPTIONS **/
			onClosed : null,
			onCompleted : null
		},

		/*****************/
		/** Init Method **/
		/*****************/
		init:function(msg, options, id) {
			opts = $.extend({}, $.jNotify.defaults, options);

			/** Box **/
			if($("#"+id).length == 0)
				$Div = $.jNotify._construct(id, msg);

			// Width of the Brower
			WidthDoc = parseInt($(window).width());
			HeightDoc = parseInt($(window).height());

			// Scroll Position
			ScrollTop = parseInt($(window).scrollTop());
			ScrollLeft = parseInt($(window).scrollLeft());

			// Position of the jNotify Box
			posTop = $.jNotify.vPos(opts.VerticalPosition);
			posLeft = $.jNotify.hPos(opts.HorizontalPosition);

			// Show the jNotify Box
			if(opts.ShowOverlay && $("#jOverlay").length == 0)
				$.jNotify._showOverlay($Div);

			$.jNotify._show(msg);
		},

		/*******************/
		/** Construct DOM **/
		/*******************/
		_construct:function(id, msg) {
			$Div = 
			$('<div id="'+id+'"/>')
			.css({opacity : 0,minWidth : opts.MinWidth})
			.html(msg)
			.appendTo('body');
			return $Div;
		},

		/**********************/
		/** Postions Methods **/
		/**********************/
		vPos:function(pos) {
			switch(pos) {
				case 'top':
					var vPos = ScrollTop + parseInt($Div.outerHeight(true)/2);
					break;
				case 'center':
					var vPos = ScrollTop + (HeightDoc/2) - (parseInt($Div.outerHeight(true))/2);
					break;
				case 'bottom':
					var vPos = ScrollTop + HeightDoc - parseInt($Div.outerHeight(true));
					break;
			}
			return vPos;
		},

		hPos:function(pos) {
			switch(pos) {
				case 'left':
					var hPos = ScrollLeft;
					break;
				case 'center':
					var hPos = ScrollLeft + (WidthDoc/2) - (parseInt($Div.outerWidth(true))/2);
					break;
				case 'right':
					var hPos = ScrollLeft + WidthDoc - parseInt($Div.outerWidth(true) + 20);
					break;
			}
			return hPos;
		},

		/*********************/
		/** Show Div Method **/
		/*********************/
		_show:function(msg) {
			$Div
			.css({
				top: posTop,
				left : posLeft
			});
			switch (opts.VerticalPosition) {
				case 'top':
					$Div.animate({
						top: posTop + opts.LongTrip,
						opacity:1
					},opts.ShowTimeEffect,function(){
						if(opts.onCompleted) opts.onCompleted();
					});
					if(opts.autoHide)
						$.jNotify._close();
					else
						$Div.css('cursor','pointer').click(function(e){
							$.jNotify._close();
						});
					break;
				case 'center':
					$Div.animate({
						opacity:1
					},opts.ShowTimeEffect,function(){
						if(opts.onCompleted) opts.onCompleted();
					});
					if(opts.autoHide)
						$.jNotify._close();
					else
						$Div.css('cursor','pointer').click(function(e){
							$.jNotify._close();
						});
					break;
				case 'bottom' :
					$Div.animate({
						top: posTop - opts.LongTrip,
						opacity:1
					},opts.ShowTimeEffect,function(){
						if(opts.onCompleted) opts.onCompleted();
					});
					if(opts.autoHide)
						$.jNotify._close();
					else
						$Div.css('cursor','pointer').click(function(e){
							$.jNotify._close();
						});
					break;
			}
		},

		_showOverlay:function(el){
			var overlay = 
			$('<div id="jOverlay" />')
			.css({
				backgroundColor : opts.ColorOverlay,
				opacity: opts.OpacityOverlay
			})
			.appendTo('body')
			.show();

			if(opts.clickOverlay)
			overlay.click(function(e){
				e.preventDefault();
				$.jNotify._close();
			});
		},


		_close:function(){
				switch (opts.VerticalPosition) {
					case 'top':
						if(!opts.autoHide)
							opts.TimeShown = 0;
						$Div.delay(opts.TimeShown).animate({
							top: posTop-opts.LongTrip,
							opacity:0
						},opts.HideTimeEffect,function(){
							$(this).remove();
							if(opts.ShowOverlay && $("#jOverlay").length > 0)
								$("#jOverlay").remove();
								if(opts.onClosed) opts.onClosed();
						});
						break;
					case 'center':
						if(!opts.autoHide)
							opts.TimeShown = 0;
						$Div.delay(opts.TimeShown).animate({
							opacity:0
						},opts.HideTimeEffect,function(){
							$(this).remove();
							if(opts.ShowOverlay && $("#jOverlay").length > 0)
								$("#jOverlay").remove();
								if(opts.onClosed) opts.onClosed();
						});
						break;
					case 'bottom' :
						if(!opts.autoHide)
							opts.TimeShown = 0;
						$Div.delay(opts.TimeShown).animate({
							top: posTop+opts.LongTrip,
							opacity:0
						},opts.HideTimeEffect,function(){
							$(this).remove();
							if(opts.ShowOverlay && $("#jOverlay").length > 0)
								$("#jOverlay").remove();
								if(opts.onClosed) opts.onClosed();
						});
						break;
				}
		},

		_isReadable:function(id){
			if($('#'+id).length > 0)
				return false;
			else
				return true;
		}
	};

	/** Init method **/
	jNotify = function(msg,options) {
		if($.jNotify._isReadable('jNotify'))
			$.jNotify.init(msg,options,'jNotify');
	};

	jSuccess = function(msg,options) {
		if($.jNotify._isReadable('jSuccess'))
			$.jNotify.init(msg,options,'jSuccess');
	};

	jError = function(msg,options) {
		if($.jNotify._isReadable('jError'))
			$.jNotify.init(msg,options,'jError');
	};
})(jQuery);

$(function() {
	//初始化瀑布流
    var $container = $('.thumbnails,.axis');
    ty = $container.attr("ty");
    cwidth = $container.attr("rel");
    if(cwidth){
        column_width = Number(cwidth);
    }else{
        column_width = 234;
    }

    $container.imagesLoaded(function(){
        $container.masonry({
            itemSelector : '.tile',
            stamp : '.stamp',
            columnWidth: column_width
        });
        $('.stamp').css("visibility","visible");
    });

    if(ty == 'axis'){
        desturl = $('#pagination li.active').next().children('a').attr("href");
        //分页自动加载，新增内容瀑布流化
        $container.infinitescroll({
            navSelector  : '#pagination', 
            nextSelector : $('#pagination li.active').next().children('a'), 
            itemSelector : '.tile:not(.tile-tags)', 
            stamp : '.stamp', 
            loadingImg:'http://weixiao178.com/_static/kinger/img/6RMhx.gif',
            loadingText: "正在加载...",
            donetext: "没有更多页面了",
            pathParse : function(p, pn){
                return [desturl];
            },
            loading:{
                finishedMsg: "没有更多页面了",
                img:'http://weixiao178.com/_static/kinger/img/6RMhx.gif'
            }
        },
        function( newElements ) {
            var $newElems = $( newElements ).css({ opacity: 0 });
            $( newElements ).find('[rel=namecard]').namecard();
            date_parm = $newElems.find('[rel=page_date_parm]:last').val();
            // $newElems.find('[rel=page_parm_date]').remove();
            if(date_parm){
                desturl = "?date=" + date_parm + "&page=2";
                $('#pagination li.active').next().children('a').attr("href",desturl);
            }
            $newElems.imagesLoaded(function(){
                $newElems.animate({ opacity: 1 });
                $container.masonry( 'appended', $newElems, true );
            });
        });
}else{
    //分页自动加载，新增内容瀑布流化
        $container.infinitescroll({
            navSelector  : '#pagination', 
            nextSelector : $('#pagination li.active').next().children('a'), 
            itemSelector : '.tile:not(.tile-tags)', 
            stamp : '.stamp', 
            loadingImg:'http://weixiao178.com/_static/kinger/img/6RMhx.gif',
            loadingText: "正在加载...",
            donetext: "没有更多页面了",
            loading:{
                finishedMsg: "没有更多页面了",
                img:'http://weixiao178.com/_static/kinger/img/6RMhx.gif'
            }
        },
        function( newElements ) {
            var $newElems = $( newElements ).css({ opacity: 0 });
            $( newElements ).find('[rel=namecard]').namecard();
            $newElems.imagesLoaded(function(){
                $newElems.animate({ opacity: 1 });
                $container.masonry( 'appended', $newElems, true );
            });
        });
}
    


    //$tiles = $container.find("li.tile");
    $tiles =  $('.thumbnails').find("li.tile");
	if( /Android|iPhone|iPad/i.test(navigator.userAgent) ){
		  //handheld
		}else{
            $tiles.live("mouseover", function(e){
                $(this).find('.actions').show();
            })
            .live("mouseout", function(e) {
                $(this).find(".actions").hide();
            });
            /**
            $('.axis').find("li.tile").live("mouseover", function(e){
                $(this).find('.actions').show();
            })
            .live("mouseout", function(e) {
                $(this).find(".actions").hide();
            });**/
    }
   

    /* tile_view */
    $('.kDetail-bar .comment').on('click', function(e){
        $('#comment-form .controls textarea#id-comment').focus();
    });

    $("#comment-form").submit(function(){
        $text = $(this).find(".controls textarea#id-comment");
        text_len = $.trim($text.val()).length;
        if (text_len)
            return true;
        else {
            $text.focus();
            return false;
        }
    });
    //喜欢设置 
    $("button.likeable:not(.disabled)").live("click",function(e){
        $btn_like = $(this);
        url = $btn_like.data("href");
        id = $btn_like.data("id");
        $i = $btn_like.find("i");
        $btn_like.addClass("disabled");
        $.post(url,{"id": id},function(data, status){
            if(status != "success")
                return false;
            if (data.liked) {
                $i.addClass("like"); 
                $btn_like.find('span').html("取消喜欢");
            } else {
                $i.removeClass("like"); 
                $btn_like.find('span').html("喜欢");
            }
            $btn_like.removeClass("disabled");
        },"json");
    });
$(".facew").live("mouseover",function(){ 
        $(this).removeClass("face-ico").addClass("Qface-ico");
 }).live("mouseout", function(){
        $(this).removeClass("Qface-ico").addClass("face-ico");
 });
// 2013-1-25

});
// hacker for IE(ie<9) "indexOf" 
if (!Array.prototype.indexOf) {
	Array.prototype.indexOf = function(elt /*, from*/ ) {
		var len = this.length >>> 0;
		var from = Number(arguments[1]) || 0;
		from = (from < 0) ? Math.ceil(from) : Math.floor(from);
		if (from < 0)
			from += len;
		for (; from < len; from++) {
			if (from in this &&
				this[from] === elt)
				return from;
		}
		return -1;
	};
}


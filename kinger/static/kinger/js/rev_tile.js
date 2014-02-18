$(function() {
    //设置喜欢
    $("a[rel=likeable]:not(.disabled)").live("click",function(e){   
        $btn_like = $(this);
        url = $btn_like.data("href");
        id = $btn_like.data("id");
        $i = $btn_like.find("i");
        $btn_like.addClass("disabled");
        $.post(url,{"id": id},function(data, status){ 
            if(status != "success")
                return false;
            if (data.liked) {
                $i.removeClass("no_like");
                $i.addClass("like"); 
                $("#likeable_"+id+ " span").find("i").removeClass("no_like");
                $("#likeable_"+id+ " span").find("i").addClass("like");
                $btn_like.find('.like_type').html("取消喜欢");
                $("#likeable_"+id).find('.like_type').html("取消喜欢");
                $("[rel=view_"+ id +"]").siblings("span").find('i').removeClass("no_like")
                $("[rel=view_"+ id +"]").siblings("span").find('i').addClass("like")
                $("[rel=view_"+ id +"]").html("取消喜欢");
            } else {
                $i.removeClass("like");
                $i.addClass("no_like");
                $("#likeable_"+id+ " span").find("i").removeClass("like");
                $("#likeable_"+id+ " span").find("i").addClass("no_like");
                $("#likeable_"+id).find('.like_type').html("喜欢");
                $btn_like.find('.like_type').html("喜欢");
                $("[rel=view_"+ id +"]").siblings('span').find('i').removeClass("like")
                $("[rel=view_"+ id +"]").siblings('span').find('i').addClass("no_like")
                $("[rel=view_"+ id +"]").html("喜欢"); 
            } 
            $btn_like.removeClass("disabled");
            $btn_like.parent().siblings('.bottom-assess').find(".like_content").find("span").text(data.n_likers);
            $btn_like.parent().siblings('.bottom_describe').find(".like_content").find("span").text(data.n_likers);
            $("#like_conten_"+id).text(data.n_likers); 
            
        },"json");
    });

    //瓦片评论、详情
    // $("a[rel=tile_comment],a[rel=tile_view]").live("click",function(){
    //     var is_login = $("#is_user_login").val();
    //     if(is_login){
    //         url = $(this).data("href"); 
    //         $("#tile_view_conent").empty();
    //         $('#box_tile_view').modal('toggle');
    //         $("body").addClass("body_hide_scroll");
    //         $("html").addClass("body_hide_scroll");//ie6/Ie7
    //         $("#colse").show();  
    //         $.post(url,{},function(result){
    //             data = $.parseJSON(result); 
    //             $("#tile_view_conent").html(data.con).show();  
    //         });
    //     }else{
    //         // jNotify("您尚未登陆");
    //         document.location.href = "/accounts/signin";
    //     }
    // });
   // 瓦片评论、详情
    $("a[rel=tile_comment],a[rel=tile_view],[rel=tile_view]").live("click",function(){ 
        var is_login = $("#is_user_login").val();
        var content =$("#tile_view_conent");
        if(is_login){
            tid = $(this).data("id");
            url = $(this).data("href");
            pre_url = "/axis_pre/" + tid + "/"; 
            content.empty(); 
            $('#box_tile_view').modal('toggle');
            $("body").addClass("body_hide_scroll");
            $("html").addClass("body_hide_scroll");//ie6/Ie7
            $("#colse").show();
            $(".axis_loading").show();
            $.post(pre_url,{},function(result){
                data = $.parseJSON(result); 
                if(data.type == "ok"){
                    content.html(data.con).show(); 
                    $.post(url,{},function(results){
                        d = $.parseJSON(results);
                        content.html("");
                        content.html(d.con).show();
                        $(".axis_loading").hide();
                    });
                }
            });
        }else{
            // jNotify("您尚未登陆");
            document.location.href = "/accounts/signin";
        }
    });

    //瓦片描述修改
    $("#upDatecomment").live('click',function(){ 
        $('#divinput_text').attr("contenteditable","true");
        $('#divinput_text').addClass("test_box");
        $("#divinput_text").focus();
        //$("[rel = picComment]").find("span").hide(); 
        //$("[rel = picComment]").addClass("addborder");
        //$(".input_textarea").val($("[rel = picComment]").find("span").text());
        //$(".input_textarea").show();
        //$(".input_textarea").focus();
        $(this).hide();
        $("#serverDatecomment,#resetComment,.line_nav").show();
    })
    //取消修改 
    $('#resetComment').live('click',function(){ 
        //text = $(this).attr("placeholder");
        //$("[rel = picComment]").find("span").show();
        //$("[rel = picComment]").append(text);
        $('#divinput_text').removeClass("test_box");
        //$("[rel = picComment]").removeClass("addborder");
        //$(".input_textarea").hide();
        $('#divinput_text').removeAttr("contenteditable");
        $("#upDatecomment").show();
        $("#serverDatecomment,.line_nav,#resetComment,.input_textarea").hide();
        $("#divinput_text").text($("#divinput_text").attr("rel"));
    });
    //保存修改
    $("#serverDatecomment").live('click',function(){
        url = $(this).data("href");
        value = $("#divinput_text").text();
        $("#divinput_text").attr("rel",value);
        $('#divinput_text').removeClass("test_box"); 
        $('#divinput_text').removeAttr("contenteditable");
        $("#upDatecomment").show();
        $("#serverDatecomment,.line_nav,#resetComment,.input_textarea").hide();
        tid = $(this).attr("rel");
        $('[rel=desc_'+tid+']').text(value);
        $.post(url,{"tid":tid,"desc":value},function(result){
             data = $.parseJSON(result); 
             if(data.status){ 
                 //$("[rel = picComment]").find("span").text(data.desc);
             } 
        }) 
        $("#ti-"+tid).css("z-index","1");  
    })
    //瓦片评论、详情 翻页
    $("a[rel=tile_pre],a[rel=tile_next],a[rel=tile_detail],[rel=tl_itme]").live("click",function(){
        url = $(this).data("href");
         $(".axis_loading").show();
        $.post(url,{},function(result){
            data = $.parseJSON(result); 
            $("#tile_view_conent").empty(); 
            $("#tile_view_conent").html(data.con).show();
            $(".axis_loading").hide();
        });
    })

    //删除瓦片
    $("a[rel=delete_tile]").live("click",function(){
        r = confirm("你确定要删除这条记录吗？小伙伴们的评论也会一并删除哦～");
        if(r==true){
            url = $(this).data("href");
            document.location.href = url;
        }
    })
   //
    $("a[rel=pic_ico]").live("click",function(){
        url = $(this).data("href");
        $.post(url,{},function(result){
            data = $.parseJSON(result); 
            $("#pic_ico").html('');
            $("#pic_ico").html(data.con).show();
        });
    })

    //鼠标移上显示评论、喜欢按钮
    $("[rel=tiles],.t_itme,.img_box_btn").live("mouseover",function(e){ 
           e.stopPropagation();
           e.preventDefault();
           $(this).find('.assess').show();
    }).live("mouseout", function(e){
            e.stopPropagation();
            e.preventDefault();
           $(this).find('.assess').hide();
    });
     //鼠标移上显示翻页按钮
    $(".content_box").live("mouseover",function(){  
           $(".peg_btn").show();
    }).live("mouseout", function(){
           $(".peg_btn").hide();
    });

    $("#myModal,#box_record,#box_cookbook_view,#box_active,#box_tile_view,#box_theme_view").live('hide', function () { 
     //弹框关闭监听事件
        $("#colse").hide();
        $("#myModal,#box_record,#box_cookbook,#active_view_conent,#tile_view_conent,#theme_view_conent").empty();
        $("body").removeClass("body_hide_scroll");
        $("html").removeClass("body_hide_scroll");//ie6/Ie7  
         $(".axis_loading").hide()
    });
    $("#colse").live('click',function(){ //弹框关闭按钮
         $("#myModal,#box_record_view,#box_cookbook_view,#box_active,#box_tile_view,#box_theme_view").modal('hide');
         //$("body").removeClass("body_hide_scroll");
        // $(this).hide();
         $(".axis_loading").hide()
        $("#myModal,#box_record,#box_cookbook,#active_view_conent,#tile_view_conent,#theme_view_conent").empty();
    });

    // $("#box_theme_view,#box_tile_view").click(function(e){  
    //     $("#box_tile_view,#box_theme_view").modal('hide');
    // });

   //主题弹框
   $("a[rel=theme_view]").live("click",function(){ 
        
        var is_login = $("#is_user_login").val();
        if(is_login){
            tid = $(this).data("id");
            if(!tid){tid = 0;}
            url = $(this).data("href");
            cid = $(this).data("cid");
            if(!cid){cid = 0;}
            pre_url = "/axis_pre/" + tid + "/?ty=theme&cid=" + cid ;
            $("#theme_view_conent").empty();
            $("#box_theme_view").modal('toggle');
            $("body").addClass("body_hide_scroll");
            $("html").addClass("body_hide_scroll");//ie6/Ie7
            $("#colse").show();
            $(".axis_loading").show();
            $.post(pre_url,{},function(result){
                data = $.parseJSON(result);
                if(data.status=='error'){ 
                    $("#theme_view_conent").empty();
                    $("#theme_view_conent").html('<div style=" color:#666666; text-align: center; font-size: 32px; height:320px; line-height:50px; padding-top:200px; width:960px;background: #fff;">没有内容</div>').show(); 
                    $(".axis_loading").hide();
                }else{ 
                    $("#theme_view_conent").html(data.con).show(); 
                    $.post(url,{},function(results){
                        d = $.parseJSON(results); 
                           $("#theme_view_conent").empty();
                           $("#theme_view_conent").html(d.con).show(); 
                           $(".axis_loading").hide(); 
                    })
              }
            });
        }else{
            // jNotify("您尚未登陆");
            document.location.href = "/accounts/signin"

        }
    })

    //主题弹框、详情 翻页
    $("a[rel=theme_pre],a[rel=theme_next],a[rel=theme_detail],[rel=tm_itme]").live("click",function(){ 
        url = $(this).data("href");
         $(".axis_loading").show();
        $.post(url,{},function(result){
            data = $.parseJSON(result);
            if(data.status != false){
                $("#theme_view_conent").empty();
                $("#theme_view_conent").html(data.con).show();
                $(".axis_loading").hide();
             }else{
              jNotify(data.msg);
            } 
        }); 
    })
    //获取评论框的焦点
    $("[rel=comment_input]").live('click', function(){
        $("#id-comments").focus();
    })
    
});

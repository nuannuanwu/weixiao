// JavaScript Document
$(".list tr:even").addClass("bg_color");
$(".list tr").hover(
   function(){ 
		$(this).addClass("atr");
   },
   function(){ 
		$(this).removeClass("atr");
});
$("#upphotobtn").click(function(){
	albumsModal();
})
 
function albumsModal(){
	$('#upPhotoModal').modal({
		backdrop:false
	});
}

$("#status").change(function(){
	var status_id = $(this).val();
	javascript:location.href = '{% url oa_album_detail album.id %}?status=' + status_id;
})
$("#upphotobtn").click(function(){
	albumsModal();
})

function albumsModal(){
	$('#upPhotoModal').modal({
		backdrop:false
	});
} 
$(':checkbox[rel=checkall]').change(function(){
	$(':checkbox[rel=role]').attr('checked',this.checked);
	$(':checkbox[rel=checkall]').attr('checked',this.checked);
	chekck();
})
$(':checkbox[rel=role]').change(function(){
	var flag = true;
	$(':checkbox[rel=role]').each(function() {
        if(!this.checked){
			flag = false;
		}
    });
	$(':checkbox[rel=checkall]').attr('checked',flag);
	chekck();
})

function chekck(){
	var formChek = $("#form_post");
	var checkedlen = formChek.find('input[rel=role]:checked').length;
	if(checkedlen){
		$("#sub_form").removeAttr('disabled')
	}else{
		$("#sub_form").attr('disabled','disabled')
	}
}

/*function check(){  
    var r=confirm("是否删除所选项？");
	if (r==true) {
		//alert("删除成功");
	} else { 
		return false;//false:阻止提交表单  
	}  
}*/
 
        //上传照片 	
	$("#my-uploadphotos").click(function(){
		var inputHtml ='<p class="addinput" style="display:none;"><span class="filesname"></span><input type="file" class="inpitid hide" name="files" accept="image/*" /><a class="delectfile">删除</a></p>';
		$("#quoteRequest").append(inputHtml);
                $(".addinput >input[name=files]:last").click();
		$(".addinput >input[name=files]:last").change(); 
	});
         
	//$(".inpitid").live('change',function(){
       $(".inpitid").delegate("file", "change", function () { 
		var url = $(this).val();
		url=url.split("\\");
		var fileName = url[url.length-1];
		$(this).siblings("span").html(fileName);
		if(url){
			$(this).parent(".addinput").show(); 
			$("#uploadphotos").removeAttr('disabled');  
		}else{
			$(this).parent(".addinput").remove();
			$("#uploadphotos").attr('disabled','disabled'); 
		}
	});
        
	$(".delectfile").live('click',function(){
		$(this).parent(".addinput").remove();
		var fileBox =$("#quoteRequest");
                //alert(fileBox.find('p').length);
		if(fileBox.find('p').length>0){
                    $("#uploadphotos").removeAttr('disabled'); 
		}else{
                    $("#uploadphotos").attr('disabled','disabled');
                }
		 
	});
        
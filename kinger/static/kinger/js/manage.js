$(function() {
	$('.middleinput:text, textarea').addClass('xlarge');
    $('.control-group label').addClass('control-label');
    $("select.chosen").chosen()
});
//检查上传图片是否合法
function checkSubmit(){
	if(document.getElementById('id_logo')){
		f=document.getElementById('id_logo').value;
	}else{
		f=document.getElementById('id_avatar').value;
	}
	if(f!=''){
		if(!/\.(gif|jpg|jpeg|bmp|png)$/i.test(f)){
			document.getElementById('id_logo_error').style.cssText = 'display:block;margin-top:12px'
			document.getElementById('id_logo_error').innerHTML='图片类型必须是<br/>gif,jpeg,jpg,bmp,png<br/>中的一种';
			return false;
		}else{
			document.getElementById('id_logo_error').innerHTML='';
			$("#id_form").submit();
		}
	}
	$("#id_form").submit();
}
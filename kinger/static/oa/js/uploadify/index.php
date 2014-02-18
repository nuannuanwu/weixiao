<?php 
error_reporting(0);


$upload_salt = 'my_unique_salt';
$form_file_name = 'upload_file';


?>
<!DOCTYPE HTML>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>UploadiFive Test</title>
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" type="text/javascript"></script>
<script src="jquery.uploadify.min.js" type="text/javascript"></script>
<link rel="stylesheet" type="text/css" href="uploadify.css">
<style type="text/css">
body {
	font: 13px Arial, Helvetica, Sans-serif;
}
</style>
</head>

<body>
	<h1>Uploadify Demo</h1>

	<hr>

	<form method="post" action="uploadify.php" enctype="multipart/form-data">
		<input name="<?php echo $form_file_name;?>" type="file">
		<input type="hidden" name="token" value="<?php echo md5($upload_salt . $timestamp);?>">
		<input type="submit" value="手动上传">
	</form>

	<hr>

	<form>
		<div id="queue"></div>
		<input id="file_upload" name="file_upload" type="file" multiple="true">
	</form>

	<hr>

	<script type="text/javascript">
		<?php $timestamp = time();?>
		$(function() {
			$('#file_upload').uploadify({
				'overrideEvents'  : ['onSelectError', 'onDialogClose'],
				'formData'     : {
					'timestamp' : '<?php echo $timestamp;?>',
					'token'     : '<?php echo md5($upload_salt . $timestamp);?>'
				},
				'buttonText' : '自动上传',
				'fileObjName' : '<?php echo $form_file_name;?>',
				'fileSizeLimit' : '20MB',
				'swf'      : 'uploadify.swf',
				'uploader' : 'uploadify.php',
				'onSelectError' : function(file, errorCode, errorMsg) {
					if (errorCode == -110) {
						alert('too big');
					};
		        }

			});
		});
	</script>
</body>
</html>
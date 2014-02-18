<?php


// file 表单名
$form_file_name = 'upload_file';

// 上传目录
$targetFolder = '/uploads';
$targetPath = $_SERVER['DOCUMENT_ROOT'] . dirname($_SERVER['REQUEST_URI']) . $targetFolder;

// 非法上传验证
$upload_salt = 'my_unique_salt';
$verifyToken = md5($upload_salt . $_POST['timestamp']);

// 允许后缀类型
$fileTypes = array('jpg','jpeg','gif','png');

if (!empty($_FILES) && $_POST['token'] == $verifyToken) {
	$file = $_FILES[$form_file_name];
	$tempFile = $file['tmp_name'];
	$targetFile = rtrim($targetPath,'/') . '/' . $file['name'];

	$fileParts = pathinfo($file['name']);
	
	if (in_array($fileParts['extension'],$fileTypes)) {
		move_uploaded_file($tempFile, $targetFile);
		echo '1';
	} else {
		echo 'Invalid file type.';
	}
}else{
	echo "Error1";
}

?>

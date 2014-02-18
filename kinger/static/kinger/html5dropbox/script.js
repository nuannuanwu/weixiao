function pr(o){if(window.console) console.log(o)}

function objsize(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

// html5 uploader
var UploaderHTML5 = {
	init: function(settings){
		var file_hash_list = {};
		var file_list = {};
		var max_index = 0;
		var dropbox = $('#dropbox'),
                    message = $('.message', dropbox); 
		var url = $('form#post_form2').attr('action')
		var form_token = $('input[name="csrfmiddlewaretoken"]').val();
                
		dropbox.filedrop({
			// The name of the $_FILES entry:
			paramname:'img',
			maxfiles: 12,
                        maxfilesize: 5,
			url: url,
			auto: false,
			data: {form_token:form_token},	// 其它表单数据 
			drop: function(e){//拖放事件
				var files = e.dataTransfer.files;
				var len = files.length;
				var count = $('.imageHolder', dropbox).length; 
				if (count+len > this.maxfiles ) {
					alert('文件太多, 一次只能拖放 '+ this.maxfiles +' 个文件');
					return false;
				}; 
                                var max_file_size = 1048576 * this.maxfilesize; 
                                 $("#dorop_remind").show(); 
                                 
				for (var i = 0; i < len; i++) {
					max_index = max_index + 1;
					var file = files[i]; 
                                        if (file.size > max_file_size) {
                                            alert('文件太大, 只能拖放 '+ this.maxfilesize +' MB文件'); 
					}else{ 
                                            if(file.type.match(/^image\//)){ 
                                                    $.data(file, 'index', max_index);
                                                    file.index = max_index;
                                                    createImage(file)
                                            }
                                        }
				}; 
                               $("#dorop_remind").hide(); 
                               $("#html5_post_data").removeAttr("disabled"); 
                               
			},

			uploadFinished:function(i,file,response){
				$.data(file).addClass('done');
				$('.progressHolder').hide();
				$('.imageDesc').show(); 
				// response is the JSON object that post_file.php returns
			},
                afterAll: function(){ 
                    //上传完跳转  
                    window.location.href = settings.redirect_url;
            }, 	
	    error: function(err, file) {
                    //alert(err)
				switch(err) {
					case 'EmptyFile':
						showMessage('未选择文件!');
						break;
					case 'BrowserNotSupported':
						showMessage('浏览器不支持html5!');
						break;
					case 'TooManyFiles':
						alert('文件太多, 一次只能拖放 '+ this.maxfiles +' 个文件');
						break;
					case 'FileTooLarge':
						alert(file.name+' 文件太大, 最大文件大小是 ' + this.maxfilesize + ' MB');
						break;
					case 'HTTPError':
						// alert('HTTP 错误!('+file.status+')');
						//pr(file.status)
						break;
					default:
						break;
				}
				$('.progressHolder').hide();
				$('.imageDesc').show();
			},
			
			// Called before each upload is started
			beforeEach: function(file){
				if(!file.type.match(/^image\//)){
					alert('只允许上传图片类型的文件'); 
					// Returning false will cause the
					// file to be rejected
					return false;
				}
			},
			
			uploadStarted:function(i, file, len){
				$('.progressHolder').show();
				$('.imageDesc').hide();
                                $("#dorop_remind").show();
			},
			
			progressUpdated: function(i, file, progress) {
				$.data(file).find('.progress').width(progress);
			}
	    	 
		});  
                
                //var URL = window.URL || window.webkitURL; 
		function createImage(file){
			var file_index = $.data(file, 'index');
			var template = '<div class="preview">'+
								'<a class="imageRemove hide" href="javascript:void(0)">x</a>'+
								'<span class="imageHolder">'+
									'<img />'+
									'<span class="uploaded"></span>'+
								'</span>'+
								'<div class="imageDesc"><input type="text" name="" value="" placeholder="输入图片描述" data-file-index="'+file_index+'" class="desc"></div>'+
								'<div class="progressHolder" style="display:none">'+
									'<div class="progressBar"></div>'+
								'</div>'+
							'</div>';
			var preview = $(template), image = $('img', preview);  
			var reader = new FileReader(); 
			image.width = 100;
			image.height = 100; 
			reader.onload = function(e){ 
                            //pr('onload');
				// e.target.result holds the DataURL which
				// can be used as a source of the image: 
				var hash = $.md5(e.target.result+file.name); 
				if ( JSON.stringify(file_hash_list).indexOf(hash) > 0 ){
					alert('文件 '+file.name+' 已经添加过了');
                                         delete file_list[file_index];
                                         delete file_hash_list[ file_index ]; 
				}else{ 
					file_list[ file_index ] = file;
					file_hash_list[ file_index ] = hash; 
					image.attr('src',e.target.result); 
//                                        //////////////////////////////
//                                        var canvas = document.createElement("canvas");
//                                        var img = new Image();
//                                        
//                                        //img.src = URL.createObjectURL( file );
//                                        img.src = e.target.result;
//                                        canvas.width = 120;
//                                        canvas.height = 120;
//                                        var ctx = canvas.getContext("2d");
//                                        ctx.drawImage(img, 0, 0, 120, 120);
//                                        
//                                        //pr(img)
//                                        //$(canvas).appendTo(dropbox);
//                                        $('.imageHolder', preview).html( $(canvas) )
//                                        //URL.revokeObjectURL( img.src );
//                                        //img = null;
//                                        //preview.appendChild(canvas);
//                                        //////////////////////////// 
					message.hide();
					preview.appendTo(dropbox); 
					// Associating a preview container
					// with the file, using jQuery's $.data():
					$.data(file,preview);  
                                        // 将文件添加到上传队列中
                                        
                                        $(file).data('result', e.target.result);
                                        dropbox.filedrop.addFile(file_index, file);
                                        var uploader_box = document.getElementById('uploader_box'); 
                                        uploader_box.scrollTop = uploader_box.scrollHeight;
				}
			};

			// 开始读取数据
			reader.readAsDataURL(file);
		}

		// 显示提示消息
		function showMessage(msg){
			message.html(msg);
		}

		// 照片描述文字编辑
		$('input.desc', dropbox).live('change', function(e) {  
			var index = $(this).attr('data-file-index');
			var file = file_list[index];
                        var token =$('input[name=csrfmiddlewaretoken]').val();
                        var textVal =$(this).val();
                        var description = encodeURIComponent(textVal); 
			file.data = {description:description, csrfmiddlewaretoken: token,new_type:1,ty:"html5"};	// 存储文件描述
                });

		// 照片上传按钮
		$('#html5_post_data').unbind('click');
		$('#html5_post_data').bind('click', function(){ 
                   $("input.desc").change(); 
                    dropbox.filedrop.uploadFiles(file_list); 
		});

		// 删除按钮
		$('.imageRemove', dropbox).live('click', function(e) {
			var index = $('input[type="text"]:first', $(this).parent('.preview')).attr('data-file-index');		
			delete file_list[index]
			delete file_hash_list[index]
			$(this).parent('.preview').remove();
                        var len = objsize(file_list),leng = objsize(file_hash_list);
                        if(parseInt(len) == 0 || parseInt(leng) == 0 ){
                            $('#html5_post_data').attr('disabled','disabled'); 
                            message.show();
                        }
                        dropbox.filedrop.delFile(index);
		});

		// 鼠标 hover事件
		$('.preview', dropbox).live('mouseover mouseout', function(e) {
			e.stopPropagation();
            e.preventDefault();
            if (e.type == 'mouseover') {
                  $('.imageRemove', $(this)).removeClass('hide')
            }else if (e.type == 'mouseout') {
                  $('.imageRemove', $(this)).addClass('hide')
            };
		});
         //取消操作
        $('#html5_post_rest').live('click', function(e) { 
              var box = $("#dropbox .preview");  
              if(box.length>0){
                    var r = confirm("是否执行操作,当前内容将被清空?");
                    if (r==true) { 
                        $.each(file_list, function(n) {
                            delete file_list[n];
                            delete file_hash_list[n]; 
                        });
                         dropbox.filedrop.delAllFile();
                          $("#dropbox .preview").remove();
                          $("#hide_box").click(); 
                          message.show();
                    }
                }else{
                   $("#hide_box").click(); 
                } 
        });
		html5_uploader_init = true;
	} 
}; 

var UploaderFlash = {
    file_hash_list : {},
    file_list : {},
    oo: {},
    max_index : 0,
    init: function (settings) { 
        var url = settings.url;
        var form_obj = {};
        var file_queue = [];
        var file_size_limit = '5mb'; // 5 MB
        var flash_swf_url = settings.swf;
        var button = settings.buttonId;
        var container =settings.container;
        var oo; 
        var dropbox = $('#flashbox');
        var formtoken = $('input[name=csrfmiddlewaretoken]').val();
        
        var uploadify_settings = {
            runtimes : 'flash',
            file_data_name: 'img',
            browse_button : button,
            container: container,
            max_file_size : file_size_limit,
            url : url,
            max_file_count: 12, // user can add no more then 1 files at a time
            chunk_size:'1mb',
            //resize : {width : 320, height : 240, quality : 90},
            flash_swf_url :flash_swf_url , 
            multipart_params : {
            "formtoken" : formtoken,
            "file_id" : '',
            "file_path":''
            }, 
            filters : [
                {title : "Image files", extensions : "jpg,gif,png,bmp"}
            ]
    	}; 
	var uploader = new plupload.Uploader(uploadify_settings); 
        uploader.unbindAll();
	uploader.bind('Init', function(up, params) { 
		//$('#filelisttype').html("<div>Current runtime: " + params.runtime + "</div>")
	}); 
	uploader.init(); 
        //添加图片
	uploader.bind('FilesAdded', function(up, files) {  
            var file_index = UploaderFlash.max_index++;
            if(up.files.length > 12){ 
                alert("一次只能上传12张照片");  
            }
            $.each(files, function(n, file) {
                if(file.size>5*1024*1024){
                    up.removeFile(files[n]);
                }else{
                //pr(file.size+"-----------");
                if((up.files.length-files.length + n)>11){  
                    uploader.removeFile(file); 
                }else{ 
                    var file_hash = $.md5(file.name + file.size);
                    if ( JSON.stringify(UploaderFlash.file_hash_list).indexOf(file_hash) > 0 ){
                         alert('文件 '+file.name+' 已经添加过了'); 
                         up.removeFile(files[n]); 
                    }else{  
                            UploaderFlash.file_hash_list[ file_index ] = file_hash; 
                            UploaderFlash.createImageHolder(file);
                            uploader.start();//文件自动上传 
                            $("#up_static").show();  
                    } 
                } 
            }
           });
           var uploader_box = document.getElementById('uploader_box'); 
           uploader_box.scrollTop = uploader_box.scrollHeight;
	});
        //图片上传前
        uploader.bind('BeforeUpload',function(up,file){ 
           up.settings.multipart_params.file_id = file.id; 
        });
        //图片上传中
	uploader.bind('UploadProgress', function(up, file) { 
                var speed =up.total.bytesPerSec ;
                var speed2 = parseInt(up.total.bytesPerSec/1024) ;
                var rapportdownloaded = uploader.total.loaded/uploader.total.size*100 ;
                var percentdownloaded = ((Math.round(rapportdownloaded*100))/100) ;
                var bytelefttoupload = uploader.total.size-uploader.total.loaded;
                var eta = secondeenminute(Math.round(bytelefttoupload/speed));  
                //$("#onload_tp").html( speed2 +'Kb/s,' + percentdownloaded +'% '+ eta); 
                //$("#typeid_"+file.id).html( + "% ");  
                if(file.percent==100){
                    $('.progressHolder', $('div#uploaded_'+file.id)).hide();
                    $('.imageDesc', $('div#uploaded_'+file.id)).show(); 
                }
                $('.progressBar', $('div#holder_'+file.id)).css('width',file.percent+"%");
                $('.progressBar', $('div#holder_'+file.id)).html(file.percent+"%"); 
	}); 
        //上传错误
         uploader.bind('Error', function(up, err) { 
//             $('#filelist').append("<div>Error: " + err.code +
//                ", Message: " + err.message +
//                (err.file ? ", File: " + err.file.name : "") +
//                "</div>"
//            ); 
            if(err.code == -600){ 
                 alert("您选着的图片:" + err.file.name + "超过了5mb")
            } else if(err.code == -601){
                 alert("您选着的图片"+ err.file.name+"格式不对");
            } else if(err.code == -700) {
                 alert("您选着的图片"+ err.file.name+"有问题");
            } 
            up.refresh(); // Reposition Flash/Silverlight
        });
        //
	 uploader.bind('UploadComplete',function(up,file){ 
               $('#flash_post_data').removeAttr('disabled'); 
         });
         //上传成功
	uploader.bind('FileUploaded', function(up, file, response){
               var data 
               try{
                    data = response.response;
                    var datas = $.parseJSON(data); 
                }catch(err){
                    alert("上传出错!");
                    $('.error', $('div#holder_'+file.id)).show(); 
                } 
                if(datas.status == 1){
                    UploaderFlash.createImage(file,data);
                    $('input[type="text"]', $('input[type="text"]').parent('.preview')).focus();
                }else{
                    $('.error', $('div#holder_'+file.id)).show(); 
                }
                var uploader_box = document.getElementById('uploader_box'); 
                uploader_box.scrollTop = uploader_box.scrollHeight;
	})
        // 照片上传按钮
        $('#flash_post_data').unbind('click');
        $('#flash_post_data').bind('click', function(){ 
            $("#dorop_remind").show();
            $("#html5_post_data").attr("disabled","disabled");
            var src = $(this); 
            var tfrom = $('#post_form2');
            var url = tfrom.attr("action"); 
            // 检查当前按钮状态
            if (src.hasClass('disabled')) { 
                return;
            };
             var list = UploaderFlash.file_list; 
              // 批量上传 
            for (var i in list) { 
                upload_file(list[i]); 
            };
            
            var n = 0; //记录上传次数
            // 上传文件
            function upload_file(file){ 
                set_status(file, false);
                pr(file.file_path+"---------")
                $.post(url, file, function(data, textStatus, xhr) {
                    var d = $.parseJSON(data);
                    n = n + 1; //上传一次加一
                    if ( n != parseInt(objsize(list))){//判断是否上传完 
                        if (d.status == 1) { 
                           // pr('上传完成一只')
                        }else{ 
                            $('.error').show();
                        }
                        $('div#uploaded_'+file.id).hide();
                        //$("#dorop_remind").show() 
                    }else{  
                         window.location.href = settings.redirect_url;
                    }
                    set_status(file, true);
                });
            }
            
            // 更新控件状态
            function set_status(f, status){
                var t = $('div#holder_'+f.fid);
                // set disable
                if (status === false) { 
                   //$('input', tfrom).prop('disabled', true);
                    src.addClass('disabled');
                    t.addClass('uploadUploading')
                }else{ 
                   //$('input', tfrom).prop('disabled', false);
                    src.removeClass('disabled');
                    t.removeClass('uploadUploading')
                }
            } 
        });
     // 照片描述文字编辑
     $('input.desc', dropbox).die('change');
     $('input.desc', dropbox).live('change', function(e) {
         var index = $(this).attr('data-file-index');
         var file = UploaderFlash.file_list[index];
         file.description = $(this).val();   // 更新文件描述 
     });
      //取消操作
    $('#flash_post_rest').die('click');
    $('#flash_post_rest').live('click', function() {  
        var box = $('.preview',dropbox); 
            if(box.length>0){
                var r=confirm("是否执行操作,当前内容将被清空?");
                if (r==true) { 
                  $('#flash_cealr').click(); 
                  $("#hide_box").click(); 
                }  
            }else{ 
              $("#hide_box").click();  
            }  
     })
    $('#flash_cealr').click(function(e) { 
       e.stopPropagation();
       e.preventDefault();
       UploaderFlash.file_list = {};
       UploaderFlash.file_hash_list= {}; 
        uploader.files.splice(0,uploader.files.length); 
       $("#post_form_content").empty(); 
    });
    
     // 删除按钮
     $('.imageRemove', dropbox).live('click', function(e) {
         var index = $('input[type="text"]:first', $(this).parent('.preview')).attr('data-file-index');
         var did = $(this).data("id"); 
         if (index) {
             delete UploaderFlash.file_list[index]
             delete UploaderFlash.file_hash_list[index]
         } 
         $.each(uploader.files, function(i, file) {
             if(file.id == did){
                uploader.removeFile(file);
               // alert(uploader.files.length);
             }
         });
          $(this).parent('.preview').remove(); 
         var len = objsize(UploaderFlash.file_list),leng = objsize(UploaderFlash.file_hash_list); 
         if(parseInt(len) == 0 || parseInt(leng) == 0 ){
            $('#flash_post_data').attr('disabled','disabled'); 
         }
     });

     // 鼠标 hover事件
     $('.preview', dropbox).live('mouseover mouseout', function(e) {
         e.stopPropagation();
         e.preventDefault();
         if (e.type == 'mouseover') {
             $('.imageRemove', $(this)).removeClass('hide');
         }else if (e.type == 'mouseout') {
             $('.imageRemove', $(this)).addClass('hide')
         };
     });
    
     function secondeenminute(sec) {
            if ((sec/60)<1) {
                return  sec+'sec.' ;
            } else if ((sec/60)>1 && (sec/3600)<1) {
                var min = sec/60;
                sec = sec % 60;
                return  Math.floor(min)+'min. '+Math.floor(sec)+'sec.' ;
            } else {
                var hou = sec/3600;
                var rmin = sec % 3600;
                var min = rmin/60;
                sec = rmin % 60;
                return  Math.floor(hou)+'h. '+Math.floor(min)+'min. '+Math.floor(sec)+'sec.' ;
            }
        }

    flash_uploader_init = true;
},
createImageHolder: function(file){ //创建出错图
        var hid = 'holder_'+file.id;
        //pr(hid+"1111111111111111111")
        var template = '<div class="preview imageHolder" id="'+hid+'">'+
                        '<a data-id='+file.id+' class="imageRemove hide" href="javascript:void(0)">x</a>'+
        		'<span class="imageHolder" style="background:#e0e0e0">'+
            		'<span class="uploaded"></span>'+
                                '<span class="loading">正在上传</span>'+
                                '<span class="error">上传错误</span>'+
                            '</span>'+
                            '<div class="progressHolder">'+
                                '<div class="progressBar"></div>'+
                            '</div>'+
                        '</div>'; 
        var preview = $(template);
        preview.appendTo('#post_form_content'); 
       //preview.appendTo('#post_form2');
    }, 
    createImage: function(f, data){  //创建图片 
        var datas= $.parseJSON(data);
        var img_url = datas.pic;//路径
        var img_pid = datas.pid;//id
        var img_path = datas.file_path;//路径 
        var img_extension = datas.extension;//后缀名
        var file = {
            name: '',
            fid: f.id,
            description: '',
            tile_pid: img_pid,
            file_path:img_path,
            extension:img_extension,
            ty: 'flash',
            new_type: 1,
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val() 
        } 
        var file_index = UploaderFlash.max_index++; 
        UploaderFlash.file_list[ file_index ] = file; 
        // create thumb preview
        var hid = 'uploaded_'+f.id; 
        var template = '<div class="preview" id="'+hid+'">'+ 
                        '<a data-id='+f.id+' class="imageRemove hide" href="javascript:void(0)">x</a>'+
                        '<span class="imageHolder">'+
                            '<img src="'+img_url+'"/>'+
                            '<input type="hidden" name="thumb['+file_index+']" value="'+img_url+'"/>'+ 
                            '<span class="uploaded"></span>'+
                            '<span class="uploading"></span>'+
                        '</span>'+
                         '<div class="progressHolder" style="">'+
                            '<div class="progressBar"></div>'+
                        '</div>'+
                        '<div class="imageDesc" style="display:none;"><input type="text" name="description['+file_index+']" value="" placeholder="输入图片描述" data-file-index="'+file_index+'" class="desc"></div>'+
                     '</div>';
              
            var preview = $(template);
            $('div#holder_'+f.id).remove();
            preview.appendTo('#post_form_content'); 
            //preview.appendTo('#post_form2');
            $('div#holder_'+f.id).removeClass('imageHolder').html(preview.html());
        }
    
}

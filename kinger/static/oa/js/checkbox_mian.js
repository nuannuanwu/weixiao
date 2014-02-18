// JavaScript Document

function pr(o){if(window.console){console.log(o)}};

//var $ = $;
jQ19(function() {
       //$ = jQ19;
	Do.initEvents();	// checkbox 事件初始化.
    //alert('sdjfhksjdfhjkh');
});

// 多级用户选择面板
// 
// 对应的 html 结构形如:
// <!-- box1  -->
// <div data-type="box">
//
// 	<div>
// 		 <label>
// 	        <input name="" data-type="top" type="checkbox" data-id="2" data-pid="">
// 	        中班
// 	    </label>
// 	</div>
//
// 	<div>
// 	<!-- box2  -->
// 		<div data-type="box">
// 			<div>  
// 				<label>
// 	                <input name="" data-type="" type="checkbox" data-id="201" data-pid="2">
// 	                中1班
// 	            </label> 
// 			</div>
// 			<ul>
// 				<li>
// 	                <label>
// 	                    <input type="checkbox" data-type="user" data-name="abc" data-id="20101" data-pid="201">
// 	                    名字abc
// 	                </label>
// 	            </li>
//				...		
// 	        </ul>
// 	    </div>
// 	    <!-- /box2  -->
// 	</div>
//
// </div>
// <!-- /box1  -->
var sel_identify = ''

var Do = { 
        inputBox : '',                  // 操作这个对象里的input
        serverUserBox:'',
	currentSchoolID : '',		// 当前选择的学校 id
	checkedUserIDs: [],		// (当前学校)已选对象id列表	
	checkedUser: {},	// 保存的已选 user list. 结构形如: {school_id:[uid, uid, ...], }
	// 初始化, 事件绑定
	initEvents: function(){
	        Do.inputBox = "#content "; // 
                Do.serverUserBox =$("#data_panel ul");
		Do.currentSchoolID = $('select[name="school_id"]').val();
		Do.checkedUserIDs = [];	// 
		Do.checkedUser[Do.currentSchoolID] = [];
		Do.initCheckboxStatus(); 
		// 切换学校
//		$('select[name="school_id"]').on('change', function(e){
//			Do.currentSchoolID = $(e.target).val();
//                         alert('111111111111111111');
//		})
                // 切换学校事件
                $('select[name="school_id"]').on('click', function(e){
			Do.currentSchoolID = $(e.target).val(); 
                          
		})
                
		// 所有 checkbox 事件
		$(document).on('change',Do.inputBox + 'input[type="checkbox"]', function(e){
			var tar = $(e.target);
                        Do.updateCheckedUserClose(tar);
                        //alert(Do.checkedUserIDs.length +"---------222222222");
                        //alert(Do.checkedUser.length+"----------11111111111111")
                        //alert('111111111111111111');
		});
//		$('.user-box input[type="checkbox"]').live('click',function(e){
//			var tar       = $(e.target);
//			Do.updateCheckedUserClose(tar);
//                        //alert('111111111111111111');
//		}); 

	      $(document).on('click', '.rm_user', function(e){
			var tar = $(e.target)
			var data_id = parseInt(tar.attr('data-id'))
			Do.removeUser(data_id)
			tar.parent('li').remove();
		});
                $(document).on('click', '.rem-btn', function(e){ //清除已选功能
                    Do.clearCheckUserlist(); 
                    Do.serverUserBox.empty();
                });
                $(document).on('change', '.teacher_all', function(e){ //全选功能
                    //Do.clearCheckUserlist(); 
                      //Do.serverUserBox.empty();
                      var checked = $(this).prop("checked");
                      var tar       = $(e.target); 
                      Do.checkAllUserlist(checked); 
		      Do.updateCheckedUserClose(tar);
                });
                $(document).on('click', '.st-group li a', function(e){   //老师、学生tab  
                    var rletype= $(this).attr('rel'); 
                    if(rletype==1){
                                 $(".list_1").show();
                                 $(".list_2").hide();
                                 $('.datas').hide(); 
                         }else{
                                 $(".list_1").hide();
                                 $(".list_2").show();
                                 $('.datas').show(); 
                         }
                         $(this).parent().addClass('on');
                         $(this).addClass('ona');
                         $(this).parent().siblings().removeClass('on');
                         $(this).parent().siblings().find("a").removeClass('ona');
                        // Do.updateIdentify(rletype);
                }); 
                
	}, 

	initCheckboxStatus: function(){ 
		//pr('initCheckboxStatus')
		var list = Do.checkedUserIDs
		//pr(list)
		$.each(list, function(i, data_id){ 
			//pr('data_id')
			var tar = $('input[data-id='+data_id+']').prop('checked', true)
			Do.updateCheckboxStatus( tar );
		})
	},
	updateCheckedUserClose: function(tar){
		var data_type = tar.attr('data-type')
		var data_id   = tar.attr('data-id')
		var data_pid  = tar.attr('data-pid');
		if(data_type == 'top'){	// top level
			$('input[type="checkbox"]'+sel_identify, tar.parents('[data-type="box"]')).prop('checked', tar.prop('checked'))
		}else{						// others: data_type == 'user' || data_type == 'class'
			$('input[data-pid='+data_id+']'+sel_identify).prop('checked', tar.prop('checked'));	// 更新子级
		} 
                Do.updateCheckedUserList(tar)
		Do.updateCheckboxStatus(tar) 

	},

	// 更新 "已选 user id" 列表 / 遍历更新相关 checkbox 状态
	// @tar input[type=checkbox] 对象
	updateCheckedUserList: function(tar){

		// 1. 更新同 id checkbox
		var related_data_id_list = []
		var related_data_id_list = Do.getSublevelUserID(tar)
		var checked = tar.prop('checked')

		// 2. 读取已勾选项目
		var sel = ( checked ? ':checked' : ':not(:checked)' )
		var inbox_users     = $('input[type="checkbox"][data-type="user"]'+sel_identify+sel, tar.parents('[data-type="box"]'))
		// var inbox_user_checked	    		  = $('input[type="checkbox"][data-type="user"]:checked', tar.parents('[data-type="box"]'))
		Do.checkedUser[Do.currentSchoolID] = []
		Do.checkedUserIDs = [] 
		$.each(inbox_users, function(i, v){
			var sub_data_id = parseInt(v.getAttribute("data-id"))
			var index = $.inArray(sub_data_id, Do.checkedUserIDs) 
			if ( index < 0 ) {		// 滤重
				// // 1. 记录所有已选的 user id
				// if (checked) {
				// 	Do.checkedUser[Do.currentSchoolID].push(sub_data_id)
				// } 
				// 2. 更新 user id 相关 checkbox
				var tar_list = $('input[data-id='+sub_data_id+']');
				$.each(tar_list, function(i2, tar_input){
					var related_tar = $(tar_input)
					var related_tar_data_id = parseInt(related_tar.attr('data-id'))
					if (checked) { // 添加 checkbox (添加所有已选的)
						//related_tar.prop('checked', checked);
					}else{ // 移除 checkbox (只移除所点击的 checkbox 相关的 checkbox)
						if ( $.inArray(related_tar_data_id, related_data_id_list) >= 0 ) {
							related_tar.prop('checked', checked);
						}
					}
                                        //暂时不调用更新状态
					Do.updateCheckboxStatus(related_tar) //
				})
			}
		})
                  
		// 待优化
		var inbox_user_checked	    = $('input[type="checkbox"][data-type="user"]'+sel_identify+':checked')
		$.each(inbox_user_checked, function(i, tar){
                    //pr(tar)
			var sub_data_id = parseInt(tar.getAttribute("data-id"))
			var index = $.inArray(sub_data_id, Do.checkedUserIDs)
			// 1. 记录所有已选的 user id
			if (index < 0) {
				Do.checkedUserIDs.push(sub_data_id)
				Do.checkedUser[Do.currentSchoolID].push(tar)
			}
		}) 
		// 3. 生成 li
		Do.updateDatapanel() 
	},

	// 更新 tar 父级子级的 checkbox 状态
	// @tar input[type=checkbox] 对象
	updateCheckboxStatus: function(tar){
		var data_id = tar.attr('data-id');
		var data_pid = tar.attr('data-pid');
		var data_type = tar.attr('data-type');
		var parent = $('input[data-id='+data_pid+'][data-type!="user"]'+sel_identify)
		// 1. 更新子级 (无)
		// 2. 更新父级
		var num_total = $('input[type="checkbox"][data-type="'+data_type+'"][data-pid="'+data_pid+'"]'+sel_identify, tar.parents('[data-type="box"]')).length
		var num_checked = $('input[type="checkbox"][data-type="'+data_type+'"][data-pid="'+data_pid+'"]'+sel_identify+':checked', tar.parents('[data-type="box"]')).length
		if (num_total != 0) {
			if (num_checked < num_total) {
				parent.prop('checked', false);
			}else{
				parent.prop('checked', true);
			}
			Do.updateCheckboxStatus(parent);
		}
	},

	// 获取元素下所有子级的 user id
	// @tar input[type=checkbox] 对象
	// @return []
	getSublevelUserID: function(tar){
		var sublevel_id_list = [] 
		var checked = tar.prop('checked')
		var sel = ( checked ? ':checked' : ':not(:checked)' )
		var sublevel_ids = $('input[type="checkbox"][data-type="user"]'+sel_identify+sel, tar.parents('[data-type="box"]')[0])	// parents() 返回若干数组. 只取最邻近的一级

		$.each(sublevel_ids, function(i, v){
			var sub_data_id = parseInt(v.getAttribute("data-id"))
			var index = $.inArray(sub_data_id, sublevel_id_list)
			if ( index < 0 ) {		// 滤重
				sublevel_id_list.push(sub_data_id)
			}
		})
		return sublevel_id_list
	},
                
        updateIdentify: function (identify){
            if (identify){
               sel_identify = '[data-identify = "'+identify+'"]'
            }else{
               sel_identify = ''
            }
        },

	updateDatapanel: function(){ //更新已选框成员
		var list = Do.checkedUser[Do.currentSchoolID]; 
                //pr(list)
		var li = ''
		for (var i = list.length - 1; i >= 0; i--) {
			var u = $(list[i]);
			li += '<li><input schoolid="'+ u.attr("schoolid") +'" data-id = "'+u.attr("data-id")+'"  data-pid = "'+u.attr("data-pid")+'" type ="checkbox" name = "to" value =' + u.attr("data-id") + ' checked="checked" style="display:none;" />' + u.attr('data-name') + '<span class = "rm_user" data-id = "'+u.attr("data-id")+ '">&nbsp</span></li>';
		}; 
		Do.serverUserBox.html(li);
	}, 
	removeUser: function(data_id ){ 
		var index = Do.checkedUserIDs.indexOf(data_id)
		if (index >= 0) {
			Do.checkedUserIDs.splice(index, 1)
			Do.checkedUser[Do.currentSchoolID].splice(index, 1)
			var tar_list = $(Do.inputBox + 'input[data-id='+data_id+']'+sel_identify)
			$.each(tar_list, function(i, v){ 
				var tar = $(v).prop('checked', false)
				Do.updateCheckboxStatus( tar )
			})
		};
	},
         checkAllUserlist: function(checked){ 
             //alert(checked)
             var userid_list = [];
             var sel = ( checked ? ':not(checked)' : ':checked' );
             var tar_list = $(Do.inputBox + "input[type=checkbox]" +sel_identify+sel);
             $.each(tar_list, function(i, v){
                var sub_data_id = parseInt(v.getAttribute("data-id"))
                var index = $.inArray(sub_data_id, userid_list)
                if ( index < 0 ) {		// 滤重
                       userid_list.push(sub_data_id)
                }  
             });
            Do.checkedUserIDs = userid_list; 
            //Do.updateCheckboxStatus( ); 
            $.each(tar_list, function(i, v){ 
                var tar = $(v).prop('checked', checked); 
            });   
        },        
         clearCheckUserlist: function(){
            Do.checkedUserIDs = [];
            Do.currentSchoolID = '';
            //Do.updateCheckboxStatus( );
            var tar_list = $(Do.inputBox + 'input[type="checkbox"]'+sel_identify+':checked')
            $.each(tar_list, function(i, v){ 
                var tar = $(v).prop('checked', false);
                Do.updateCheckboxStatus( tar ); 
            });
        } 
}



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







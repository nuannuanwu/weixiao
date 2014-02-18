# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url


urlpatterns = patterns("oa.views.agency",
    url(r'^$', "index", name='oa_home'),
    url(r'^agency/create/$', "create", name='oa_agency_create'),
    url(r'^agency/create_user/$', "create_agency_user", name='oa_agency_create_agency_user'),
    url(r'^unread_list/$', "unread_list", name="oa_unread_list"),
)

urlpatterns += patterns("oa.views.department",
    url(r'^department/index/$', "index", name='oa_department_list'),
    url(r'^department/create/$', "create", name='oa_department_create'),
    url(r'^department/update/(?P<department_id>\d+)/$', "update", name='oa_department_update'),
    url(r'^department/delete/(?P<department_id>\d+)/$', "delete", name='oa_department_delete'),
)

urlpatterns += patterns("oa.views.position",
    url(r'^position/index/$', "index", name='oa_position_list'),
    url(r'^position/create/$', "create", name='oa_position_create'),
    url(r'^position/update/(?P<position_id>\d+)/$', "update", name='oa_position_update'),
    url(r'^position/delete/(?P<position_id>\d+)/$', "delete", name='oa_position_delete'),
)

urlpatterns += patterns("oa.views.school",
    url(r'^school/index/$', "index", name='oa_school_list'),
    url(r'^school/create/$', "create", name='oa_school_create'),
    url(r'^school/update/(?P<school_id>\d+)/$', "update", name='oa_school_update'),
    url(r'^school/delete/(?P<school_id>\d+)/$', "delete", name='oa_school_delete'),
    url(r'^school/export_member/(?P<school_id>\d+)/$', "export_member", name='oa_school_export_teacher'),
)

urlpatterns += patterns("oa.views.group",
    url(r'^class/index/$', "index", name='oa_class_list'),
    url(r'^class/create/$', "create", name='oa_class_create'),
    url(r'^class/update/(?P<group_id>\d+)/$', "update", name='oa_class_update'),
    url(r'^class/delete/(?P<group_id>\d+)/$', "delete", name='oa_class_delete'),
    url(r'^class/check_teachers/$', "check_teachers", name='oa_class_check_teachers'),
    url(r'^class/get_school_teacher/$', "get_school_teacher", name='oa_class_get_school_teacher'),
    url(r'^class/batch_import/$', "batch_import", name='oa_class_batch_import'),
    url(r'^class/template/$', "template", name='oa_class_template'),
    url(r'^class/import_view/$', "import_view", name='oa_class_import'),
    url(r'^class/check_import/$', "check_import", name='oa_class_check_import'),
)

urlpatterns += patterns("oa.views.teacher",
    url(r'^teacher/index/$', "index", name='oa_teacher_list'),
    url(r'^teacher/create/$', "create", name='oa_teacher_create'),
    url(r'^teacher/update/(?P<teacher_id>\d+)/$', "update", name='oa_teacher_update'),
    url(r'^teacher/school_agency/$', "get_school_agency", name='oa_get_school_agency'),
    url(r'^teacher/pre_username/$', "get_pre_username", name='oa_get_pre_username'),
    url(r'^teacher/send_account/$', "send_account", name='oa_teacher_send_account'),
    url(r'^teacher/template/$', "template", name='oa_teacher_template'),
    url(r'^teacher/batch_import/$', "batch_import", name='oa_teacher_batch_import'),
    url(r'^teacher/import_view/$', "import_view", name='oa_teacher_import'),
    url(r'^teacher/check_import/$', "check_import", name='oa_teacher_check_import'),
    url(r'^teacher/user_role/$', "user_role", name='oa_teacher_user_role'),
    url(r'^teacher/change_status/$', "change_status", name='oa_teacher_status'),
)

urlpatterns += patterns("oa.views.student",
    url(r'^student/index/$', "index", name='oa_student_list'),
    url(r'^student/create/$', "create", name='oa_student_create'),
    url(r'^student/update/(?P<student_id>\d+)/$', "update", name='oa_student_update'),
    url(r'^student/school_class/$', "get_school_class", name='oa_get_school_class'),
    url(r'^student/send_account/$', "send_account", name='oa_student_send_account'),
    url(r'^student/send_groupaccount/(?P<group_id>\d+)/$', "group_send_account", name='oa_student_send_group_account'),
    url(r'^student/template/$', "template", name='oa_student_template'),
    url(r'^student/batch_import/$', "batch_import", name='oa_student_batch_import'),
    url(r'^student/import_view/$', "import_view", name='oa_student_import'),
    url(r'^student/check_import/$', "check_import", name='oa_student_check_import'),
    url(r'^student/get_extra_form/$', "get_extra_form", name='oa_guardian_get_extra_form'),
)

urlpatterns += patterns("oa.views.permission",
    url(r'^permission/index/$', "index", name='oa_permission_role_list'),
    url(r'^permission/create_role/$', "create_role", name='oa_permission_create_role'),
    url(r'^permission/update/(?P<role_id>\d+)/$', "update_role", name='oa_permission_update_role'),
    url(r'^permission/delete_role/$', "delete_role", name='oa_permission_delete_role'),
    url(r'^permission/role_accesses/$', "get_role_accesses", name='oa_permission_role_accesses'),
    url(r'^permission/designate_role/$', "designate_role", name='oa_permission_designate_role'),
    url(r'^permission/role_detail/$', "role_detail", name='oa_permission_role_detail'),
    url(r'^permission/user_role/$', "user_role", name='oa_permission_user_role'),
    url(r'^permission/add_role/(?P<user_id>\d+)/$', "add_role", name='oa_permission_add_role'),
    url(r'^permission/authorize/$', "set_authorize", name='oa_permission_set_authorize'),
    url(r'^teacher/change_authorize/$', "change_authorize", name='oa_permission_change_authorize'),
)

urlpatterns += patterns("oa.views.workgroup",
    url(r'^workgroup/index/$', "index", name='oa_workgroup_list'),
    url(r'^workgroup/personal/$', "personal", name='oa_workgroup_personal'),
    url(r'^workgroup/create/$', "create", name='oa_workgroup_create'),
    url(r'^workgroup/personal/create/$', "personal_create", name='oa_workgroup_personal_create'),
    url(r'^workgroup/update/(?P<workgroup_id>\d+)/$', "update", name='oa_workgroup_update'),
    url(r'^workgroup/personal/update/(?P<workgroup_id>\d+)/$', "personal_update", name='oa_workgroup_personal_update'),
    url(r'^workgroup/delete/$', "delete", name='oa_workgroup_delete'),
    url(r'^workgroup/personal/delete/$', "personal_delete", name='oa_workgroup_personal_delete'),
    url(r'^workgroup/set/$', "set_workgroup", name='oa_workgroup_set'),
    url(r'^communicate/$', "communicate", name='oa_communicate'),
)

urlpatterns += patterns("oa.views.cookbook",
    url(r'^cookbook/$', "index", name='oa_cookbook'),
    url(r'^cookbook/get_cookbook_date/$', "get_cookbook_date", name="oa_cookbook_get_cookbook_date"),
    url(r'^cookbook/save_cookbook/$', "save_cookbook", name="oa_cookbook_save_cookbook"),
    url(r'^cookbook/save_cookbook_set/$', "save_cookbook_set", name="oa_cookbook_save_cookbook_set"),
)

urlpatterns += patterns("oa.views.account",
    url(r'^account_setting/$', "account_setting", name='oa_account_setting'),
    url(r'^logout/$', "oa_logout", name='oa_logout'),
    url(r'^account_password_change/(?P<user_id>\d+)/$', "password_change", name='oa_account_password_change'),
    url(r'^account_password_reset/(?P<user_id>\d+)/$', "password_set", name='oa_account_password_set'),
#    url(r'^account/check_username/$', "get_user_by_username", name='oa_check_pre_username'),
#    url(r'^cross_domain/$', "cross_domain", name='oa_cross_domain'),
)

urlpatterns += patterns("oa.views.message",
    url(r'^message/index/$', "message_list", name='oa_message_list'),
    url(r'^message/delete/$', "delete_message", name='oa_delete_message'),
    url(r'^message/contact/remove/$', "contact_remove", name='oa_contact_remove'),
    url(r'^message/send/$', "send_message", name='oa_send_message'),
    url(r'^message/record/$', "message_record", name='oa_message_record'),
    url(r'^message/record/(?P<message_id>\d+)$', "record_view", name='oa_message_record_view'),
    url(r'^message/cancel_timing/(?P<message_id>\d+)$', "cancel_timing", name='oa_message_cancel_timing'),
    url(r'^message/history/(?P<user_id>\d+)/$', "user_message_history", name='oa_message_history'),
    url(r'^message/receiver/$', "set_receiver", name='oa_message_set_receiver'),
    url(r'^message/mailbox/(?P<site_id>\d+)/$', "mailbox", name='oa_mailbox'),
    url(r'^website/manage/(?P<site_id>\d+)/$', "mailbox_index", name='oa_website_manage'),
    url(r'^message/delete_mailbox/(?P<site_id>\d+)/$', "delete_mailbox", name='oa_mailbox_delete'),
    url(r'^message/mailbox_detail/(?P<mailbox_id>\d+)/$', "mailbox_detail", name='oa_mailbox_detail'),
    url(r'^message/mailbox_set/(?P<mailbox_id>\d+)/$', "mailbox_set", name='oa_mailbox_set'),
)

urlpatterns += patterns("oa.views.website",
    url(r'^website/$', "index", name='oa_website_list'),
    url(r'^website/create/$', "create", name='oa_website_create'),
    url(r'^website/admins/(?P<site_id>\d+)/$', "site_admin", name='oa_website_admins'),
    url(r'^part/grove/create/(?P<site_id>\d+)/$', "create_part", name='oa_part_nav_grove'),
    url(r'^part/feature/create/(?P<site_id>\d+)/$', "create_part", name='oa_part_nav_feature'),
    url(r'^part/recruit/create/(?P<site_id>\d+)/$', "create_part", name='oa_part_nav_recruit'),
    url(r'^part/teache/(?P<site_id>\d+)/$', "part_teache", name='oa_part_teache'),
    url(r'^part/teache/create/(?P<site_id>\d+)/$', "create_part", name='oa_part_nav_teache'),
    url(r'^website/teache/delete/$', "delete_part_teaches", name='oa_website_teache_delete'),
    url(r'^website/update/(?P<site_id>\d+)/$', "update_website", name='oa_website_update'),
    url(r'^website/edit/(?P<site_id>\d+)/$', "edit_website", name='oa_website_edit'),
    url(r'^template/(?P<site_id>\d+)/$', "template", name='oa_template_list'),
    url(r'^change_template/(?P<template_id>\d+)/$', "change_template", name='oa_change_template'),
    
    url(r'^part/grove/update/(?P<part_id>\d+)/$', "update_part", name='oa_part_nav_grove_update'),
    url(r'^part/feature/update/(?P<part_id>\d+)/$', "update_part", name='oa_part_nav_feature_update'),
    url(r'^part/recruit/update/(?P<part_id>\d+)/$', "update_part", name='oa_part_nav_recruit_update'),
    url(r'^part/teache/update/(?P<part_id>\d+)/$', "update_part", name='oa_part_nav_teache_update'),
    
    url(r'^part/announcement/list/(?P<site_id>\d+)/$', "announcement_list", \
        name='oa_part_con_anc_list'),
    url(r'^part/announcement/create/(?P<site_id>\d+)/$', "announcement_create", \
        name='oa_part_con_anc_create'),
    url(r'^part/announcement/delete/$', "operate_part_announcements", name='oa_part_con_anc_operate'),                   
    url(r'^part/announcement/update/(?P<part_id>\d+)/$', "update_announcement",\
        name='oa_part_con_anc_update'), 
                        
    url(r'^part/news/list/(?P<site_id>\d+)/$', "news_list", \
        name='oa_part_con_news_list'),
    url(r'^part/news/create/(?P<site_id>\d+)/$', "news_create", \
        name='oa_part_con_news_create'),
    url(r'^part/news/delete/$', "delete_part_news", name='oa_part_con_news_delete'),                   
    url(r'^part/news/update/(?P<part_id>\d+)/$', "update_news",\
        name='oa_part_con_news_update'),    
                        
    url(r'^part/tips/create/(?P<site_id>\d+)/$', "tips_create", \
        name='oa_part_con_tips_create'),
                        
    url(r'^part/video/list/(?P<site_id>\d+)/$', "video_list", \
        name='oa_part_con_video_list'),
    url(r'^part/video/create/(?P<site_id>\d+)/$', "video_create", \
        name='oa_part_con_video_create'),
    url(r'^part/video/delete/$', "delete_part_video", name='oa_part_con_video_delete'),                   
    url(r'^part/video/update/(?P<part_id>\d+)/$', "update_video",\
        name='oa_part_con_video_update'), 
    url(r'^figure/teacher/(?P<site_id>\d+)/$', "star_figure_teacher", \
        name='oa_star_figure_teacher'),
    url(r'^figure/student/(?P<site_id>\d+)/$', "star_figure_student", \
        name='oa_star_figure_student'),
    url(r'^figure/status/teacher/$', "star_teacher_status",  name='oa_star_teacher_status'),
    url(r'^figure/status/student/$', "star_student_status",  name='oa_star_student_status'),
    url(r'^figure/update/(?P<site_id>\d+)/(?P<user_id>\d+)/$', "star_figure_detail", \
        name='oa_star_figure_detail'),   
    url(r'^check_website_domain/$', "check_website_domain", name='oa_check_website_domain'),       
)

urlpatterns += patterns("oa.views.album",
    url(r'^album/school/(?P<site_id>\d+)/$', "school_albums",name='oa_album_school_list'),
    url(r'^album/create/(?P<site_id>\d+)/$', "album_create",name='oa_album_create'),
    url(r'^album/update/(?P<album_id>\d+)/$', "album_update",name='oa_album_update'),
    url(r'^album/detail/(?P<album_id>\d+)/$', "album_detail",name='oa_album_detail'),
    url(r'^album/upload_photo/(?P<album_id>\d+)/$', "upload_photo",name='oa_album_upload_photo'),
    url(r'^album/update_photo/(?P<photo_id>\d+)/$', "update_photo",name='oa_album_update_photo'),
    url(r'^album/delete/(?P<site_id>\d+)/$', "delete_album",name='oa_album_delete'),
    url(r'^album/show_photo/(?P<album_id>\d+)/$', "show_photo",name='oa_album_show_photo'),
    url(r'^album/photo_detail/$', "photo_detail",name='oa_album_photo_detail'),
)

urlpatterns += patterns("oa.views.article",
    url(r'^site/article/(?P<site_id>\d+)/$', "index",name='oa_article_list'),
    url(r'^site/article_create/(?P<site_id>\d+)/$', "article_create",name='oa_article_create'),
    url(r'^site/article_update/(?P<article_id>\d+)/$', "article_update",name='oa_article_update'),
)

urlpatterns += patterns("oa.views.link",
    url(r'^site/link/(?P<site_id>\d+)/$', "index",name='oa_link_list'),
    url(r'^site/link/create/(?P<site_id>\d+)/$', "create",name='oa_link_create'),
    url(r'^site/link/delete/(?P<site_id>\d+)/$', "delete",name='oa_link_delete'),
)

urlpatterns += patterns("oa.views.document",
    url(r'^document/category/$', "category",name='oa_document_category'),
    url(r'^document/category/delete/(?P<cat_id>\d+)/$', "delete_category",name='oa_document_delete_category'),
    url(r'^document/get_extra_form/$', "get_extra_form",name='oa_document_get_extra_form'),
    url(r'^document/write/$', "write_document",name='oa_write_document'),
    url(r'^document/my/$', "my_document",name='oa_my_document'),
    url(r'^document/detail/(?P<doc_id>\d+)/$', "document_detail",name='oa_document_detail'),
    url(r'^document/download/(?P<file_id>\d+)/$', "download_document",name='oa_download_document'),
    url(r'^document/delete_file/$', "delete_document_file",name='oa_delete_document_file'),
    url(r'^document/download_zip/(?P<doc_id>\d+)/$', "download_zipfile",name='oa_download_zip_document'),
    url(r'^document/need_approval/$', "need_approval",name='oa_need_approval'),
    url(r'^document/approval_document/(?P<doca_id>\d+)/$', "approval_document",name='oa_approval_document'),
    url(r'^document/approvaled/$', "having_approvaled",name='oa_approvaled_document'),
    url(r'^document/issued_document/$', "issued_document",name='oa_issued_document'),
    url(r'^document/cancel_document/(?P<doc_id>\d+)/$', "cancel_document",name='oa_cancel_document'),
    url(r'^document/reback_document/$', "reback_document",name='oa_reback_document'),
    url(r'^document/invalid_document/$', "invalid_document",name='oa_invalid_document'),
    url(r'^document/personal_document/$', "personal_document",name='oa_personal_document'),
    url(r'^document/delete/(?P<doc_id>\d+)/$', "delete_document",name='oa_delete_document'),
    url(r'^document/update/(?P<doc_id>\d+)/$', "update_document",name='oa_update_document'),
    url(r'^document/reback/edit/(?P<doca_id>\d+)/$', "edit_reback_document",name='oa_edit_reback_document'),
    url(r'^document/invalid/document/(?P<doc_id>\d+)/$', "invalid_user_document",name='oa_invalid_user_document'),
    url(r'^document/resave/document/(?P<doc_id>\d+)/$', "resave_document",name='oa_resave_document'),
    url(r'^document/receiver/$', "set_receiver", name='oa_document_set_receiver'),
    url(r'^document/approvalers/$', "get_approvalers", name='oa_document_get_approvalers'),
    
)

urlpatterns += patterns("oa.views.apply",
    url(r'^regist/apply/$', "index", name='oa_regist_apply_list'),
    url(r'^regist/detail/(?P<regist_id>\d+)/$', "regist_detail",name='oa_regist_apply_detail'),
)

urlpatterns += patterns("oa.views.schedule",
#    url('^schedule/student/$', "student_index", name="oa_schedule_student"),
    url('^schedule/$', "teacher_index", name="oa_schedule_teacher"),
    url('^schedule/create/$', "create", name="oa_create_schedule"),
    url('^schedule/delete/(?P<schedule_id>\d+)/$', "delete", name="oa_delete_schedule"),
    url('^schedule/download/(?P<schedule_id>\d+)/$', "download", name="oa_download_schedule"),
)

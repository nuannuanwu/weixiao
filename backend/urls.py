# -*- coding: utf-8 -*-
from django.conf.urls import patterns,  url
#from backend.views.task import *

urlpatterns = patterns('',

)

urlpatterns += patterns("backend.views.cron",
    url(r'^cron/push_tile/$', "push_tile", name='cron_push_tile'),
    url(r'^cron/push_unread_message/$', "push_unread_message", name='cron_push_unread_message'),
    url(r'^cron/push_unread_tile/$', "push_unread_tile", name='cron_push_unread_tile'),
    url(r'^cron/sms2send/$', "sms2send", name='cron_sms2send'),
    url(r'^cron/sms2gate/$', "sms2gate", name='cron_sms2gate'),
    url(r'^cron/send_unread_message/$', "send_unread_message", name='cron_send_unread_message'),
    url(r'^cron/send_emergency_message/$', "send_emergency_message", name='cron_send_emergency_message'),
    url(r'^cron/send_unread_cookbook/$', "send_unread_cookbook", name='cron_send_unread_cookbook'),
    url(r'^cron/send_user_message/$', "send_user_message", name='cron_send_user_message'),
    url(r'^cron/send_staff_unread/$', "send_staff_unread", name='cron_send_staff_unread'),
    url(r'^cron/mytest/$', "mytest", name='cron_mytest'),
)

urlpatterns += patterns("backend.views.taskqueue",
    url(r'^taskqueue/apns/$', "apns", name='cron_push_tile'),
    url(r'^taskqueue/sms2send/$', "sms2send", name='cron_sms2send'),
    url(r'^taskqueue/sms2gate/$', "sms2gate", name='cron_push_sms_send'),
    url(r'^taskqueue/notice2staff/$', "notice2staff", name='cron_push_notice_staff'),
    url(r'^taskqueue/make_tile_img/$', "make_tile_img", name='cron_make_tile_img'),
    url(r'^taskqueue/large_img/$', "large_img", name='cron_make_large_img'),
    url(r'^taskqueue/httptest/$', "httptest", name='cron_httptest'),
)

urlpatterns += patterns('backend.views.task',
    url(r'^task/parent_info/$', 'parent_info', name='cron_parent_info'),
    url(r'^task/parent_access_info/(?P<uid>\d+)/$', 'parent_access_info', name='cron_parent_access_info'),
    url(r'^task/tile_microsecond_init/$', 'tile_microsecond_init', name='cron_tile_microsecond_init'),
    url(r'^task/active_data_migration/$', 'active_data_migration', name='cron_active_data_migration'),
    url(r'^task/video_object_to_code/$', 'video_object_to_code', name='cron_video_object_to_code'),
    url(r'^task/img_sae_to_oss/$', 'img_sae_to_oss', name='cron_img_sae_to_oss'),
    url(r'^task/img_sae_to_sae/$', 'img_sae_to_sae', name='cron_img_sae_to_sae'),
    url(r'^task/inner_role_for_school/$', 'inner_role_for_school', name='cron_inner_role_for_school'),
    url(r'^task/default_access_for_teacher/$', 'default_access_for_teacher', name='cron_default_access_for_teacher'),
    url(r'^task/tile_visit_trans/$', 'tile_visit_trans', name='cron_tile_visit_trans'),
)

try:
	import backend.views.callback
	urlpatterns += patterns("backend.views.callback",
	    url(r'^callback/sms/$', "sms_soap_callback", name='sms_soap_callback'),
	    url(r'^callback/sms/?wsdl/$', "sms_soap_callback", name='sms_soap_callback'),
	)
except:
	pass
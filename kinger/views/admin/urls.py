# -*- coding: utf-8 -*-
from django.conf.urls import patterns,  url


urlpatterns = patterns('',

)

urlpatterns += patterns("kinger.views.admin.extend",
    url(r'^kinger/sms/not_logged_in/$', "not_logged_in_sms", name="admin_not_logged_in_sms"),
    url(r'^kinger/cookbook/(?P<cid>\d+)/status/$', "cookbook_info", name="admin_cookbook_info"),
    url(r'^kinger/tile/tile_change/$', "tile_change_form", name="admin_tile_change_form"),
    url(r'^send_staff_unread/$', "send_staff_unread", name="admin_send_staff_unread"),
    url(r'^kinger/tile/rev_tile_change/$', "rev_tile_change", name="rev_admin_tile_change_form"),
    url(r'^kinger/school_tiles_info/$', "school_tiles_info", name="admin_school_tiles_info"),
    url(r'^kinger/school_all_class/$', "special_group_for_school", name="admin_school_all_class"),
    url(r'^kinger/get_group_messages/$', "get_group_messages", name="admin_get_group_messages"),
    url(r'^kinger/get_tile_image/$', "get_tile_image", name="admin_get_tile_image"),
    url(r'^kinger/get_user_messages/$', "get_user_messages", name="admin_get_user_messages"),
    url(r'^kinger/groupimg/(?P<gid>\d+)/download/$', "download_zipfile", name="admin_groupimg_download"),
)


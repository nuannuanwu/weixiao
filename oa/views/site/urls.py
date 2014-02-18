# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url


urlpatterns = patterns("oa.views.site.frontend",
    url(r'^$', "index", name='oa_site_index'),
    url(r'^introduction/$', "introduction", name='oa_site_introduction'),
    url(r'^teache/$', "teache", name='oa_site_teache'),
    url(r'^announce/$', "announce", name='oa_site_announce'),
    url(r'^news/$', "news", name='oa_site_news'),
    url(r'^articals/$', "articals", name='oa_site_articals'),
    url(r'^part_detail/(?P<part_id>\d+)/$', "part_detail", name='oa_site_part_detail'),
    url(r'^feature/$', "feature", name='oa_site_feature'),
    url(r'^recruit/$', "recruit", name='oa_site_recruit'),
    url(r'^videos/$', "videos", name='oa_site_videos'), 
    url(r'^video_detail/(?P<video_id>\d+)/$', "video_detail", name='oa_site_video_detail'),
    url(r'^mailbox/$', "mailbox", name='oa_site_mailbox'),
    url(r'^album_photo/(?P<photo_id>\d+)/$', "album_photo", name='oa_album_photo'),
    url(r'^album_photos/(?P<album_id>\d+)/$', "album_photos", name='oa_album_photos'),
    url(r'^album/$', "album", name='oa_site_album'),
    url(r'^teacher_starts/$', "teacher_starts", name='oa_site_teacher_starts'),
    url(r'^student_starts/$', "student_starts", name='oa_site_student_starts'),
    url(r'^regist/$', "regist", name='oa_site_regist'),
    url(r'^ajax_login/$', "ajax_login", name='oa_ajax_login'),
    url(r'^ajax_logout/$', "ajax_logout", name='oa_ajax_logout'),
)

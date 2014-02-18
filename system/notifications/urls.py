# -*- coding: utf-8 -*-

from django.conf.urls import *

urlpatterns = patterns('notifications.views',
    url(r'^$', 'all', name='all'),
    url(r'^unread/$', 'unread', name='unread'),
    url(r'^mark-all-as-read/$', 'mark_all_as_read', name='mark_all_as_read'),
    url(r'^mark-as-read/(?P<slug>\d+)/$', 'mark_as_read', name='mark_as_read'),
    url(r'^reply_notify/$', 'reply_notify', name='reply_notify'),
    url(r'^hide_notice_box/$', 'hide_notice_box', name='hide_notice_box'),
)
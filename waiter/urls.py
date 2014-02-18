# -*- coding: utf-8 -*-
from django.conf.urls import patterns,  url

urlpatterns = patterns('waiter.views.default',
    url('^index/$', 'index',name='waiter'),
    url(r'^$', 'index',name='waiter'),  
    url(r'^history/(?P<user_id>\d+)/(?P<to_user_id>\d+)/$', 'history', name='waiter_history'),
    url(r'^savemes/$', 'save_message',name="waiter_save_message"),   

    url(r'^update_unread_message/$', 'update_unread_message',name="waiter_update_unread_message"),
)

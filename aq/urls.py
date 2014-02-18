# -*- coding: utf-8 -*-
from django.conf.urls import patterns,  url

urlpatterns = patterns('aq.views.default',
    url('^index/$', 'index',name='aq'),
    url(r'^$', 'index',name='aq'),
    url(r'^track/$', 'track', name='aq_track'),
    url(r'^history/(?P<user_id>\d+)/(?P<to_user_id>\d+)/$', 'history', name='aq_history'),
    url(r'^savemes/$', 'save_message',name="aq_save_message"),
    
    url(r'^add_track/$', 'add_track',name="aq_add_track"),
    url(r'^cancle_track/$', 'cancle_track',name="aq_cancle_track"),

    url(r'^update_unread_message/$', 'update_unread_message',name="aq_update_unread_message"),
)

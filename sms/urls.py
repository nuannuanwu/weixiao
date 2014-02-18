# -*- coding: utf-8 -*-
from django.conf.urls import patterns,  url

urlpatterns = patterns('sms.views',
    url('^test/$', 'test',name='sms_test'),  
)

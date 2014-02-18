#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',)#-*- coding: utf-8 -*-


from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('kinger.apps.client.views',
    #(r'^(?P<client_id>\w+)/?$',            'client'),
    (r'^login?$',           'login'),
)# Create your views here.
